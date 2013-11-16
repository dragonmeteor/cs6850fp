require 'rubygems'
require 'active_record'
require 'mechanize'
require 'sqlite3'
require 'json'
require 'uri'
require File.expand_path(File.dirname(__FILE__) + "/lib/models/models.rb")

ActiveRecord::Base.configurations = YAML::load(IO.read('db/config.yml'))
ActiveRecord::Base.establish_connection("development")

def report_explored_items
=begin
	item_count = Item.count
	explored_count = Item.where(:content_tree_explored => true).count
	puts
	puts "Content tree explored: #{explored_count} out of #{item_count}"
	link_count = Reference.where(:kind => "ct").count
	puts "There are currently #{link_count} content tree links."	

	explored_count = Item.where(:description_explored => true).count
	puts
	puts "Description explored: #{explored_count} out of #{item_count}"
	link_count = Reference.where(:kind => "text").count
	puts "There are currently #{link_count} text links."
	puts
=end
end

def create_items(nico_ids)
	existing_ids = Item.where(:nicoid => nico_ids).map {|x| x.nicoid}
	to_insert_ids = nico_ids - existing_ids
	puts "There are #{to_insert_ids.count} new ID(s)."
	if to_insert_ids.count.times != 0
		to_insert_ids.count.times do |i|
			print "#{to_insert_ids[i]}, "
			if (i % 5 == 4)
				puts
			end
		end		
		if (to_insert_ids.count % 5 != 0)
			puts
		end
	end
	if to_insert_ids.length > 0
		Item.transaction do 
			Item.create(to_insert_ids.map {|x| {:nicoid => x}})
		end
	end
	to_insert_ids.length
end

def save_tag_progress(tag_progress)
	File.open("tag_progress.rb", "w") do |f|
		f.write("{\n")
		tag_progress.keys.each do |tag|
			f.write("  \"#{tag.gsub(/\\/, "\\\\\\\\").gsub("\"", "\\\"")}\" => {\n")
			progress = tag_progress[tag]			
			f.write("    \"douga\" => [#{progress["douga"].join(",")}],\n")			
			f.write("    \"seiga\" => #{progress["seiga"]},\n")	
			f.write("  },\n")
		end
		f.write("}\n")
	end
end

def seed_douga_by_tag(tag, tag_progress, direction)
	progress = tag_progress[tag]
	page_index = progress["douga"][direction] + 1
	if direction == 0
		url = "http://ext.nicovideo.jp/api/search/tag/#{tag}?order=a&sort=f&page=#{page_index}"
	else
		url = "http://ext.nicovideo.jp/api/search/tag/#{tag}?order=d&sort=f&page=#{page_index}"
	end
	
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
				sleep(1)
			end
		rescue Mechanize::ResponseReadError => e
			sleep(1)
		end
	end	

	if direction == 0
		puts "Douga with tag \"#{tag}\" (ascending) -- Page #{page_index}:"
	else
		puts "Douga with tag \"#{tag}\" (descending) -- Page #{page_index}:"
	end
	if page.body.strip.length == 0
		return 0
	else
		search_result = JSON.parse(page.body)	
		if search_result["list"].nil?
			return 0
		end

		nico_id_list = search_result["list"].map { |item| item["id"] }
		if nico_id_list.length == 0
			return 0
		end
		count = create_items(nico_id_list)

		tag_progress[tag]["douga"][direction] = page_index

		save_tag_progress(tag_progress)
		report_explored_items
		return 1
	end	
end

def seed_seiga_by_tag(tag, tag_progress)
	matches = tag.scan(/[^A-Za-z]((sm|nm|im|nc|so)\d{1,12})/)
	if matches.count > 0
		return 0
	end
	
	progress = tag_progress[tag]
	page_index = progress["seiga"] + 1
	if tag.include?("?") || tag.include?("%")
		return 0
	end
	url = "http://seiga.nicovideo.jp/tag/#{tag}?target=illust&sort=image_created_d&page=#{page_index}&"		
	
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
		rescue Mechanize::ResponseReadError => e
			sleep(1)
		end
	end

	puts "Seiga with tag \"#{tag}\" -- Page #{page_index}:"
	image_anchors = page.search("a[@class='center_img_inner ']")
	if image_anchors.count == 0
		return 0
	else
		nico_ids = []
		image_anchors.each do |anchor|
			nico_ids << anchor['href'].split('/')[-1].strip
		end
		if nico_ids.length == 0
			return 0
		end
		count = create_items(nico_ids)

		tag_progress[tag]["seiga"] = page_index

		save_tag_progress(tag_progress)
		report_explored_items
		return 1
	end
end

tag_progress = eval(File.open("tag_progress.rb", "r:utf-8") { |f| f.read })

tag_still_going = {}
tag_progress.keys.each do |tag|
	tag_still_going[tag] = {"douga"=>[true,true], "seiga"=>true}
end

tag_progress.keys.each do |tag|		
	while true		
		has_next_round = false

		if tag_still_going[tag]["douga"][0]
			tag_still_going[tag]["douga"][0] = (seed_douga_by_tag(tag, tag_progress,0) != 0)
			has_next_round = (has_next_round || tag_still_going[tag]["douga"][0])
		end
		sleep(1)
		if tag_still_going[tag]["douga"][1]
			tag_still_going[tag]["douga"][1] = (seed_douga_by_tag(tag, tag_progress,1) != 0)
			has_next_round = (has_next_round || tag_still_going[tag]["douga"][1])
		end
		sleep(1)
		if tag_still_going[tag]["seiga"]
			tag_still_going[tag]["seiga"] = (seed_seiga_by_tag(tag, tag_progress) != 0)
			has_next_round = (has_next_round || tag_still_going[tag]["seiga"])
		end
		sleep(1)

		if !has_next_round
			break
		end
	end
end

