
inputfile="./MIPLIB2010/mps-files/bienst2.mps"

outputfile = "outputfile.mps"

class Parser:

    # this is a dictinoary containing true if the row was initially an equality.
    old_equality_rows = {}

    rhs_ident = None

    def __init__(self, outputfile):
        self.outputfile = outputfile
        self.process_next_line_inner = self.emit_line

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

    def output(self, line):
        self.emit_line(line + "\n")

    def emit_line(self, line):
        self.outputfile.write(line)

    def process_rows_line(self, line):
        [row_type, row_name] = line.split()
        if row_type != "E":
            self.emit_line(line)
        else:
            self.old_equality_rows[row_name] = True
            self.output(f" L {row_name}_le")
            self.output(f" G {row_name}_ge")

    def process_columns_line(self, line):
        def handle_value(column_name, row_name, value):
            if row_name in self.old_equality_rows:
                self.output(f" {column_name} {row_name}_le {value}")
                self.output(f" {column_name} {row_name}_ge {value}")
            else:
                self.output(f" {column_name} {row_name} {value}")

        line = line.split()
        [column_name, row_name, value] = line
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
        [rhs_name, row_name, value] = line
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

with open(inputfile, 'r') as file, open(outputfile, 'w') as output:
    parser = Parser(output)
    for line in file.readlines():
       parser.process_next_line(line)
