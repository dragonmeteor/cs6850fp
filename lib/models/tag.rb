require 'active_record'

class Tag < ActiveRecord::Base
	has_and_belongs_to_many :items
	validates_uniqueness_of :text
end