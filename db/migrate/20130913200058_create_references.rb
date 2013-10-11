class CreateReferences < ActiveRecord::Migration
  def up
  	create_table :references do |t|
  		t.integer :from_id
  		t.integer :to_id
  		t.string :kind
  	end
  end

  def down
  	drop_table :references
  end
end
