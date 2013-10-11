class CreateItems < ActiveRecord::Migration
  def up
  	create_table :items do |t|
  		t.string :nicoid
  		t.string :title
  		t.integer :user_id
  		t.integer :view_count
  		t.integer :comment_count
  		t.integer :mylist_count
      t.datetime :uploaded_at
  		t.boolean :is_mmd
      t.boolean :content_tree_explored, :default => false
      t.boolean :description_explored, :default => false      
      t.timestamps
  	end
  end

  def down
  	drop_table :items
  end
end
