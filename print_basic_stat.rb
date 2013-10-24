require 'rubygems'
require 'active_record'
require 'mechanize'
require 'sqlite3'
require 'nokogiri'
require File.expand_path(File.dirname(__FILE__) + "/lib/models/models.rb")

if ARGV.count < 1
	puts "Usage: ruby print_basic_stat <config-file-name>"
	exit
end

ActiveRecord::Base.configurations = YAML::load(IO.read(ARGV[0]))
ActiveRecord::Base.establish_connection("development")

puts "item count = #{Item.count}"
puts "mmd item count = #{Item.where(:is_mmd => true).count}"
puts "user count = #{User.count}"
puts "link count = #{Reference.count}"