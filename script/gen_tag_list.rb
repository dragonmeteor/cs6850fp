require 'rubygems'
require 'active_record'
require 'mechanize'
require 'sqlite3'
require 'nokogiri'
require File.expand_path(File.dirname(__FILE__) + "/../lib/models/models.rb")

if ARGV.length < 2
	puts "Usage: ruby gen_tag_list.rb <db-config-file> <output-file>"
	exit
end

ActiveRecord::Base.configurations = YAML::load(IO.read(ARGV[0]))
ActiveRecord::Base.establish_connection("development")

#mmd_tags = []
mmd_tag_set = Set.new([])
Tag.all.each do |tag|
	#if tag.text.downcase.include?("mmd") || tag.text.downcase.include?("mikumikudance")
	#if !mmd_tag_set.include?(tag.text.downcase)
	#mmd_tags << tag.text.downcase
	if tag.text.include?("オススメ") || tag.text.include?("勧め") || tag.text.include?("紹介")
		mmd_tag_set.add(tag.text.downcase)
	end
	#end
	#end
end

File.open(ARGV[1], "w") do |f|	
	mmd_tag_set.each do |tag|		
		f.write("\"#{tag}\",\n")		
	end	
end