require 'rubygems'
require 'active_record'
require 'mechanize'
require 'sqlite3'
require File.expand_path(File.dirname(__FILE__) + "/lib/models/models.rb")

ActiveRecord::Base.configurations = YAML::load(IO.read('db/config.yml'))
ActiveRecord::Base.establish_connection("development")

#begin
	
#rescue
#	puts "Cannot find unexplored item!"	
#end

while true	
	item = Item.where(:content_tree_explored => false).first	
	if !item.nil?
		puts "Considering item with Nico ID: #{item.nicoid} ... "		
		if item.title.nil?
			puts "Item has no title, so fetching title info ..."
			item.fetch_info
		end

		if item.is_mmd			
			item.fetch_content_tree_info
		else
			puts "Item is not an MMD item. Skipping content tree lookup... "
			item.content_tree_explored = true
			item.save
		end
	end
	found_content_tree = !item.nil?

	item_count = Item.count
	explored_count = Item.where(:content_tree_explored => true).count
	puts
	puts "Content tree explored: #{explored_count} out of #{item_count}"
	link_count = Reference.where(:kind => "ct").count
	puts "There are currently #{link_count} content tree links."
	puts
	
	sleep(1)

	item = Item.where(:description_explored => false).first			
	if !item.nil?		
		puts "Considering item with Nico ID: #{item.nicoid} ... "
		if item.title.nil?
			puts "Item has no title, so fetching title info ..."
			item.fetch_info
		end

		if item.is_mmd			
			item.fetch_description_info
		else
			puts "Item is not an MMD item. Skipping description lookup ... "
			item.description_explored = true
			item.save
		end
	end
	found_text = !item.nil?

	item_count = Item.count
	explored_count = Item.where(:description_explored => true).count
	puts
	puts "Description explored: #{explored_count} out of #{item_count}"
	link_count = Reference.where(:kind => "text").count
	puts "There are currently #{link_count} text links."
	puts

	sleep(1)

	if !found_content_tree && !found_text
		break
	end
end