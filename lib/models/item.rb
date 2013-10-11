require 'yaml'
require 'active_record'
require 'mechanize'

class Item < ActiveRecord::Base
	belongs_to :user
	has_and_belongs_to_many :tags
	validates_uniqueness_of :nicoid

	has_many :parent_references, :foreign_key => "from_id", :class_name => "Reference"
	has_many :parents, :through => :parent_references

	has_many :child_references, :foreign_key => "to_id", :class_name => "Reference"
	has_many :children, :through => :child_references

	def item_type
		if nicoid.index("sm") == 0 || nicoid.index("nm") == 0 || nicoid.index("so") == 0
			:movie
		elsif nicoid.index("im") == 0
			:image
		end
	end

	def info_url
		case item_type
		when :movie
			"http://ext.nicovideo.jp/api/getthumbinfo/#{nicoid}"
		when :image
			"http://seiga.nicovideo.jp/api/illust/info?id=#{nicoid}"
		end		
	end

	def content_tree_url
		"http://commons.nicovideo.jp/tree/#{nicoid}"
	end

	def fetch_info
		case item_type 
		when :movie
			fetch_movie_info
		when :image
			fetch_image_info
		end			
	end	

	def fetch_movie_info				
		page = get_page(info_url)
		if page.nil?
			return
		end		
		response = page.search('nicovideo_thumb_response')[0]
		if response['status'] != 'ok'
			return
		end

		puts "======================================="				
		self.uploaded_at = DateTime.parse(response.search("first_retrieve")[0].inner_text)
		self.title = response.search("title")[0].inner_text
		self.view_count = response.search("view_counter")[0].inner_text.to_i		
		self.comment_count = response.search("comment_num")[0].inner_text.to_i
		self.mylist_count = response.search("mylist_counter")[0].inner_text.to_i
		if !response.search("user_id")[0].nil?
			self.user = User.where(:nicoid => response.search("user_id")[0].inner_text).first_or_create
		end
		

		puts "Video ID: " + response.search("video_id")[0].inner_text		
		puts "Title: " + title
		puts "Uploaded at: " + uploaded_at.to_s
		puts "Views: #{view_count}" 
		puts "Comments: #{comment_count}"
		puts "My Lists: #{mylist_count}" 
		if !response.search("user_id")[0].nil?
			puts "User ID: #{user.nicoid}"
		end
		puts

		mmd_strings = ["mikumikudance", "mmd"]
		puts "Tags:"
		count = 1
		tags_elem = response.search("tags[@domain='jp']")
		tags_elem.search('tag').each do |tag_elem|
			puts "[#{sprintf("%02d", count)}] " + tag_elem.inner_text
			count += 1
			tag = Tag.where(:text => tag_elem.inner_text).first_or_create
			if !tags.include?(tag)
				self.tags << tag
			end
			mmd_strings.each do |s|
				if tag.text.downcase.include?(s)
					self.is_mmd = true
				end				
			end			
		end

		puts "Is MMD?: #{if self.is_mmd then "Yes" else "No" end}"		
		puts "======================================="
		puts			
		save
	end

	def get_page(url)
		puts "Fetching #{url} ... "
		agent = Mechanize.new		
		while true
			begin
				page = agent.get(url)
				break
			rescue Mechanize::ResponseCodeError => e
				if e.to_s.index("404") == 0
					"Result: 404"
					puts
					return
				else
					"Result: other error, retrying ... "
					sleep(5)				
				end
			end
		end
		puts "Result: success"
		puts
		page
	end

	def fetch_image_info				
		page = get_page(info_url)
		if page.nil?
			return
		end
		response = page.search('response')
		if response.nil?
			return
		end

		puts "======================================="		
		self.uploaded_at = DateTime.parse(response.search("created")[0].inner_text)
		self.title = response.search("title")[0].inner_text
		self.view_count = response.search("view_count")[0].inner_text.to_i		
		self.comment_count = response.search("comment_count")[0].inner_text.to_i
		self.mylist_count = response.search("clip_count")[0].inner_text.to_i
		self.user = User.where(:nicoid => response.search("user_id")[0].inner_text).first_or_create		

		puts "Image ID: " + response.search("id")[0].inner_text		
		puts "Title: " + title
		puts "Uploaded at: " + uploaded_at.to_s
		puts "Views: #{view_count}" 
		puts "Comments: #{comment_count}"
		puts "My Lists: #{mylist_count}" 
		puts "User ID: #{user.nicoid}"
		puts

		puts "Tags:"
		page = get_page("http://seiga.nicovideo.jp/seiga/#{nicoid}")
		if !page.nil?
			tag_box = page.search("div[@class='lg_box_tag']")
			mmd_strings = ["mikumikudance", "mmd"]		
			count = 1		
			tag_box.search("a[@class='tag']").each do |tag_elem|
				puts "[#{sprintf("%02d", count)}] " + tag_elem.inner_text
				count += 1
				tag = Tag.where(:text => tag_elem.inner_text).first_or_create
				if !tags.include?(tag)
					self.tags << tag
				end
				mmd_strings.each do |s|
					if tag.text.downcase.include?(s)
						self.is_mmd = true
					end				
				end			
			end			
		end
				
		puts "Is MMD?: #{if self.is_mmd then "Yes" else "No" end}"		
		puts "======================================="
		puts			
		save
	end

	def content_tree_url
		"http://commons.nicovideo.jp/tree/#{nicoid}"
	end

	def process_items_in_box_node(box_node)	
		if box_node.nil?
			puts "  None"
		else
			count = 1
			box_node.search("li[@class='item2']").each do |item|	
				a_elem = item.search("a[@class='title_link']")[0]
				movie_number = a_elem['href'].split('/')[-1]
				puts "[#{count}] " + a_elem.inner_text + " (#{movie_number})"	
				count += 1
				yield movie_number
			end
		end	
	end

	def fetch_or_batch_create_items(nico_ids)		
		existing_ids = Item.where(:nicoid => nico_ids).map {|x| x.nicoid}		
		to_insert_ids = nico_ids - existing_ids		
		if to_insert_ids.length > 0
			Item.transaction do 
				Item.create(to_insert_ids.map {|x| {:nicoid => x}})
			end
		end		
		result = Item.where(:nicoid => nico_ids).to_a		
		result
	end

