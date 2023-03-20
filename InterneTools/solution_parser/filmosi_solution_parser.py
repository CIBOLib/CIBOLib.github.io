import argparse
import json
import variables_parser #can decide the level of a variable

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


class Solution_Parser():
    instance_name="";
    solver="";
    solver_status="infeasible";
    objective_value=None;
    best_dual_bound=None;
    final_gap_percentage=-1;
    upper_variables={};
    lower_variables={};
    variables={};
    feasible=-1

    def __init__(self):
        return

    def process_stat_line(self, line):
        # STAT[0]; input_file[1] ; zbest[2] ; final_bound[3] ; root_bound[4] ; time (s.)[5] ; root_time (s.)[6] ; opt[7] ; nodes[8] ; %root_gap[9] ; %final_gap[10] ; setting[11]
        line=line.replace(" ","")
        data=line.split(";")

        self.feasible=int(data[7])
        if self.feasible>=0:
            self.objective_value=float(data[2])
            self.best_dual_bound=float(data[3])
            self.final_gap_percentage=float(data[10])
            time=float(data[5])
            if time>=3600 or self.feasible==0: #or only if there are special cases, I do not know yet
                self.solver_status="not solved to optimality"
            else:
                self.solver_status="solved to optimality"
        return

    def process_solution_line(self, line):
        line=line.strip(' ')
        array=line.split(" ")
        variable, variable_value=array[0],float(array[len(array)-1])
        self.variables[variable]=variable_value

    def assemble_result(self):

        metadata=variables_parser.get_metadata(args.mpsfile, args.auxfile)
        upper_variables_names=metadata['leader_variables']
        lower_variables_names=metadata['follower_variables']

        for variable in self.variables.keys():
            if variable in upper_variables_names:
                self.upper_variables[variable]=self.variables[variable]
            elif variable in lower_variables_names:
                self.lower_variables[variable]=self.variables[variable]
            else:
                raise Exception("Variable not found in original instance", variable);


        soldata = {
            'instance_name': self.instance_name,
            'solver':self.solver,
            'solver_status':self.solver_status,
            'objective_value': self.objective_value,
            'best_dual_bound': self.best_dual_bound,
            'leader_variables': self.upper_variables,
            'follower_variables': self.lower_variables,
        }
        return soldata

def write_result_json(path: str, result_dictionary: dict):
    name_of_file=path + result_dictionary['instance_name'] + ".json"
    json_file = open(name_of_file, "w")
    json.dump(result_dictionary, json_file, indent=4)
    json_file.close()


def open_input_file(filename):
        return open(filename, 'r')



with open_input_file(args.logfile) as logfile:

    sol_parser = Solution_Parser()
    filename_without_extension=args.logfile[:-len(".filmosi.log")]
    array=filename_without_extension.split("/")
    sol_parser.instance_name=array[len(array)-1]
    sol_parser.solver="(Fischetti, Ljubic, Monaci, Sinnl)-Solver";

    for line in logfile.readlines():
        if line[:len('STAT;')]=='STAT;':
            sol_parser.process_stat_line(line)
        elif sol_parser.feasible==0 or sol_parser.feasible==1:
            if line=="\n" or line.__contains__("AVAILABLE") or line.__contains__("LEADER COST") or line.__contains__("----") :
                continue
            else:
                sol_parser.process_solution_line(line)

result = sol_parser.assemble_result()
write_result_json(args.output_path,result)
