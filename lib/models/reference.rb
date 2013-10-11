require 'active_record'

class Reference < ActiveRecord::Base
	belongs_to :child_item, :foreign_key => :from_id, :class_name => "Item"
	belongs_to :parent_item, :foreign_key => :to_id, :class_name => "Item"
end