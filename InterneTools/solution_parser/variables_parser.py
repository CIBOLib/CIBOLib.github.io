import gzip


class AuxParser():
    number_of_lower_constraints = 0
    number_of_lower_variables = 0
    # a dictionary that always contains True for all variable names/indices that are of the lower level
    lower_variable_dict = {}
    # a dictionary that always contains True for all variable names/indices that are of the lower level
    lower_constraint_dict = {}
    # a dictionary mapping the lower level variable index to the coefficient value of the lower level cost function
    lower_objective_coefficient_dict = {}
    # objective sense 1 -> min, -1 -> max
    objective_sense = 1

    # a list of the order that the LC entries appear in.
    lc_entries = []

    def __init__(self):
        pass

    def process_next_line(self, line):
        
        [val_type, value] = line.split()
        if value.isnumeric():
            value = int(value)
        if val_type == "N":
            self.number_of_lower_variables = int(value)
        elif val_type == "M":
            self.number_of_lower_constraints = int(value)
        elif val_type == "LC":
            self.lower_variable_dict[value] = True
            self.lc_entries.append(value)
        elif val_type == "LR":
            self.lower_constraint_dict[value] = True
        elif val_type == "LO":
            matching_lc_index = self.lc_entries.pop(0)
            self.lower_objective_coefficient_dict[matching_lc_index] = value
        elif val_type == "OS":
            self.objective_sense = value
        else:
            raise Exception('Invalid value type: ' + val_type)


class MpsParser():
    objsense = 'MAX'
    current_row_index = 0

    problem_name = None

    # a dictionary pointing from the row name to a tuple containing (row sense, bool is_lower)
    row_metadata = {}
    cost_row_name = None

    # a dict pointing from (row_name) to (is_lower: bool, entries: {column to (is_lower, coefficient)})
    row_entries = {}

    # a dict pointing from (row_name) to (is_lower: bool, coefficient)
    rhs_row_entries = {}

    # a dict pointing from the col name to the coefficient
    cost_vector_entries = {}
    # a dict ponting from the col name to the coefficient of the lower cost vector
    lower_cost_vector_entries = {}

    # a dictionary specifying the column type. only set if the variable is not real.
    column_types = {}

    # required to correctly count colmun indices
    current_column_name = None

    # internal:

    # we start the counter at -1 because it will be incremented at the first entry already
    current_column_index = -1
    # required to skip all but the first rhs ident
    first_rhs_ident = None
    int_marker_active = False

    def __init__(self, aux_parser):
        self.aux_parser = aux_parser

    def process_objsense(self, line):
        self.objsense = line.strip()

    def process_next_line(self, line):
        if line[0] != " ":
            next_section = line.strip()
            if next_section.startswith("NAME"):
                self.problem_name = line.split()[1].strip()
            elif next_section == "OBJSENSE":
                self.process_next_line_inner = self.process_objsense
            elif next_section == "ROWS":
                self.process_next_line_inner = self.process_rows_line
            elif next_section == "COLUMNS":
                self.process_next_line_inner = self.process_columns_line
            elif next_section == "RHS":
                self.process_next_line_inner = self.process_rhs_line
            elif next_section == "RANGES":
                self.process_next_line_inner = self.process_ranges_line
            elif next_section == "BOUNDS":
                self.process_next_line_inner = self.process_bounds_line
            elif next_section == "ENDATA":
                self.process_next_line_inner = self.process_end
            else:
                raise Exception(f"unknown section marker: {next_section}")
        else:
            self.process_next_line_inner(line)

    def process_end(self, line):
        if len(line.strip()) > 0:
            raise Exception("found non empty line after ENDATA")

    def process_ranges_line(self, line):
        # do nothing here
        return

    def process_bounds_line(self, line):
        # do nothing here
        return

    def process_rhs_line(self, line):
        # do nothing here
        return

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
        if row_type in ["G", "L", "N"]:
            self.row_metadata[row_name] = (row_type, is_lower_row)
        else:
            raise Exception(f"unsupported row sense found: {row_type}")

    def process_columns_line(self, line):
        if "'MARKER'" in line:
            if "'INTORG'" in line:
                self.int_marker_active = True
            elif "'INTEND'" in line:
                self.int_marker_active = False
            else:
                raise Exception('Invalid marker row found: ' + line.strip())
            return

        [column_name, row_name, value] = line.split()

        if self.current_column_name != column_name:
            self.current_column_index += 1
            self.current_column_name = column_name

        (row_sense, row_is_lower) = self.row_metadata[row_name]
        is_lower_column = column_name in self.aux_parser.lower_variable_dict or self.current_column_index in self.aux_parser.lower_variable_dict

        if is_lower_column:
            self.lower_cost_vector_entries[column_name] = self.aux_parser.lower_objective_coefficient_dict[self.current_column_index]

        value = float(value)
        if row_sense == "G":
            value *= -1

        if row_sense == "N" and self.cost_row_name == row_name:
            self.cost_vector_entries[column_name] = value
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
            'instance_name': self.problem_name,
            'leader_objective_sense': self.objsense,
            'leader_variables': upper_variables,
            'follower_variables': lower_variables,
            'follower_objective_sense': self.aux_parser.objective_sense,
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
