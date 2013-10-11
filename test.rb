require 'rubygems'
require 'mechanize'

agent = Mechanize.new

page = agent.get('http://commons.nicovideo.jp/tree/sm21231366')

# Prints the title
title = page.search("//span[@class='title']")[0].inner_text
puts title

def display_items_in_box(box_node)	
	if box_node.nil?
		puts "  None"
	else
		count = 1
		box_node.search("li[@class='item2']").each do |item|	
			a_elem = item.search("a[@class='title_link']")[0]
			movie_number = a_elem['href'].split('/')[-1]
			puts "[#{count}] " + a_elem.inner_text + " (#{movie_number})"	
			count += 1
		end
	end	
end


puts "Parents:"
parent_box = page.search("//div[@id='ParentBox']")[0]
display_items_in_box(parent_box)

puts
puts "Children:"
child_box = page.search("//div[@id='ChildBox']")[0]
display_items_in_box(child_box)