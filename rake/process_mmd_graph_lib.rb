require File.expand_path(File.dirname(__FILE__) + "/task_lib.rb")


class ProcessMmdGraphTasks < FileProcessingTasks
	def initialize(name, dir_name, options={})
		options = {
			:db_config_file => "db/config.yml",
			:paper_dir => "paper",
			:top_indegree_rank_count => 30
		}.merge(options)

		super(name, dir_name, options)
	end

	def gen_tasks
		item_graph_raw_tasks
		item_graph_categorized_tasks
		item_graph_cat_chron_tasks
		user_graph_tasks
		
		item_count_vs_user_plot_tasks

		view_count_vs_item_count_plot_tasks
		comment_count_vs_item_count_plot_tasks
		mylist_count_vs_item_count_plot_tasks
		indegree_vs_item_count_plot_tasks
		indegree_evolution_plot_tasks

		plot_tasks		
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
			run("python script/remove_forward_in_time_edges.py #{item_graph_categorized_file_name} #{item_graph_cat_chron_file_name}")
		end
	end

	no_index_file_tasks(:user_graph, Proc.new {"#{dir_name}/user_graph.json"}) do
		file user_graph_file_name => [item_graph_cat_chron_file_name] do
			run("python script/create_user_graph.py #{item_graph_cat_chron_file_name} #{user_graph_file_name}")
		end
	end

	no_index_file_tasks(:item_count_vs_user_plot, Proc.new {"#{options[:paper_dir]}/item_count_vs_user_plot.png"}) do
		file item_count_vs_user_plot_file_name => [user_graph_file_name] do
			run("python script/create_item_count_vs_user_plot.py #{user_graph_file_name} #{item_count_vs_user_plot_file_name}")
		end
	end

	no_index_file_tasks(:view_count_vs_item_count_plot, Proc.new {"#{options[:paper_dir]}/view_count_vs_item_count_plot.png"}) do
		file view_count_vs_item_count_plot_file_name => [item_graph_cat_chron_file_name] do
			run("python script/create_stat_vs_item_count_plot.py #{item_graph_cat_chron_file_name} view_count \"view count\" \"\" " +
				"#{view_count_vs_item_count_plot_file_name}")
		end
	end

	no_index_file_tasks(:comment_count_vs_item_count_plot, Proc.new {"#{options[:paper_dir]}/comment_count_vs_item_count_plot.png"}) do
		file comment_count_vs_item_count_plot_file_name => [item_graph_cat_chron_file_name] do
			run("python script/create_stat_vs_item_count_plot.py #{item_graph_cat_chron_file_name} comment_count \"comment count\" True " +
				"#{comment_count_vs_item_count_plot_file_name}")
		end
	end

	no_index_file_tasks(:mylist_count_vs_item_count_plot, Proc.new {"#{options[:paper_dir]}/mylist_count_vs_item_count_plot.png"}) do
		file mylist_count_vs_item_count_plot_file_name => [item_graph_cat_chron_file_name] do
			run("python script/create_stat_vs_item_count_plot.py #{item_graph_cat_chron_file_name} mylist_count \"mylist count\" True " +
				"#{mylist_count_vs_item_count_plot_file_name}")
		end
	end

	no_index_file_tasks(:indegree_vs_item_count_plot, Proc.new {"#{options[:paper_dir]}/indegree_vs_item_count_plot.png"}) do
		file indegree_vs_item_count_plot_file_name => [item_graph_cat_chron_file_name] do
			run("python script/create_indegree_vs_item_count_plot.py #{item_graph_cat_chron_file_name} #{indegree_vs_item_count_plot_file_name}")
		end
	end	

	def plot_tasks
		namespace name do
			task :plot => [:item_count_vs_user_plot,
				:view_count_vs_item_count_plot,
				:comment_count_vs_item_count_plot,
				:mylist_count_vs_item_count_plot,
				:indegree_vs_item_count_plot]
			task :plot_clean => [:item_count_vs_user_plot_clean,
				:view_count_vs_item_count_plot_clean,
				:comment_count_vs_item_count_plot_clean,
				:mylist_count_vs_item_count_plot_clean,
				:indegree_vs_item_count_plot_clean]
		end
	end

	def_index :top_indegree_rank do
		options[:top_indegree_rank_count]
	end

	one_index_file_tasks(:indegree_evolution_plot, :top_indegree_rank, Proc.new { |rank|
		"#{options[:paper_dir]}/indegree_evolution/#{sprintf("%04d", rank+1)}.png"
	}) do |rank|
		indegree_evolution_plot_file = indegree_evolution_plot_file_name(rank)
		file indegree_evolution_plot_file => [item_graph_cat_chron_file_name] do
			FileUtils.mkdir_p("#{options[:paper_dir]}/indegree_evolution")
			run("python script/create_indegree_evolution_plot.py #{item_graph_cat_chron_file_name} #{options[:top_indegree_rank_count]} \"#{options[:paper_dir]}/indegree_evolution/\"")
		end
	end
end
