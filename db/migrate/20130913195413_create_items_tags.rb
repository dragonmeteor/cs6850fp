class CreateItemsTags < ActiveRecord::Migration
  def up
  	create_table :items_tags , :id => false do |t|
  		t.integer :item_id, :null => false
  		t.integer :tag_id, :null => false
  	end
  	add_index :items_tags, [:item_id, :tag_id], :unique => true
  end

  def down
  	remove_index :items_tags, :column => [:item_id, :tag_id]
  	drop_table :items_tags  	
  end
end
