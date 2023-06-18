import gzip


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
    return result


class AuxParser():

    def __init__(self):
        # a dictionary that always contains True for all variable names/indices that are of the lower level
        self.lower_variable_dict = {}
        # a dictionary that always contains True for all variable names/indices that are of the lower level
        self.lower_constraint_dict = {}
        self.number_of_follower_vars = 0
        # a list of the order that the LC entries appear in.
        self.lc_entries = []

    def process_next_line(self, line):
        array = line.split()
        if len(array) == 2:
            [val_type, value] = array
        elif len(array) == 0:  # empty
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
        elif val_type == "N":
            self.number_of_follower_vars = value
        else:
            return


class MpsParser():

    def __init__(self, aux_parser):
        self.aux_parser = aux_parser

        self.current_row_index = 0

        # a dictionary pointing from the row name to a tuple containing (row sense, bool is_lower)
        self.row_metadata = {}
        self.cost_row_name = None

        # a dict pointing from (row_name) to (is_lower: bool, entries: {column to (is_lower, coefficient)}), TODO:coefficient not relevant here can refactor more
        self.row_entries = {}

        # required to correctly count column indices
        self.current_column_name = None

        # internal:

        # we start the counter at -1 because it will be incremented at the first entry already
        self.current_column_index = -1
        #

        # dicts pointing from column to always True
        self.columns_in_upper_level = {}
        self.columns_in_lower_level = {}

        # the column names in order of appearance
        self.original_column_order_of_appearance_upper = []
        self.original_column_order_of_appearance_lower = []

    def process_next_line(self, line):
        if len(line) == 0:
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
            elif next_section == "BOUNDS":
                self.process_next_line_inner = self.process_bounds_line
            elif next_section in ["RANGES", "RHS"]:
                self.process_next_line_inner = self.process_non_relevant_line
            elif next_section == "ENDATA":
                self.process_next_line_inner = self.process_end
            else:
                # raise Exception(f"unknown section marker: {next_section}")
                pass
        else:
            self.process_next_line_inner(line)

    # mibs format does not see bounds as LR in the aux-File. IMPORTANT. current_row_index could be not necessary here
    def process_bounds_line(self, line):
        split = line.split()
        [bound_type, bound_name, column_name] = line.split()[:3]
        current_row_index = self.current_row_index
        self.current_row_index += 1
        is_lower = current_row_index in self.aux_parser.lower_constraint_dict or column_name in self.columns_in_lower_level

        self.include_column(column_name, is_lower)

    def include_column(self, column_name, is_lower):
        if is_lower:
            if not column_name in self.columns_in_lower_level:
                self.columns_in_lower_level[column_name] = True
                self.original_column_order_of_appearance_lower.append(
                    column_name)
        else:
            if not column_name in self.columns_in_upper_level:
                self.columns_in_upper_level[column_name] = True
                self.original_column_order_of_appearance_upper.append(
                    column_name)

    def process_non_relevant_line(self, line):
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
        else:
            line = line.split()
            [column_name, row_name, value] = line[:3]
            self.handle_column_line_value(column_name, row_name, value)
            line = line[3:]
            if len(line) > 0:
                [row_name, value] = line
                self.handle_column_line_value(column_name, row_name, value)

    def handle_column_line_value(self, column_name, row_name, value):
        if self.current_column_name != column_name:
            self.current_column_index += 1
            self.current_column_name = column_name

        (row_sense, row_is_lower) = self.row_metadata[row_name]
        is_lower_column = column_name in self.aux_parser.lower_variable_dict or self.current_column_index in self.aux_parser.lower_variable_dict

        # cost vector, not relevant for us here, but there can only be one
        if row_sense == "N" and self.cost_row_name != row_name:
            raise Exception("instance has more than one N-Rows:", self.cost_row_name, "and", row_name)

        self.include_column(column_name, is_lower_column)

    def assemble_result(self):
        if len(self.original_column_order_of_appearance_lower) != self.aux_parser.number_of_follower_vars:
            raise Exception(
                f"Conflict regarding follower variables: identified vars - {len(self.original_column_order_of_appearance_lower)} vs. aux-file N - {self.aux_parser.number_of_follower_vars}")
        if len(set(self.columns_in_lower_level.keys()).intersection(set(self.columns_in_upper_level.keys()))) > 0:
            raise Exception(
                "Some variables could not be distinguished as leader xor follower variables")
        metadata = {
            'leader_variables': self.original_column_order_of_appearance_upper,
            'follower_variables': self.original_column_order_of_appearance_lower,
        }
        return metadata
