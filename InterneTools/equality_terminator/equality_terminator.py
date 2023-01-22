import argparse
import os.path as path

arg_parser = argparse.ArgumentParser(description="decomposes equations into inequalities for mps/aux problems")
arg_parser.add_argument('mps_file', action='store', help='the input mps file')
arg_parser.add_argument('--aux_files', action='store', nargs='*', help='aux files that belong to the specified mps file. May be used multiple times')
arg_parser.add_argument('--aux_output_dir', action='store', required=True, help='A directory to write the resulting aux files to')
arg_parser.add_argument('--mps_output_dir', action='store', required=True, help='A directory to write teh resulting mps files to')
arg_parser.add_argument('--gzip_output', action='store_true', help="compress the output using gzip (note: this does not change the file extension)")

args = arg_parser.parse_args()
# print(args)

class ParserBase:
    def __init__(self, outputfile):
        self.outputfile = outputfile
        self.process_next_line_inner = self.emit_line

    def output(self, line):
        self.emit_line(line + "\n")

    def emit_line(self, line):
        self.outputfile.write(line)


class MpsParser(ParserBase):
    # this is a dictinoary containing true if the row was initially an equality.
    old_equality_rows = {}
    # this is a list telling us the row name of an old index
    old_row_ordering = []
    # this is a dictionary mapping our new row names to the indices they appear in the file
    new_row_indices = {}


    rhs_ident = None

    def process_next_line(self, line):
        if line[0] != " ":
            next_section = line.strip()
            if next_section.startswith("NAME"):
                self.emit_line(line)
            elif next_section in ["ROWS", "USERCUTS", "LAZYCONS"]:
                self.process_next_line_inner = self.process_rows_line
            elif next_section == "COLUMNS":
                self.process_next_line_inner = self.process_columns_line
            elif next_section == "RHS":
                self.process_next_line_inner = self.process_rhs_line
            else:
                # ensure that the function does not do anything if called again
                self.process_next_line_inner = self.emit_line
            self.emit_line(line)
        else:
            self.process_next_line_inner(line)


    def process_rows_line(self, line):
        [row_type, row_name] = line.split()
        # update our old row order list
        self.old_row_ordering.append(row_name)
        def insert_row_index(row_name):
            idx = len(self.new_row_indices)
            self.new_row_indices[row_name] = idx

        if row_type != "E":
            self.emit_line(line)
            insert_row_index(row_name)
        else:
            self.old_equality_rows[row_name] = True
            le_name = row_name + "_le"
            ge_name = row_name + "_ge"
            self.output(f" L {le_name}")
            self.output(f" G {ge_name}")
            insert_row_index(le_name)
            insert_row_index(ge_name)

    def process_columns_line(self, line):
        def handle_value(column_name, row_name, value):
            if row_name in self.old_equality_rows:
                self.output(f" {column_name} {row_name}_le {value}")
                self.output(f" {column_name} {row_name}_ge {value}")
            else:
                self.output(f" {column_name} {row_name} {value}")

        line = line.split()
        [column_name, row_name, value] = line[:3]
        handle_value(column_name, row_name, value)
        line = line[3:]
        if len(line) > 0:
            [row_name, value] = line
            handle_value(column_name, row_name, value)

    def process_rhs_line(self, line):
        def handle_value(row_name, value):
            if row_name in self.old_equality_rows:
                self.output(f" {self.rhs_ident} {row_name}_le {value}")
                self.output(f" {self.rhs_ident} {row_name}_ge {value}")
            else:
                self.output(f" {self.rhs_ident} {row_name} {value}")

        line = line.split()
        [rhs_name, row_name, value] = line[:3]
        line = line[3:]
        if self.rhs_ident != rhs_name:
            if self.rhs_ident is None:
                self.rhs_ident = rhs_name
            else:
                return
        handle_value(row_name, value)
        if len(line) > 0:
            [row_name, value] = line
            handle_value(row_name, value)

class AuxParser(ParserBase):

    number_of_constraints = 0
    # the lines before we actually get to read the LR section we are interested in
    buffered_lines = []

    buffer_emitted = False
    lr_section_reached = False

    def __init__(self, outputfile, mps_parser):
        super().__init__(outputfile)
        self.mps_parser = mps_parser

    def process_next_line(self, line):
        [val_type, value] = line.split()
        if val_type == "N":
            self.emit_line(line)
        elif val_type == "M":
            self.number_of_constraints = int(value)
        elif val_type == "LR":
            self.lr_section_reached = True
            self.process_lr_value(value)
        else:
            if self.lr_section_reached:
                if not self.buffer_emitted:
                    self.buffer_emitted = True
                    self.emit_buffer()
                self.emit_line(line)
            else:
                self.buffered_lines.append(line)

    def process_end_reached(self):
        if not self.buffer_emitted:
            self.emit_buffer()


    def process_lr_value(self, value):
        def emit_lr_for_rowname(row_name):
            new_idx = self.mps_parser.new_row_indices[row_name]
            self.buffered_lines.append(f"LR {new_idx}\n")

        old_idx = int(value)
        row_name = self.mps_parser.old_row_ordering[old_idx]
        if row_name in mps_parser.old_equality_rows:
            self.number_of_constraints += 1
            emit_lr_for_rowname(row_name + "_le")
            emit_lr_for_rowname(row_name + "_ge")
        else:
            emit_lr_for_rowname(row_name)

    def emit_buffer(self):
        self.output(f"M {self.number_of_constraints}")
        for line in self.buffered_lines:
            self.emit_line(line)
        self.buffered_lines = []




def open_input_file(filename):
    if filename.endswith('.gz'):
        import gzip
        return gzip.open(filename, 'rt')
    else:
        return open(filename, 'r')
def open_output_file(filename):
    out_dir = args.mps_output_dir
    if filename.endswith("aux"):
        out_dir = args.aux_output_dir
    outputfile = path.join(out_dir, path.basename(filename))
    if args.gzip_output and filename.endswith(".gz"):
        import gzip
        return gzip.open(outputfile, 'wt')
    else:
        return open(outputfile, 'w')



with open_input_file(args.mps_file) as mps_file, open_output_file(args.mps_file) as output:
    mps_parser = MpsParser(output)
    for line in mps_file.readlines():
       mps_parser.process_next_line(line)

for aux_file in args.aux_files:
    with open_input_file(aux_file) as aux_input, open_output_file(aux_file) as output:
        aux_parser = AuxParser(output, mps_parser)
        for line in aux_input.readlines():
            aux_parser.process_next_line(line)
        aux_parser.process_end_reached()


