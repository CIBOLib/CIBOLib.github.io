# Usage: todo

# Usage through equaltity_terminator_executer:

python3 equality_terminator_executer --dir_path inputdir --output_dir outputdir

one can use the optional parameter --max_parallel 'number' to use 'number'-many subprocesses instead of only one.

# Validity:

The following grep queries in the collection folder must not return anything in the future, so that the conversion of E-constraints into G- and L-contraints by the provided Python script is valid:

grep -r 'INDICATORS' .
grep -r 'REFROW' .

The reason is that for efficiency reasons not the whole mps is parsed but only to the NAME ROWS, (optional: USERCUTS, LAZYCONS) COLUMNS and RHS section. In a usual mps we have following sections:
NAME
ROWS
COLUMNS
RHS
BOUNDS
ENDATA

# Assumptions:

Read more about the mps format: http://cgm.cs.mcgill.ca/~avis/courses/567/cplex/reffileformatscplex.pdf

## 1) 

On page 14 in this pdf we have a very interesting part: 
"For example, since ILOG CPLEX no longer requires fixed columnar positions, blank spaces are interpreted as delimiters. 
Older MPS files containing names with embedded spaces therefore become unreadable."

Therefore in older mps files a contraint or variable could have a blank included in its name.

However I do not expect this to be the case in any files of the collection. That is why the Python script just splits the lines.


## 2) 

On page 17:  "Several RHS vectors can exist. The name of each RHS vector appears in Field 2. However, only the first RHS vector is selected when a problem is read. 
Additional RHS vectors are discarded." 

Therefore the script discards every other rhs with anonther RHS identifier than the first one. I assume this may lead to smaller or equal sized results without changing the actual semantic of the mps.

## 3)

regarding the aux file: I assume that the sections are contiguous. 
Example: 
LR 1
LO 4
LR 2

would result in a not valid aux file.