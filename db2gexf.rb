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

THRESHOLD = 3000

builder = Nokogiri::XML::Builder.new do |xml|
	xml.gexf(:xmlns => "http://www.gexf.net/1.2draft", :version => "1.2")  {		
		xml.graph(:mode => "static", :defaultedgetype => "directed") {			
			node_list = []
			xml.nodes {
				count = Item.count
				current = 0							
				Item.all.each do |item|
					if !item.view_count.nil? && item.view_count >= THRESHOLD
						xml.node(:id => item.id, :label => item.nicoid)
						node_list << item.id
					end
					current += 1
					if current % 100 == 0
						puts "Processed #{current} nodes out of #{count} ..."
					end					
				end
			}
			node_set = Set.new(node_list)
			xml.edges {
				count = Reference.count
				current = 0
				Reference.all.each do |link|
					if (node_set.include?(link.from_id) && node_set.include?(link.to_id))
						xml.edge(:id => link.id, :source=>link.from_id, :target=>link.to_id)
					end					
					current += 1
					if current % 100 == 0
						puts "Created #{current} edges out of #{count} ..."
					end					
				end
			}
		}
	}
end

File.open(ARGV[1], "w") do |f|
	f.write(builder.to_xml)
end