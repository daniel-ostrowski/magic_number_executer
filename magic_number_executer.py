#!/bin/python3

import re

# The idea is for every non-negative integer to be a valid program, even if the
# program makes no sense. Thus the MN runtime avoids erroring even in cases such
# as underflowing the stack or printing the ascii value of a negative number.

# As an argument naming convention, "verband" means "that which must be verbed"

# The global stack. All access to the stack should be performed using the
# push() and pop() functions.
stack = []

# The hash which maps label numbers to statement numbers.
labels = {}

# A lookup table mapping opcodes to the instructions they specify.
OPCODES = {"001" : "push_integer", "002" : "push_float"}

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
    # Ensure argument is a float
    if (type(pushand) != float):
        raise ValueError(("Magic Number Executer internally attempted to " + \
              "push a non-float value onto the stack.\nValue was \"{}\" of " + \
              "type \"{}\"").format(pushand, type(pushand)))
    # Push the argument onto the stack
    stack.append(pushand)

# Pop the top of the MN program's stack. If the stack is empty, throw an
# exception.
def pop():
    # Ensure the stack is non-empty
    if len(stack) == 0:
        raise StackUnderflow()
    # Pop the top of the stack and return the value
    return stack.pop()

# As a convention, the functions for performing different commands in MN take as
# input the whole raw string source statement for the command. The functions
# assume that the input is valid

# Interpret and execute a push of an integer constant. An integer push has the
# format: 001sdddddd, s = 0 -> positive, s = 1 -> negative, d = decimal digit
# Example: 0011001234 is -1234
def push_integer(instruction):
    # Ensure the instruction is 10 digits
    if re.match("$\d{10}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction was actually an addition
    opcode = instruction[:3]
    if opcode != "001":
        raise MisinterpretedInstruction(OPCODES[opcode], "addition")
    # Ensure the sign is valid
    sign = instruction[3]
    if sign != "0" and sign != "1":
        raise InvalidMNInstruction(instruction)
    sign_multiplier = 1 if sign == "0" else -1
    # Parse the integer and push it onto the stack
    integer = int(instruction[4:])
    push(integer)

# Interpret and execute a push of a floating point constant. A floating point
# push has the format: 002deesmmmmmm, d = 0 -> positive exponent, d = 1 ->
# negative exponent, e = decimal digit of exponent, s = 0 -> positive value,
# s = 1 -> negative value, m = decimal digit of mantissa
# Example: 0021021000002 is -2e-2 == -.02
def push_float():
    pass

# Interpret and execute the reading of a float from standard input, to be put
# onto the stack.
def read_float():
    pass

# Interpret and execute the reading of a char from standard input. Try to
# coerce the read float into an integer which validly represents an ascii char.
# If such a coercion is possible, push the integer value onto the stack.
# Otherwise, do not push anything onto the stack.
def read_char():
    pass

# Interpret and execute the printing a float to standard output. No control
# over precision displayed is provided.
def print_float():
    pass

# Interpret and execute the printing of a char to standard output. Try to coerce
# the argument into an integer which validly represents an ascii char. If such a
# coercion is possible, print that ascii char. Otherwise, do not print anything.
def print_char():
    pass

# Interpret and execute the declaration of a label at the current position in
# the program. This could be performed prior to program execution.
def create_label():
    pass

# Interpret and execute coercion of a float to 1 or 0. If abs(argument) < .0001,
# push 0, otherwise push 1.
def coerce_to_boolean():
    pass

# Interpret and execute a conditional branching instruction. If the top of the
# stack is a truthy value, jump to the label specified in the instruction.
def branch_if_equal():
    pass

# Interpret and execute a logical NOT. If the top of the stack is a truthy
# value, push 0, otherwise push 1.
def logical_not():
    pass

# Interpret and execute a logical AND.
def logical_and():
    pass

# Interpret and execute a logical OR.
def logical_or():
    pass

# Interpret and execute a comparison. If the top of the stack is less than the
# second-highest value of the stack, push 1, otherwise push 0.
def less_than():
    pass

# Interpret and execute a comparison. If the top of the stack is greater than
# the second-highest value of the stack, push 1, otherwise push 0.
def greater_than():
    pass

# Interpret and execute a comparison.
# If the abs(top of stack - second-highest value of stack) < 0.0001, push 1,
# otherwise push 0
def equal():
    pass

# Interpret and execute floating point addition.
def add():
    pass

# Interpret and execute floating point subtraction. The second-highest value on
# the stack is subtracted from the highest value on the stack.
def subtract():
    pass

# Interpret and execute floating point multiplication.
def multiply():
    pass

# Interpret and execute floating point division. The highest value on the stack
# is divided by the second-highest value on the stack.
def divide():
    pass

# All values are floating point. Throughout the code, to say that 'foo' and
# 'bar' are equal really means abs(foo - bar) < 0.0001

# Simple custom exception signifying underflow of the MN program's stack
class StackUnderflow(BaseException):
    def __init__(self, message):
        self.message = "Magic Number Executer attempted to underflow the" + \
                       " stack. Although this is caused by the MN program," + \
                       "the exception should have been handled internally."

# Simple custom exception signifying that the format of an instruction being
# executed is invalid.
class InvalidMNInstruction(BaseException):
    def __init__(self, instruction):
        self.message = "Magic Number Executer encountered an instruction " + \
                       "which was invalid: {}. Although this is caused by " + \
                       "the MN program, the exception should have been " + \
                       "gracefully treated as a no-op.".format(instruction)

# Simple custom exception signifying that the opcode of an instruction passed to
# a function meant to execute a specific type of instruction is the opcode for a
# different instruction, eg add() is passed a subtract instruction.
class MisinterpretedInstruction(BaseException):
    def __init__(self, actual, intended):
        self.message = "Magic Number Executer misinterpreted {} as {}. " + \
                       "This is an internal error.".format(actual, intended)
