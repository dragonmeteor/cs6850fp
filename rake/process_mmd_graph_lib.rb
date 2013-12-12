require File.expand_path(File.dirname(__FILE__) + "/task_lib.rb")


class ProcessMmdGraphTasks < FileProcessingTasks
	def initialize(name, dir_name, options={})
		options = {
			:db_config_file => "db/config.yml",
			:paper_dir => "paper",
			:top_indegree_rank_count => 30,
			:top_cascade_count => 200,

			:user_item_exponent => -1.6,
			:max_user_item_count => 300,
			:category_prob => {
				"cg" => 220000.0/240000, 
				"model" => 14000.0/240000, 
				"motion" => 3000.0/240000, 
				"tool" => 2000.0/240000, 
				"editing" => 1000.0/240000},
			:misidenfication_prob => {
				"model" => 0.5,
				"motion" => 0.5,
				"tool" => 0.5,
				"editing" => 0.5
			},
			:self_citation_prob =>  53647.0 / 414154,
			:not_cite_prob => 350000.0 / 600000.0,
			:num_items => 240000,
			:num_users => 20000,
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

		cascade_count_tasks
		cascade_size_distribution_plot_tasks
		cascade_dot_tasks
		cascade_graph_tasks
		cascade_graph_html_tasks

		plot_tasks		

		model_spec_tasks
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

	def yes_no_text(yes_no_index)
		if yes_no_index == 0
			"no"
		else
			"yes"
		end
	end

	one_index_file_tasks(:cascade_count, :yes_no, Proc.new { |yes_no_index|
		if yes_no_index == 0
			"#{dir_name}/cascade_count_no_self_links.txt"
		else
			"#{dir_name}/cascade_count_with_self_links.txt"
		end
	}) do |yes_no_index|
		cascade_count_file = cascade_count_file_name(yes_no_index)
		cascade_size_distribution_plot_file = cascade_size_distribution_plot_file_name(yes_no_index)
		file cascade_count_file => [item_graph_cat_chron_file_name] do
			run("python script/count_cascade_patterns.py #{item_graph_cat_chron_file_name} #{yes_no_text(yes_no_index)} #{cascade_count_file} #{cascade_size_distribution_plot_file}")			
		end
	end

	one_index_file_tasks(:cascade_size_distribution_plot, :yes_no, Proc.new { |yes_no_index|
		if yes_no_index == 0
			"#{options[:paper_dir]}/cascade_size_distribution_no_self_links.png"
		else
			"#{options[:paper_dir]}/cascade_size_distribution_with_self_links.png"
		end
	}) do |yes_no_index|
		cascade_count_file = cascade_count_file_name(yes_no_index)
		cascade_size_distribution_plot_file = cascade_size_distribution_plot_file_name(yes_no_index)
		file cascade_size_distribution_plot_file => [item_graph_cat_chron_file_name] do
			run("python script/count_cascade_patterns.py #{item_graph_cat_chron_file_name} #{yes_no_text(yes_no_index)} #{cascade_count_file} #{cascade_size_distribution_plot_file}")			
		end
	end

	def_index :top_cascade do
		options[:top_cascade_count]
	end

	def_index :yes_no do
		2
	end	

	def cascade_dir_name(yes_no_index)
		if yes_no_index == 0
			"#{dir_name}/cascades_no_self_links"
		else
			"#{dir_name}/cascades_with_self_links"
		end
	end

	two_indices_file_tasks(:cascade_dot, :top_cascade, :yes_no, Proc.new {|rank, yes_no_index| 
		"#{cascade_dir_name(yes_no_index)}/#{sprintf("%04d", rank+1)}.gv"
	}) do |rank, yes_no_index|
		cascade_dot_file = cascade_dot_file_name(rank, yes_no_index)
		cascade_dir = cascade_dir_name(yes_no_index)
		cascade_count_file = cascade_count_file_name(yes_no_index)
		file cascade_dot_file => [cascade_count_file] do
			if !File.exists?(cascade_dir)
				FileUtils.mkdir_p(cascade_dir)
			end
			run("python script/create_dot_files.py #{item_graph_cat_chron_file_name} #{cascade_count_file} #{top_cascade_count} #{yes_no_text(yes_no_index)}  \"#{cascade_dir}/\"")
		end
	end

	def dot_command
		"\"C:\\Program Files (x86)\\Graphviz2.34\\bin\\dot.exe\""
	end

	def cascade_graph_dir_name(yes_no_index)
		if yes_no_index == 0
			"#{options[:paper_dir]}/cascades_no_self_links"			
		else
			"#{options[:paper_dir]}/cascades_with_self_links"
		end
	end

	two_indices_file_tasks(:cascade_graph, :top_cascade, :yes_no, Proc.new {|rank, yes_no_index| 
		"#{cascade_graph_dir_name(yes_no_index)}/#{sprintf("%04d", rank+1)}.png"
	}) do |rank, yes_no_index|
		cascade_graph_file = cascade_graph_file_name(rank, yes_no_index)
		cascade_dot_file = cascade_dot_file_name(rank, yes_no_index)
		cascade_graph_dir = cascade_graph_dir_name(yes_no_index)
		file cascade_graph_file => [cascade_dot_file] do
			if !File.exists?(cascade_graph_dir)
				FileUtils.mkdir_p(cascade_graph_dir)
			end
			run("#{dot_command} -Tpng #{cascade_dot_file} -o #{cascade_graph_file}")
		end
	end

	one_index_file_tasks(:cascade_graph_html, :yes_no, Proc.new { |yes_no_index|
		"#{cascade_graph_dir_name(yes_no_index)}/index.html" 
	}) do |yes_no_index|
		cascade_graph_html_file = cascade_graph_html_file_name(yes_no_index)
		cascade_count_file = cascade_count_file_name(yes_no_index)
		file cascade_graph_html_file => [cascade_count_file] do
			cascades = []
			File.readlines(cascade_count_file).each do |line|				
				if line.strip.length > 0
					cascades << line.split[2].to_i				
				end
			end

HTML_TEMPLATE = <<-TEMPLATE
<html>
	<head>
		<title>Cascade Frequencies in MikuMikuDance Item Network</title>
	</head>
	<body>
		<h1>Cascade Frequencies in MikuMikuDance Item Network</h1>
		<p>Red = CG production, Green = Modeling, Blue = Choreography, Orange = Tool Making, Magenta = Summarizing</p>
		<table border="1">
			<tr>
				<% options[:top_cascade_count].times do |rank| %>
					<td align="center">						
						<img src="<%= sprintf("%04d", rank+1) %>.png" /><br/>
						Rank: <%= rank+1 %><br/>
						Count: <%= cascades[rank] %>
					</td>
					<% if (rank+1)%5 == 0 %>
						</tr>
						<% if rank+1 < options[:top_cascade_count] %>
							<tr>
						<% end %>
					<% end %>								
				<% end %>
			<% if options[:top_cascade_count] % 5 != 0 %>
				</tr>
			<% end %>			
		</table>
	</body>
</html>
TEMPLATE

			template = ERB.new(HTML_TEMPLATE)
			content = template.result(binding)     	

			fout = File.open(cascade_graph_html_file, "wt")    	
			fout.write(content)
			fout.close			
		end
	end

	no_index_file_tasks(:model_spec, Proc.new { "#{dir_name}/model_spec.txt"}) do 
		file model_spec_file_name do
			File.open(model_spec_file_name, "w") do |f|
				f.write("#{options[:num_items]}\n")
				f.write("#{options[:num_users]}\n")
				f.write("#{options[:user_item_exponent]}\n")
				f.write("#{options[:max_user_item_count]}\n")
				f.write("#{options[:self_citation_prob]}\n")
				f.write("#{options[:not_cite_prob]}\n")
				f.write("#{options[:category_prob]["cg"]}\n")
				f.write("#{options[:category_prob]["model"]}\n")
				f.write("#{options[:category_prob]["motion"]}\n")
				f.write("#{options[:category_prob]["tool"]}\n")
				f.write("#{options[:category_prob]["editing"]}\n")
				f.write("#{options[:misidenfication_prob]["model"]}\n")
				f.write("#{options[:misidenfication_prob]["motion"]}\n")
				f.write("#{options[:misidenfication_prob]["tool"]}\n")
				f.write("#{options[:misidenfication_prob]["editing"]}\n")
			end
		end
	end

end
