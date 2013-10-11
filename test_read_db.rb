require 'rubygems'
require 'active_record'
require 'mechanize'
require 'sqlite3'
require File.expand_path(File.dirname(__FILE__) + "/lib/models/models.rb")

ActiveRecord::Base.configurations = YAML::load(IO.read('db/config.yml'))
ActiveRecord::Base.establish_connection("development")

Item.first(10).each do |item|
	puts "======================================="			
	puts "Video ID: " + item.nicoid
	puts "Title: " + item.title
	puts "Uploaded at: " + item.uploaded_at.to_s
	puts "Views: #{item.view_count}" 
	puts "Comments: #{item.comment_count}"
	puts "My Lists: #{item.mylist_count}" 
	puts "User ID: #{item.user.nicoid}"		
	puts "Retrieved at: #{item.updated_at}"
	puts

	puts "Tags:"
	count = 1
	item.tags.each do |tag|
		puts "[#{sprintf("%02d", count)}] " + tag.text
		count += 1		
	end

	puts "======================================="
	puts			
end
