require 'rubygems'
require 'active_record'
require 'mechanize'
require 'sqlite3'
require 'nokogiri'
require File.expand_path(File.dirname(__FILE__) + "/../lib/models/models.rb")

if ARGV.length < 2
	puts "Usage: ruby gen_tag_progress.rb <db-config-file> <output-progress-file>"
	exit
end

ActiveRecord::Base.configurations = YAML::load(IO.read(ARGV[0]))
ActiveRecord::Base.establish_connection("development")

mmd_tags = []
mmd_tag_set = Set.new([])
Tag.all.each do |tag|
	if tag.text.downcase.include?("mmd") || tag.text.downcase.include?("mikumikudance")
		if !mmd_tag_set.include?(tag.text.downcase)
			mmd_tags << tag.text.downcase
			mmd_tag_set.add(tag.text.downcase)
		end
	end
end

File.open(ARGV[1], "w") do |f|
	f.write("{\n")
	mmd_tags.each do |tag|		
		f.write("  #{tag.inspect} => {\n")
		f.write("    \"douga\" => [0,0],\n")
		f.write("    \"seiga\" => 0,\n")
		f.write("  },\n")
	end
	f.write("}\n")
end