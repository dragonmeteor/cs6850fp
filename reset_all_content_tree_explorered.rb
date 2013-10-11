require 'rubygems'
require 'active_record'
require 'mechanize'
require 'sqlite3'
require File.expand_path(File.dirname(__FILE__) + "/lib/models/models.rb")


ActiveRecord::Base.configurations = YAML::load(IO.read('db/config.yml'))
ActiveRecord::Base.establish_connection("development")

#Item.update_all(:content_tree_explored => false)
Item.update_all(:description_explored => false)
#Reference.delete_all
#Reference.delete_all
#puts Reference.count
#a = Item.where(:nicoid => "sm21572837").first
#b = Item.where(:nicoid => "sm21586263").first
#links = Reference.where(:from_id => a.id, :kind => "ct")
#links.each do |link|
#	puts link.child_item.title + " -> "	 + link.parent_item.title + "(#{link.kind})"
#end
