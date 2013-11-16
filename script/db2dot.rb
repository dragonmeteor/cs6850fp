require 'rubygems'
require 'active_record'
require 'mechanize'
require 'sqlite3'
require 'nokogiri'
require File.expand_path(File.dirname(__FILE__) + "/lib/models/models.rb")

if ARGV.count < 2
	puts "Usage: ruby db2gexf <config-file-name> <output-file-name>"
	exit
end

ActiveRecord::Base.configurations = YAML::load(IO.read(ARGV[0]))
ActiveRecord::Base.establish_connection("development")

#THRESHOLD = 3000

File.open(ARGV[1], "w") do |f|
	f.write("strict graph mmd {\n")
	f.write("  node [shape=point];\n")
	count = Item.count
	current = 0							

=begin	
	node_list=[]
	Item.all.each do |item|
		if !item.view_count.nil? && item.view_count >= THRESHOLD			
			node_list << item.id
		end
		current += 1
		if current % 100 == 0
			puts "Processed #{current} nodes out of #{count} ..."
		end					
	end
=end

	#node_set = Set.new(node_list)
	count = Reference.count
	current = 0
	Reference.all.each do |link|
		#if (node_set.include?(link.from_id) && node_set.include?(link.to_id))
			f.write("  n#{link.from_id} -- n#{link.to_id};\n")
		#end					
		current += 1
		if current % 100 == 0
			puts "Created #{current} edges out of #{count} ..."
		end					
	end

	f.write("}\n")
end