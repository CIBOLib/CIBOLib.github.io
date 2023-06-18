from os import path
from . import variables_parser
import re


def get_line_value(line):
    index = line.find(":")
    line = line[index+1:]
    line = line.strip(' ')
    array = line.split(" ")
    variable_value = array[0]
    return variable_value


def non_relevant(line):
    if line.startswith("First stage") or line.startswith("Second stage") or \
            line.startswith("Alps0260I Best solution") or line.__contains__("Best solution found:") or \
            line.startswith("Optimal solution:") or line.__contains__("====") or line.startswith("Blis"):
        return True
    return False

class Mibs_Solution_Parser():

    def __init__(self, translate_indices_to_names: bool):
        self.translate_indices_to_names = translate_indices_to_names
        self.instance_name = ""
        self.time = -1
        self.cpu_time = -1
        self.root_time = -1
        self.feasible = -100

        self.solver = "MibS"
        self.solver_status = None
        self.objective_value = None

        self.tree_depth = 0
        self.processed_nodes = 0
        self.partially_processed_nodes = 0
        self.not_processed_nodes = 0
        self.branched_nodes = 0
        self.pruned_nodes = 0

        self.upper_variables = {}
        self.lower_variables = {}
        self.variables = {}

    def process_processed_nodes_line(self, line):
        try:
            self.processed_nodes = int(get_line_value(line))
        except:
            raise Exception("unknown processed nodes")

    def process_partially_processed_nodes_line(self, line):
        try:
            self.partially_processed_nodes = int(get_line_value(line))
        except:
            raise Exception("unknown partially processed nodes")

    def process_branched_nodes_line(self, line):
        try:
            self.branched_nodes = int(get_line_value(line))
        except:
            raise Exception("unknown branched nodes")

    def process_pruned_nodes_line(self, line):
        try:
            self.pruned_nodes = int(get_line_value(line))
        except:
            raise Exception("unknown pruned nodes")

    def process_not_processed_nodes_line(self, line):
        try:
            self.not_processed_nodes = int(get_line_value(line))
        except:
            raise Exception("unknown not processed nodes")

    def process_tree_depth(self, line):
        try:
            self.tree_depth = int(get_line_value(line))
        except:
            raise Exception("unknown tree depth")

    def process_cpu_time_line(self, line):
        try:
            self.cpu_time = float(get_line_value(line))
        except:
            raise Exception("unknown cpu time")

    def process_wall_clock_time_line(self, line):
        try:
            self.time = float(get_line_value(line))
            if self.feasible >= 0:
                if self.time >= 3600 or self.feasible == 0:  # only if there are special cases, I do not know yet
                    self.solver_status = "not solved to optimality"
            return
        except:
            raise Exception("unknown wall-clock-time")

    def process_cost_line(self, line):
        line = line.strip(' ')
        array = line.split(" ")
        costs = float(array[len(array)-1])
        self.objective_value = costs

    # here i need to handle differences between name-based and index-based-> automatic recognization via x[...],y[...] could work
    def process_solution_line(self, line):
        line = line.strip(' ')
        array = line.split(" ")
        variable, variable_value = array[0], float(array[len(array)-1])
        self.variables[variable] = variable_value

    def translate_vars(self,vars_list,leader_variable=True):
        expr = re.compile("([xy])\\[([0-9]+)\\]")
        result = {}
        if leader_variable:
            variable_type="x"
        else:
            variable_type="y"
        var_index_based_names=list(self.variables.keys())#var_list ist entweder follower oder leader... hier noch unterscheiden!
        for key_index in range(len(var_index_based_names)):
            match = expr.match(var_index_based_names[key_index])
            if match:
                if match[1]==variable_type:
                    idx = int(match[2])
                    result[var_index_based_names[key_index]] = vars_list[idx]
        return result

    def assemble_result(self, mps_file, aux_file):
        if len(self.variables) > 0:
            instance_metadata = variables_parser.get_metadata(
                mps_file, aux_file)

            lower_variables_dict={}
            upper_variables_dict={}
            upper_variables_names_dict={}
            lower_variables_names_dict={}

            if self.translate_indices_to_names:#dict: index, name
                upper_variables_names_dict = self.translate_vars(
                    instance_metadata["leader_variables"])
                lower_variables_names_dict = self.translate_vars(
                    instance_metadata["follower_variables"],leader_variable=False)
            else:

                upper_variables_dict=dict.fromkeys(instance_metadata["leader_variables"],0)
                for index in range(len(upper_variables_dict)):
                    upper_variables_names_dict[instance_metadata["leader_variables"][index]]=instance_metadata["leader_variables"][index]

                lower_variables_dict=dict.fromkeys(instance_metadata["follower_variables"],0)
                for index in range(len(lower_variables_dict)):
                    lower_variables_names_dict[instance_metadata["follower_variables"][index]]=instance_metadata["follower_variables"][index]

            dict_keys_upper=set(list(self.variables.keys())).intersection(set(instance_metadata["leader_variables"]))
            dict_keys_lower=set(list(self.variables.keys())).intersection(set(instance_metadata["follower_variables"]))
            upper_keys=list(upper_variables_names_dict.keys())
            upper_values=list(upper_variables_names_dict.values())
            for index in range(len(upper_variables_names_dict)):
                if upper_keys[index] in dict_keys_upper:
                    upper_variables_dict[upper_values[index]]=self.variables[ upper_keys[index]]

            lower_keys=list(lower_variables_names_dict.keys())
            lower_values=list(lower_variables_names_dict.values())
            for index in range(len(lower_variables_names_dict)):
                if lower_keys[index] in dict_keys_lower:
                    lower_variables_dict[lower_values[index]]=self.variables[ lower_keys[index]]
                    #raise Exception("Variable not found in original instance", variable);
                    # -> the variable has to be an upper level variable OR it is really not in the instance (I do not assume this case here).
                    # I do not need to process the bounds this way

            self.upper_variables=upper_variables_dict
            self.lower_variables=lower_variables_dict



        soldata = {
            'instance_name': self.instance_name,
            'solver': self.solver,
            'solver_status': self.solver_status,
            'objective_value': self.objective_value,
            'time': self.time,
            'cpu_time': self.cpu_time,
            'tree_depth': self.tree_depth,
            'processed_nodes': self.processed_nodes,
            'partially_processed_nodes': self.partially_processed_nodes,
            'not_processed_nodes': self.not_processed_nodes,
            'branched_nodes': self.branched_nodes,
            'pruned_nodes': self.pruned_nodes,
            'feasible': self.feasible,
            'leader_variables': self.upper_variables,
            'follower_variables': self.lower_variables,
        }
        return soldata

    def run(self,  mps_file: str, aux_file: str, logfile: str) -> dict:
        self.instance_name = path.basename(logfile).removesuffix(".mibs.log")
        with open(logfile, 'r') as input_file:
            for line in input_file.readlines():
                if self.feasible == -100:  # computation stuff, feasible=default value
                    if line.startswith("Alps0208I Search completed."):
                        self.solver_status = "solved to optimality"
                        self.feasible = 1
                    elif line.startswith("Alps0230I Reached time limit."):
                        self.solver_status = "not solved to optimality"
                        self.feasible = 0
                    elif line.startswith("Alps0202I Problem is infeasible."):
                        self.feasible = -1
                else:  # start to parse the other result lines
                    if line == "\n" or non_relevant(line):
                        continue
                    elif line.startswith("Alps0265I Number of nodes fully processed") or line.startswith("Alps0264I Number of nodes processed"):
                        self.process_processed_nodes_line(line)
                    elif line.startswith("Alps0266I Number of nodes partially processed"):
                        self.process_partially_processed_nodes_line(line)
                    elif line.startswith("Alps0267I Number of nodes branched"):
                        self.process_branched_nodes_line(line)
                    elif line.startswith("Alps0268I Number of nodes pruned before processing"):
                        self.process_pruned_nodes_line(line)
                    elif line.startswith("Alps0270I Number of nodes left"):
                        self.process_not_processed_nodes_line(line)
                    elif line.startswith("Alps0272I Tree depth"):
                        self.process_tree_depth(line)
                    elif line.startswith("Alps0274I Search CPU time:"):
                        self.process_cpu_time_line(line)
                    elif line.startswith("Alps0278I Search wall-clock time"):
                        self.process_wall_clock_time_line(line)
                    elif line.startswith("Cost"):
                        self.process_cost_line(line)
                    # no further results regarding variables
                    elif line.startswith("Number of problems"):
                        break
                    elif not self.objective_value is None:
                        self.process_solution_line(line)
        return self.assemble_result(mps_file, aux_file)