=begin
	def clean_duplicate_links(link_kind)
		existing_parent_links = Reference.where(:to_id => self.id, :kind => link_kind).to_a.sort{|x,y| x.from_id - y.from_id}
		current = nil
		Reference.transaction
			existing_parent_links.each do |link|
				if current.nil? or current.
			end
		end
	end
=end

	def fetch_content_tree_info
		tree_url = content_tree_url
		page = get_page(tree_url)
		if page.nil?
			return
		end

		puts "======================================="
		puts "Fetching content tree data of #{nicoid}"
		puts

		puts "Parent:"
		parent_box = page.search("//div[@id='ParentBox']")[0]
		parent_nico_ids = []
		process_items_in_box_node(parent_box) do |parent_nico_id|
			parent_nico_ids << parent_nico_id			
		end

		parents = fetch_or_batch_create_items(parent_nico_ids)		
		existing_link_parents = Reference.where(:from_id => self.id, :kind => "ct").to_a.map {|x| x.parent_item}
		new_link_parents = parents - existing_link_parents
		if new_link_parents.length > 0
			Reference.transaction do 
				Reference.create(new_link_parents.map{|x| {:from_id => self.id, :to_id => x.id, :kind => "ct"}})
			end
		end

		puts

		puts "Children:"
		child_box = page.search("//div[@id='ChildBox']")[0]
		child_nico_ids = []
		process_items_in_box_node(child_box) do |child_nico_id|
			child_nico_ids << child_nico_id
		end

		children = fetch_or_batch_create_items(child_nico_ids)	
		existing_link_children = Reference.where(:to_id => self.id, :kind => "ct").to_a.map {|x| x.child_item}
		new_link_children = children - existing_link_children		
		if new_link_children.length > 0
			Reference.transaction do 
				Reference.create(new_link_children.map{|x| {:from_id => x.id, :to_id => self.id, :kind => "ct"}})
			end
		end

		puts "======================================="
		puts

		self.content_tree_explored = true
		save
	end

	def fetch_description_info		
		case item_type
		when :movie
			fetch_movie_description_info
		when :image
			fetch_image_description_info
		end				
	end

	def fetch_movie_description_info
		page = get_page(info_url)
		if page.nil?
			self.description_explored = true
			self.save		
			return
		end				
		response = page.search('nicovideo_thumb_response')[0]
		if response['status'] != 'ok'
			self.description_explored = true
			self.save		
			return		
		end
		follow_item_links_in_response(response)
	end

	def fetch_image_description_info
		page = get_page(info_url)		
		if page.nil?
			self.description_explored = true
			self.save
			return
		end
		response = page.search('response')
		if response.nil?
			self.description_explored = true
			self.save
			return
		end

		follow_item_links_in_response(response)
	end

	def follow_item_links_in_response(response)
		puts "======================================="
		puts "ID: #{nicoid}"	
		puts "Description:"
		description = response.search('description')[0].inner_text
		puts description
		matches = description.scan(/[^A-Za-z]((sm|nm|im|nc|so)\d{1,12})/)
		count = 1
		puts
		puts "Links"
		parent_nico_ids = []
		matches.each do |x|			
			puts "[#{count}] #{x[0]}"
			parent_nico_ids << x[0]
			count += 1			
		end

		parents = fetch_or_batch_create_items(parent_nico_ids)				
		existing_link_parents = Reference.where(:from_id => self.id, :kind => "text").to_a.map {|x| x.parent_item}
		new_link_parents = parents - existing_link_parents		

		if new_link_parents.length > 0
			Reference.transaction do 
				Reference.create(new_link_parents.map{|x| {:from_id => self.id, :to_id => x.id, :kind => "text"}})
			end
		end
		puts "======================================="
		puts
		self.description_explored = true
		save
	end
end