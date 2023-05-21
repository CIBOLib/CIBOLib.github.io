import gzip


class AuxParser():
    # a dictionary that always contains True for all variable names/indices that are of the lower level
    lower_variable_dict = {}
    # a dictionary that always contains True for all variable names/indices that are of the lower level
    lower_constraint_dict = {}

    # a list of the order that the LC entries appear in.
    lc_entries = []

    def __init__(self):
        pass

    def process_next_line(self, line):
        array = line.split()
        if len(array)==2:
            [val_type, value]=array
        elif len(array)==0:#empty
            return
        else:
            raise Exception("weird line")
        if value.isnumeric():
            value = int(value)
        if val_type == "LC":
            self.lower_variable_dict[value] = True
            self.lc_entries.append(value)
        elif val_type == "LR":
            self.lower_constraint_dict[value] = True
        else:
            return


class MpsParser():
    current_row_index = 0

    # a dictionary pointing from the row name to a tuple containing (row sense, bool is_lower)
    row_metadata = {}
    cost_row_name = None

    # a dict pointing from (row_name) to (is_lower: bool, entries: {column to (is_lower, coefficient)}), TODO:coefficient not relevant here can refactor more 
    row_entries = {}

    # required to correctly count column indices
    current_column_name = None

    # internal:

    # we start the counter at -1 because it will be incremented at the first entry already
    current_column_index = -1
    # 

    def __init__(self, aux_parser):
        self.aux_parser = aux_parser


    def process_next_line(self, line):
        if len(line)==0:
            return
        if line[0] != " ":
            next_section = line.strip()
            if next_section.startswith("NAME") or next_section.startswith("*NAME"):
                pass
            elif next_section == "OBJSENSE":
                self.process_next_line_inner = self.process_non_relevant_line
            elif next_section == "ROWS":
                self.process_next_line_inner = self.process_rows_line
            elif next_section == "COLUMNS":
                self.process_next_line_inner = self.process_columns_line
            elif next_section in ["RANGES", "RHS", "BOUNDS"]:
                self.process_next_line_inner = self.process_non_relevant_line
            elif next_section == "ENDATA":
                self.process_next_line_inner = self.process_end
            else:
                pass  #raise Exception(f"unknown section marker: {next_section}")
        else:
            self.process_next_line_inner(line)
    
    def process_non_relevant_line(self,line):
        return
    
    def process_end(self, line):
        if len(line.strip()) > 0:
            raise Exception("found non empty line after ENDATA")

    def process_rows_line(self, line):
        [row_type, row_name] = line.split()
        current_row_index = self.current_row_index
        if row_type != "N":
            self.current_row_index += 1
        is_lower_row = current_row_index in self.aux_parser.lower_constraint_dict or row_name in self.aux_parser.lower_constraint_dict
        if row_type == "N":
            # cost vector row
            if self.cost_row_name is None:
                self.cost_row_name = row_name
            pass
        if row_type in ["G", "L", "N", "E"]:
            self.row_metadata[row_name] = (row_type, is_lower_row)
        else:
            raise Exception(f"unsupported row sense found: {row_type}")

    def process_columns_line(self, line):
        if "'MARKER'" in line:
            return

        line = line.split()
        [column_name, row_name, value] = line[:3]
        self.handle_column_line_value(column_name, row_name, value)
        line = line[3:]
        if len(line) > 0:
            [row_name, value] = line
            self.handle_column_line_value(column_name, row_name, value)

    def handle_column_line_value(self,column_name, row_name, value):
        if self.current_column_name != column_name:
            self.current_column_index += 1
            self.current_column_name = column_name

        (row_sense, row_is_lower) = self.row_metadata[row_name]
        is_lower_column = column_name in self.aux_parser.lower_variable_dict or self.current_column_index in self.aux_parser.lower_variable_dict

        value = float(value)
        if row_sense == "G":
            value *= -1

        if row_sense == "N" and self.cost_row_name == row_name: #cost vector, not relevant for us here, but there can only be one
            return

        if row_name in self.row_entries:
            (_, row_dict) = self.row_entries[row_name]
        else:
            row_dict = {}
            self.row_entries[row_name] = (row_is_lower, row_dict)
        row_dict[column_name] = (is_lower_column, value)
    
    def assemble_result(self):
        all_variable_entries = set((col, is_lower) for (
            _, dict) in self.row_entries.values() for (col, (is_lower, _)) in dict.items())
        upper_variables = [col for (col, is_lower)
                           in all_variable_entries if not is_lower]
        lower_variables = [col for (col, is_lower)
                           in all_variable_entries if is_lower]
        upper_variables.sort()
        lower_variables.sort()

        metadata = {
            'leader_variables': upper_variables,
            'follower_variables': lower_variables,
        }
        return metadata


def open_input_file(filename):
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt')
    else:
        return open(filename, 'r')

def get_metadata(mpsfile_name, auxfile_name):
    with open_input_file(auxfile_name) as auxfile:
        aux_parser = AuxParser()
        for line in auxfile.readlines():
            aux_parser.process_next_line(line)
    with open_input_file(mpsfile_name) as mpsfile:
        mps_parser = MpsParser(aux_parser)
        for line in mpsfile.readlines():
            mps_parser.process_next_line(line)

    result = mps_parser.assemble_result()
    return result;
