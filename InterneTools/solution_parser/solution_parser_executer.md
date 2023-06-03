# Usage:

Example: python3 run_parser_executer_for_all_instances_in_collection_server.py --collection /home/.../collection/ --logfile_dir ./test --store_dir test_out --solver filmosi

Example_2: python3 run_parser_executer_for_all_instances_in_collection_server.py --collection /home/.../collection/ --logfile_dir ./test --store_dir test_out --solver mibs --index_based

--index_based is optional. Use it when the MibS-Output is index-based and not name based 


# Output format: filmosi

json with following data:

soldata = {
            'instance_name': self.instance_name,			->name of instance
            'solver':self.solver,					->"(Fischetti, Ljubic, Monaci, Sinnl)-Solver"
            'solver_status':self.solver_status,				->"ERROR: solution not bilevel feasible" || "not solved to optimality" || "solved to optimality"||None
            'objective_value': self.objective_value,			->objective value of solved instance
            'best_dual_bound': self.best_dual_bound,			->dual bound value of solved instance
            'input_file':self.input_file,				->mps.gz-File
            'root_bound':self.root_bound,				->root bound value
            'time':self.time,						->wall_clock time (i guess) [sec]
            'root_time':self.root_time,					->time needed for finishing root relaxation [sec]
            'feasible':self.feasible,					->1=solved to optimality || 0=not solved to optimality due to an error or timelimit || -1=infeasible
            'nodes':self.nodes,						->number of search tree nodes needed
            'root_gap_percentage':self.root_gap_percentage,		->root bound in percent
            'best_dual_bound_percentage':self.final_gap_percentage,	->dual bound in percent
            'setting':self.setting,					->setting of filmosi-solver
            'leader_variables': self.upper_variables,			->leader variables and their values as dictionary
            'follower_variables': self.lower_variables,			->follower variables and their values as dictionary
        }

#Output format: mibs

json with following data

soldata = {
            'instance_name': self.instance_name,			->name of instance
            'solver':self.solver,					->"MibS"
            'solver_status':self.solver_status,				->"ERROR: solution not bilevel feasible" || "not solved to optimality" || "solved to optimality"||None
            'objective_value': self.objective_value,			->objective value of solved instance
            'input_file':self.input_file,				->mps-gz-File
            'time':self.time,						->wall clock time [sec]
            'cpu_time':self.cpu_time,						->cpu time [sec]
            'tree_depth':self.tree_depth,					->depth of search tree
            'processed_nodes':self.processed_nodes,						->number of processed search tree nodes
            'partially_processed_nodes':self.partially_processed_nodes,						->number of partially processed search tree nodes
            'not_processed_nodes':self.not_processed_nodes,						->number of search tree nodes that are not processed
            'branched_nodes':self.branched_nodes,						->number of branched search tree nodes
            'pruned_nodes':self.pruned_nodes,						->number of pruned search tree nodes
            'feasible':self.feasible,					->1=solved to optimality || 0=not solved to optimality due to an error or timelimit || -1=infeasible
            'leader_variables': self.upper_variables,			->leader variables and their values as dictionary
            'follower_variables': self.lower_variables,			->follower variables and their values as dictionary
        }