require 'active_record'

class User < ActiveRecord::Base
	has_many :items
	validates_uniqueness_of :nicoid
end