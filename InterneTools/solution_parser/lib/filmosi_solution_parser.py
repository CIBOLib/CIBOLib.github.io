from os import path
from . import variables_parser
import os

class Filmosi_Solution_Parser():


    def __init__(self):
        self.instance_name=""
        self.input_file=None
        self.root_bound=None
        self.time=-1
        self.root_time=-1
        self.feasible=-100
        self.nodes=-1
        self.setting=None

        self.solver="(Fischetti, Ljubic, Monaci, Sinnl)-Solver"
        self.solver_status=None
        self.objective_value=None
        self.best_dual_bound=None
        self.final_gap_percentage=None
        self.root_gap_percentage=None
        self.upper_variables={}
        self.lower_variables={}
        self.variables={}

    def process_stat_line(self, line):
        # STAT[0]; input_file[1] ; zbest[2] ; final_bound[3] ; root_bound[4] ; time (s.)[5] ; root_time (s.)[6] ; opt[7]->(-1,0,1) ; nodes[8] ; %root_gap[9] ; %final_gap[10] ; setting[11]
        if line.startswith("STAT;ERROR: solution not bilevel feasible"):
            self.solver_status="ERROR: solution not bilevel feasible"
            return
        try:
            line=line.replace(" ","")
            data=line.split(";")
            self.input_file=data[1]
            self.objective_value=float(data[2])
            self.best_dual_bound=float(data[3])
            self.root_bound=float(data[4])
            self.time=float(data[5])
            self.root_time=float(data[6])
            self.feasible=int(data[7])
            self.nodes=int(data[8])
            self.root_gap_percentage=float(data[9])
            self.final_gap_percentage=float(data[10])
            self.setting=data[11]

            if self.feasible>=0:
                if self.time>=3600 or self.feasible==0: #or only if there are special cases, I do not know yet
                    self.solver_status="not solved to optimality"
                else:
                    self.solver_status="solved to optimality"
            return
        except: raise Exception("unknown status")

    def process_solution_line(self, line):
        line=line.strip(' ')
        array=line.split(" ")
        variable, variable_value=array[0],float(array[len(array)-1])
        self.variables[variable]=variable_value

    def assemble_result(self, mps_file, aux_file):
        if len(self.variables)>0 and self.feasible!=-100:
            metadata = variables_parser.get_metadata(mps_file, aux_file)
            upper_variables_names=metadata['leader_variables']
            lower_variables_names=metadata['follower_variables']

            for variable in self.variables.keys():
                if variable in upper_variables_names:
                    self.upper_variables[variable]=self.variables[variable]
                elif variable in lower_variables_names:
                    self.lower_variables[variable]=self.variables[variable]
                else:
                    self.upper_variables[variable]=self.variables[variable]
                    #raise Exception("Variable not found in original instance", variable);
                    #-> the variable has to be an upper level variable OR it is really not in the instance (I do not assume this case here)


        soldata = {
            'instance_name': self.instance_name,
            'solver':self.solver,
            'solver_status':self.solver_status,
            'objective_value': self.objective_value,
            'best_dual_bound': self.best_dual_bound,
            'input_file':self.input_file,
            'root_bound':self.root_bound,
            'time':self.time,
            'root_time':self.root_time,
            'feasible':self.feasible,
            'nodes':self.nodes,
            'root_gap_percentage':self.root_gap_percentage,
            'best_dual_bound_percentage':self.final_gap_percentage,
            'setting':self.setting,
            'leader_variables': self.upper_variables,
            'follower_variables': self.lower_variables,
        }
        return soldata

    def run(self, mps_file: str, aux_file: str, logfile: str) -> dict:
        self.instance_name = path.basename(logfile).removesuffix(".filmosi.log")
        with open(logfile, "r") as input_file:
            for line in input_file.readlines():
                if line[:len('STAT;')]=='STAT;':
                    self.process_stat_line(line)
                elif self.feasible==0 or self.feasible==1:
                    if line.__contains__("NO SOLUTION AVAILABLE") or self.solver_status=="ERROR: solution not bilevel feasible":
                        break
                    elif line=="\n" or line.__contains__("AVAILABLE") or line.__contains__("LEADER COST") or line.__contains__("----") :
                        continue
                    else:
                        self.process_solution_line(line)


        return self.assemble_result(mps_file, aux_file)
