require File.expand_path(File.dirname(__FILE__) + "/task_lib.rb")
puts File.expand_path(File.dirname(__FILE__) + "/task_lib.rb")

class ProcessMmdGraphTasks < FileProcessingTasks
	def initialize(name, dir_name, options={})
		options = {
			:db_config_file => "db/config.yml"
		}.merge(options)

		super(name, dir_name, options)
	end

	def gen_tasks
		item_graph_raw_tasks
		item_graph_categorized_tasks
		item_graph_cat_chron_tasks
	end

	no_index_file_tasks(:item_graph_raw, Proc.new { "#{dir_name}/item_graph_raw.json" }) do 
		file item_graph_raw_file_name do
			run("ruby script/db2json.rb #{options[:db_config_file]} #{item_graph_raw_file_name}")
		end
	end

	no_index_file_tasks(:item_graph_categorized, Proc.new { "#{dir_name}/item_graph_categorized.json" }) do
		file item_graph_categorized_file_name => [item_graph_raw_file_name] do
			run("python script/classify_item.py #{item_graph_raw_file_name} #{item_graph_categorized_file_name}")
		end
	end

	no_index_file_tasks(:item_graph_cat_chron, Proc.new {"#{dir_name}/item_graph_cat_chron.json"}) do
		file item_graph_cat_chron_file_name => [item_graph_categorized_file_name] do
			run("python script/remove_foward_in_time_edge.py #{item_graph_categorized_file_name} #{item_graph_cat_chron_file_name}")
		end
	end
end
