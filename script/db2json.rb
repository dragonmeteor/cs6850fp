require 'rubygems'
require 'active_record'
require 'mechanize'
require 'sqlite3'
require 'nokogiri'
require File.expand_path(File.dirname(__FILE__) + "/../lib/models/models.rb")

if ARGV.count < 2
	puts "Usage: ruby db2json <config-file-name> <output-file-name>"
	exit
end

ActiveRecord::Base.configurations = YAML::load(IO.read(ARGV[0]))
ActiveRecord::Base.establish_connection("development")

$indent_count = 0

def indent
	$indent_count += 2
end

def outdent
	$indent_count -= 2
end

def write_indented_line(f, text)
	f.write(" "*$indent_count + text + "\n")
end

def indent_and_write(f, text)
	f.write(" "*$indent_count + text)
end

def new_line(f)
	f.write("\n")
end


File.open(ARGV[1], "w") do |f|
	write_indented_line(f, "{")
	
	indent	
	count = 0	
	mmd_set = Set.new(Item.where(:is_mmd => true).to_a.map { |item| item.id })
	total = mmd_set.count

	write_indented_line(f, "\"nodes\": {")
	indent
	item_delim = ""	
	#Item.where(:id => 31668).each do |item|
	#Item.where(:is_mmd => true).each do |item|		
	mmd_set.each do |id|
		item = Item.where(:id => id)[0]
		write_indented_line(f, item_delim)
		item_delim = ","
		write_indented_line(f, "\"#{item.id}\": {")
		indent

		write_indented_line(f, "\"nicoid\": \"#{item.nicoid}\",")
		write_indented_line(f, "\"user\": \"#{item.user_id}\",")
		write_indented_line(f, "\"view_count\": #{item.view_count},")
		write_indented_line(f, "\"comment_count\": #{item.comment_count},")
		write_indented_line(f, "\"mylist_count\": #{item.mylist_count},")
		write_indented_line(f, "\"uploaded_at\": \"#{item.uploaded_at}\",")
		
		indent_and_write(f, "\"tags\": [")		
		tag_list = item.tags.map { |tag|
			#puts (tag.text.gsub(/\\/, "\\\\\\\\").gsub("\"", "\\\""))
			'"' + (tag.text.gsub(/\\/, "\\\\\\\\").gsub("\"", "\\\"")) + '"'
		}
		f.write(tag_list.join(', '))
		f.write("]\n")		

		outdent
		write_indented_line(f, "}")

		count += 1
		if count % 1000 == 0
			puts "Written #{count} out of #{total} items."
		end		
	end
	outdent
	write_indented_line(f, "},")

	write_indented_line(f, "\"edges\": [")
	ref_delim = ""
	indent
	total = Reference.count
	count = 0
	Reference.all.each do |ref|		
		if mmd_set.include?(ref.from_id) && mmd_set.include?(ref.to_id)
			write_indented_line(f, ref_delim)		
			ref_delim = ","
			write_indented_line(f, "[\"#{ref.from_id}\",\"#{ref.to_id}\"]")
		end

		count += 1
		if count % 1000 == 0
			puts "Processed #{count} out of #{total} edges."
		end
	end
	outdent
	write_indented_line(f, "]")

	outdent
	write_indented_line(f, "}")
end