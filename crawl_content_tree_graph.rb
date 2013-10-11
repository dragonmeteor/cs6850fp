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
		if item.title.nil?
			item.fetch_info
		end

		if item.is_mmd
			item.fetch_content_tree_info
		else
			item.content_tree_explored = true
			item.save
		end
	else
		break
	end
	sleep(1)	
end