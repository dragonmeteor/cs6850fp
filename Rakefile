require 'standalone_migrations'
StandaloneMigrations::Tasks.load_tasks
require File.expand_path(File.dirname(__FILE__) + "/rake/process_mmd_graph_lib.rb")


task :default => []

namespace :db do
	task :seed do
		require 'rubygems'
		require 'active_record'
		require 'sqlite3'
		require File.expand_path(File.dirname(__FILE__) + "/lib/models/models.rb")

		ActiveRecord::Base.configurations = YAML::load(IO.read('db/config.yml'))
		ActiveRecord::Base.establish_connection("development")

		Item.transaction do
			Item.new(:nicoid => 'sm21572837').save!
			Item.new(:nicoid => 'sm8695572').save!
			Item.new(:nicoid => 'sm1072801').save!			
			Item.new(:nicoid => 'im2533092').save!
			Item.new(:nicoid => 'im2997757').save!
		end
	end

	task :reset_and_seed do
		Rake::Task["db:reset"].invoke
		Rake::Task["db:seed"].invoke
	end
end

ProcessMmdGraphTasks.new("mmd01", "data/mmd_11_12_2013",
	:db_config_file => "db/config_11_12_2013.yml")