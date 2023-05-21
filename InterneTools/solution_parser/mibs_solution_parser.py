import argparse
import json
import variables_parser  # can decide the level of a variable

arg_parser = argparse.ArgumentParser(
    description="Parses the log files and extracts with the help of the variables parser the lower level and upper level variable names. Returns a result file.")
arg_parser.add_argument('--logfile', action='store',
                        help='Thelog file to parse', required=True)
arg_parser.add_argument('--mpsfile', action='store',
                        help='The mps file to parse', required=True)
arg_parser.add_argument('--auxfile', action='store',
                        help='the aux file belonging to the instance', required=True)
arg_parser.add_argument('--output_path', action='store',
                        help='the output path for the *.filmosi.res', required=True)
args = arg_parser.parse_args()


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
    False

class Solution_Parser():

    instance_name = ""
    time = -1
    cpu_time = -1
    root_time = -1
    feasible = -100

    solver = ""
    solver_status = None
    objective_value = None

    tree_depth = 0
    processed_nodes = 0
    partially_processed_nodes = 0
    not_processed_nodes = 0
    branched_nodes = 0
    pruned_nodes = 0

    upper_variables = {}
    lower_variables = {}
    variables = {}

    def __init__(self):
        return

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

    def assemble_result(self):
        if len(self.variables) > 0:
            metadata = variables_parser.get_metadata(
                args.mpsfile, args.auxfile)
            #upper_variables_names = metadata['leader_variables']
            lower_variables_names = metadata['follower_variables']

            for variable in self.variables.keys():
                if variable in lower_variables_names:
                    self.lower_variables[variable] = self.variables[variable]
                else:
                    self.upper_variables[variable] = self.variables[variable]
                    #raise Exception("Variable not found in original instance", variable);
                    # -> the variable has to be an upper level variable OR it is really not in the instance (I do not assume this case here).
                    # I do not need to process the bound this way

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


def write_result_json(path: str, result_dictionary: dict):
    name_of_file = path+".json"
    json_file = open(name_of_file, "w")
    json.dump(result_dictionary, json_file, indent=4)
    json_file.close()


def open_input_file(filename):
    return open(filename, 'r')


with open_input_file(args.logfile) as logfile:

    sol_parser = Solution_Parser()
    filename_without_extension = args.logfile[:-len(".mibs.log")]
    array = filename_without_extension.split("/")
    sol_parser.instance_name = array[len(array)-1]
    sol_parser.solver = "MibS"

    for line in logfile.readlines():
        if sol_parser.feasible == -100:  # computation stuff, feasible=default value
            if line.startswith("Alps0208I Search completed."):
                sol_parser.solver_status = "solved to optimality"
                sol_parser.feasible = 1
            elif line.startswith("Alps0230I Reached time limit."):
                sol_parser.solver_status = "not solved to optimality"
                sol_parser.feasible = 0
            elif line.startswith("Alps0202I Problem is infeasible."):
                sol_parser.feasible = -1
        else:  # start to parse the other result lines
            if line == "\n" or non_relevant(line):
                continue
            elif line.startswith("Alps0265I Number of nodes fully processed") or line.startswith("Alps0264I Number of nodes processed"):
                sol_parser.process_processed_nodes_line(line)
            elif line.startswith("Alps0266I Number of nodes partially processed"):
                sol_parser.process_partially_processed_nodes_line(line)
            elif line.startswith("Alps0267I Number of nodes branched"):
                sol_parser.process_branched_nodes_line(line)
            elif line.startswith("Alps0268I Number of nodes pruned before processing"):
                sol_parser.process_pruned_nodes_line(line)
            elif line.startswith("Alps0270I Number of nodes left"):
                sol_parser.process_not_processed_nodes_line(line)
            elif line.startswith("Alps0272I Tree depth"):
                sol_parser.process_tree_depth(line)
            elif line.startswith("Alps0274I Search CPU time:"):
                sol_parser.process_cpu_time_line(line)
            elif line.startswith("Alps0278I Search wall-clock time"):
                sol_parser.process_wall_clock_time_line(line)
            elif line.startswith("Cost"):
                sol_parser.process_cost_line(line)
            # no further results regarding variables
            elif line.startswith("Number of problems"):
                break
            elif not sol_parser.objective_value is None:
                sol_parser.process_solution_line(line)

result = sol_parser.assemble_result()
write_result_json(args.output_path, result)
