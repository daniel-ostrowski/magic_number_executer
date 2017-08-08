#!/bin/python3

# The idea is for every non-negative integer to be a valid program, even if the
# program makes no sense. Thus the MN runtime avoids erroring even in cases such
# as underflowing the stack or printing the ascii value of a negative number.

# As an argument naming convention, "verband" means "that which must be verbed"

# The global stack. All access to the stack should be performed using the
# push() and pop() functions.
stack = []

# The hash which maps label numbers to statement numbers.
labels = {}

# The list of statements in the program. This is simply the program's source
# code split into pieces.
program_statements = []

# Load a MN file. Simply read the entire file and remove non-digits. No check
# for validity is performed.
def load_MN_file(loadand):
    pass

# Parse a MN file. This is simply a matter of splitting the source code into
# individual statements.
def parse_MN_program_source(program_source):
    pass

# Execute a MN program
def execute_MN_program():
    pass

# Ensure the argument is a float, then push the argument onto the MN program's
# stack. Otherwise throw an exception.
def push(pushand):
    pass

# Pop the top of the MN program's stack. If the stack is empty, throw an
# exception.
def pop():
    pass

# As a convention, the functions for performing different commands in MN take as
# input the whole raw source statement for the command. The functions assume
# that the input is valid

# Interpret and execute a push of an integer constant.
def push_integer():
    pass

# Interpret and execute a push of a floating point constant.
def push_float():
    pass

# Interpret and execute the reading of a float from standard input, to be put
# onto the stack.
def read_float():
    pass

# Interpret and execute the reading of a float from standard input. Try to
# coerce the float into an integer which validly represents an ascii char.
# If such a coercion is possible, push the integer value onto the stack.
# Otherwise, do not push anything onto the stack.
def read_char():
    pass

# All values are floating point. Throughout the code, to say that 'foo' and
# 'bar' are equal really means abs(foo - bar) < 0.0001

# Commands
## Push specified value onto the stack
## Pop top of stack and store value into specified register
## Push integer constant
## Push float constant
## Read a float from standard in
# 'Tolerantly' read a float from standard in and try to coerce it into a char
# Print a float
# Print a char
# Declare a label
# Coerce top of stack to 1 if nonzero and 0 otherwise
# Pop the top of the stack 'foo', pop the top of the stack 'location'.
# if 'foo' is not 'tolerantly' equal to 0, go to 'location'.
# Pop the top of the stack 'foo'. Push !foo
# Pop top of stack 'foo', pop top of stack 'bar', then push
# Floating point addition:       foo + bar
# Floating point subtraction:    foo - bar
# Floating point multiplication: foo * bar
# Floating point division:       foo / bar
# Less than:                     foo < bar ? 1 : 0
# Greater than:                  foo > bar ? 0 : 1
# 'Tolerant' equality:           abs(foo - bar) < 0.0001 ? 1 : 0
# And:                           foo && bar ? 1 : 0
# Or:                            foo || bar ? 1 : 0
