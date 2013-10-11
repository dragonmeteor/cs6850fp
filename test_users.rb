require 'rubygems'
require 'active_record'
require 'sqlite3'
require File.expand_path(File.dirname(__FILE__) + "/lib/models/models.rb")


ActiveRecord::Base.configurations = YAML::load(IO.read('db/config.yml'))
ActiveRecord::Base.establish_connection("development")

#user = User.create(:nico_id => '56032', :name => 'マシシ')

puts User.first.name