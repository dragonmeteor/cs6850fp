# encoding: UTF-8
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended to check this file into your version control system.

ActiveRecord::Schema.define(:version => 20130913200058) do

  create_table "items", :force => true do |t|
    t.string   "nicoid"
    t.string   "title"
    t.integer  "user_id"
    t.integer  "view_count"
    t.integer  "comment_count"
    t.integer  "mylist_count"
    t.datetime "uploaded_at"
    t.boolean  "is_mmd"
    t.boolean  "content_tree_explored", :default => false
    t.boolean  "description_explored",  :default => false
    t.datetime "created_at",                               :null => false
    t.datetime "updated_at",                               :null => false
  end

  create_table "items_tags", :id => false, :force => true do |t|
    t.integer "item_id", :null => false
    t.integer "tag_id",  :null => false
  end

  add_index "items_tags", ["item_id", "tag_id"], :name => "index_items_tags_on_item_id_and_tag_id", :unique => true

  create_table "references", :force => true do |t|
    t.integer "from_id"
    t.integer "to_id"
    t.string  "kind"
  end

  create_table "tags", :force => true do |t|
    t.string "text"
  end

  create_table "users", :force => true do |t|
    t.string   "nicoid"
    t.string   "name"
    t.datetime "created_at", :null => false
    t.datetime "updated_at", :null => false
  end

end
