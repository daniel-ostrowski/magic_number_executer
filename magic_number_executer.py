#!/bin/python3

import re

# The idea is for every non-negative integer to be a valid program, even if the
# program makes no sense. Thus the MN runtime avoids erroring even in cases such
# as underflowing the stack or printing the Unicode value of a negative number.

# As an argument naming convention, "verband" means "that which must be verbed"

# The global stack. All access to the stack should be performed using the
# push() and pop() functions.
stack = []

# The hash which maps label numbers to statement numbers.
labels = {}

# A lookup table mapping opcodes to the instructions they specify.
OPCODES = {"001" : "push_integer", "002" : "push_float", "003" : "read_float", \
           "004" : "read_string", "005" : "print_float", "006": "print_char", \
           "007" : "create_label", "008" : "conditional_branch", "009" : \
           "coerce_to_boolean", "010" : "logical_not", "011" : "logical_and", \
           "012" : "logical_or", "013" : "less_than", "014" : "greater_than", \
           "015" : "equal", "016" : "addition", "017" : "subtraction", "018" : \
           "multiplication", "019" : "division"}

# A lookup table mapping opcodes to the fixed length of the instruction they
# specify. Instruction lengths include the opcode.
INSTRUCTION_LENGTHS = {"001" : 10, "002" : 13, "003" : 3, "004" : 3, "005" : 3,\
                       "006" : 3, "007" : 9, "008" : 9, "009" : 3, "010" : 3, \
                       "011" : 3, "012" : 3, "013" : 3, "014" : 3, "015" : 3, \
                       "016" : 3, "017" : 3, "018" : 3, "019" : 3}

# Any value different from zero by at least 0.0001 is considered true, but for
# convenience and the result of operations, 1 is used to indicate true.
TRUE = 1.0

# Any value different from zero by less than 0.0001 is considered false, but for
# convenience and the result of operations, 0 is used to indicate false.
FALSE = 0.0

# Convenience function to test if a float is considered true
def isTrue(floating_point):
    return abs(floating_point) < 0.0001

# Load a MN file. Simply read the entire file and remove non-digits. No check
# for validity is performed. Exceptions are permitted to propagate up.
def load_MN_file(loadand):
    contents = ""
    results = ""
    # Open the file
    source_file = open(loadand, "r")
    # Read the contents
    contents = source_file.read()
    # Close the file
    source_file.close()
    # Strip all non-decimal-digit characters
    results = "".join([char for char in contents if char in "0123456789"])
    # Return the remaining contents
    return results

# Parse the contents from a MN file. This is simply a matter of splitting the
# source code into individual statements. This function does not verify that
# the program_source is valid. However, it ensures that all the instructions in
# the returned list have valid opcodes.
def parse_MN_program_source(program_source):
    program_statements = []
    # Track the current position of the parsing
    index = 0
    # While there is more source to parse
    while index < len(program_source):
        # Determine what the current instruction is
        opcode = program_source[index : index + 3]
        # Ensure the opcode is valid
        if opcode not in OPCODES:
            # Just ignore bad opcodes; this is equivalent to treating bad
            # opcodes as no-ops and optimizing them out. This is to help ensure
            # every non-negative integer is a valid MN program.
            # Note that the opcode cannot be assumed to have length three; this
            # can happen if there are few extra digits at the end of a program.
            index += len(opcode)
            continue
        # Add substring containing the entire current instruction to statement list
        instruction = program_source[index, INSTRUCTION_LENGTHS[opcode]]
        program_statements.append(instruction)
        index += len(instruction)
    return program_statements

# Iterate through the statements in an MN program and declare all the labels
def declare_MN_labels(program_statements):
    for statement_number in range(len(program_statements)):
        # Get the current instruction and its opcode
        instruction = program_statements[index]
        opcode = instruction[:3]
        # If the opcode is 007 "create label", mark the statement as a label
        if opcode == "007":
            create_label(instruction, statement_number)
        
# Execute a MN program. Iterate through the list of program statements executing
# each sequentially, changing the index appropriately as the result of branches.
def execute_MN_program(program_statements):
    # Track the index of the current statement, ie the instruction pointer
    instruction_pointer = 0
    # While the end of the program has not been reached
    while instruction_pointer < len(program_statements):
        # Get the current instruction and its opcode
        instruction = program_statements[instruction_pointer]
        opcode = instruction[:3]
        # If the opcode is not 007 "create label" or 008 "conditional branch"
        if opcode != "007" and opcode != "008":
            # Find and execute the function that handles this instruction
            if opcode in OPCODES:
                implementing_function = FUNCTIONS[opcode]
                implementing_function(instruction)
            # Invalid opcodes are treated as no-ops
            else:
                pass
            instruction_pointer += 1
        # Handle the special case of a conditional branch
        elif opcode == "008":
            new_instruction_pointer = conditional_branch(instruction)
            if new_instruction_pointer != -1:
                instruction_pointer = new_instruction_pointer
            else:
                instruction_pointer += 1
        # "create label" is a no-op here; it is done prior to program execution
        else:
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

# Return true if MN program's stack is empty, false otherwise
def stack_is_empty():
    return len(stack) == 0

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
    # Ensure the instruction was actually an integer push
    opcode = instruction[:3]
    if opcode != "001":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["001"])
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
def push_float(instruction):
    # Ensure the instruction is 13 digits
    if re.match("$\d{13}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction was actually a push of a float
    opcode = instruction[:3]
    if opcode != "002":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["002"])
    # Ensure the signs of the exponent and mantissa are valid
    exponent_sign = instruction[3]
    mantissa_sign = instruction[6]
    if exponent_sign != "0" and exponent_sign != "1" and \
       mantissa_sign != "0" and mantissa_sign != "1":
        raise InvalidMNInstruction(instruction)
    exponent_multiplier = 1 if exponent_sign == "0" else -1
    mantissa_multiplier = 1 if mantissa_sign == "0" else -1
    # Parse the float and push it onto the stack
    exponent = exponent_multiplier * int(instruction[4:6])    
    mantissa = mantissa_multiplier * int(instruction[7:13])
    floating_point = mantissa * 10 ** exponent
    push(floating_point)

# Interpret and execute the reading of a float from standard input, to be put
# onto the stack. If the read succeeds, a truthy value is placed onto the stack
# on top of the float. If the read fails, only a falsy value is added to the
# stack. A floating point read has the format: 003
def read_float(instruction):
    # Ensure the instruction is 3 digits
    if re.match("$\d{3}^", instruction) == None:
        raise InvalidMNInstruction(instruction)        
    # Ensure the instruction was actually read of a float
    opcode = instruction[:3]
    if instruction != "003":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["003"])
    # Read a float. If the read succeeds, push the float and then push true
    try:
        floating_point = float(input())
        push(floating_point)
        push(TRUE)
    # If the read failed push false        
    except ValueError:
        push(FALSE)

# Interpret and execute the reading of a string from standard input. If the read
# succeeds, the last character of the string will be pushed, then the second-to
# -last character, ..., then the first character, then a truthy value. If the
# read fails, a falsy value is pushed. "Pushing a character" means pushing the
# numerical value of the character. Unicode is supported. A string read
# has the format: 004
def read_string(instruction):
    # Ensure the instruction is 3 digits
    if re.match("$\d{3}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction was actually read a string
    opcode = instruction[:3]
    if instruction != "004":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["004"])
    # Read a string. If the read succeeds, push the characters, then push true
    try:
        string = input()
        # Traverse the string backwards and push each character
        for index in range(len(string) - 1, -1, -1):
            numeric_value = ord(string[index])
            push(numeric_value)
        push(TRUE)
    # If the read failed push false
    except:
        push(FALSE)

# Interpret and execute the printing of a float to standard output. No control
# over precision displayed is provided. If the stack is empty, this instruction
# has no effect. A float print has the format: 005
def print_float(instruction):
    # Ensure the instruction is 3 digits
    if re.match("$\d{3}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction was actually read a string
    opcode = instruction[:3]
    if instruction != "005":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["005"])
    # Try to pop the stack and print the value to standard output.
    if stack_is_empty():
        return
    floating_point = pop()
    print(floating_point, end="")

# Interpret and execute the printing of a char to standard output. Pop the top
# of the stack, truncate the float to be a true integer, then test to see if
# it is in the range of a valid Unicode char. If the integer corresponds to an
# Unicode value, print that character. If the stack is empty or the truncated
# float is not a valid Unicode char, this instruction does nothing. A print char
# instruction has the format: 006
def print_char(instruction):
    # Ensure the instruction is 3 digits
    if re.match("$\d{3}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction was actually print a char
    opcode = instruction[:3]
    if instruction != "006":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["006"])
    # Try to pop the stack and make the value into a Unicode char
    if stack_is_empty():
        return
    floating_point = pop()
    integer = int(floating_point)
    # Ensure integer is in range of valid Unicode chars, then print char.
    if 0 <= integer and integer <= 1114111:
        char = chr(integer)
        print(char, end="")
    # Otherwise do nothing

# Interpret and execute the declaration of a label at the current position in
# the program. A create label instruction has the format: 007dddddd, d = decimal
# digit
def create_label(instruction, statement_number):
    # Ensure the instruction is 9 digits
    if re.match("$\d{3}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction was actually create a label
    opcode = instruction[:3]
    if instruction != "007":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["007"])
    # Create a label with the six variable digits of the instruction as a name.
    # Overwrite any label that already exists at this point
    label_name = instruction[3:]
    labels[label_name] = statement_number
    
# Interpret and execute a conditional branching instruction. If the top of the
# stack is a truthy value, jump to the label specified in the instruction by
# returning the new value for the instruction pointer. If the top of the stack
# was falsy, the stack underflowed, or the top value was truthy but the branch
# was not defined, return -1.
# and return zero. Attempting to perform a branch to an undefined label results
# in no change to the instruction pointer and a return value of zero.
# A branch if equal instruction has the format: 008dddddd
def conditional_branch(instruction):
    # Ensure the instruction is 9 digits
    if re.match("$\d{9}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction was actually conditional branch
    opcode = instruction[:3]
    if instruction != "008":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["008"])
    # Try to pop the stack
    if stack_is_empty():
        return -1
    # Test the condition
    condition = pop()
    if not isTrue(condition):
        return -1
    # Read the label
    label = instruction[3:]
    # Ensure label exists
    if label not in labels:
        return -1
    # Return the new value for the instruction counter
    new_instruction_pointer = labels[label]
    return new_instruction_pointer

# Interpret and execute coercion of a float to 1 or 0. Pop the top of the stack.
# If abs(top) < .0001, push 0. If abs(top) >= .0001, push 1. If the stack
# underflows, do not push anything. A coerce_to_boolean instruction has the
# format: 009
def coerce_to_boolean(instruction):
    # Ensure the instruction is 3 digits
    if re.match("$\d{3}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction was actually coerce to boolean
    opcode = instruction[:3]
    if instruction != "009":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["009"])
    # Try to pop the stack
    if stack_is_empty():
        return
    # Coerce the value to a boolean
    floating_point = pop()
    boolean = abs(floating_point) >= 0.0001
    push(boolean)

# Interpret and execute a logical NOT. If the top of the stack is a truthy
# value, push 0, otherwise push 1. If the stack underflows, push nothing.
# A logical not instruction has the format: 010
def logical_not(instruction):
    # Ensure the instruction is 3 digits
    if re.match("$\d{3}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction was actually logical not
    opcode = instruction[:3]
    if instruction != "010":
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES["010"])
    # Try to pop the stack
    if stack_is_empty():
        return
    # Push the logical negation of the stack value
    operand = pop()
    if isTrue(operand):
        push(0.0)
    else:
        push(1.0)

# There are several logical comparisons that take two operands. This function
# abstracts these. Pop the top two values from the stack, then perform the
# binary_function passed in. Finally, push the function's result. If the stack
# underflows, push nothing. The format for all these instructions is simply:
# ddd, where ddd = the opcode of the instruction
def binary_operation(instruction, proper_opcode, binary_function):
    # Ensure the instruction is 3 digits
    if re.match("$\d{3}^", instruction) == None:
        raise InvalidMNInstruction(instruction)
    # Ensure the instruction has the proper opcode for this type of instruction
    opcode = instruction[:3]
    if instruction != proper_opcode:
        raise MisinterpretedInstruction(OPCODES[opcode], OPCODES[proper_opcode])
    # Try to pop the stack twice
    if stack_is_empty():
        return
    operand_1 = pop()
    if stack_is_empty():
        return
    operand_2 = pop()
    # Push the result of the binary operation
    push(binary_function(operand_1, operand_2))

# Interpret and execute a logical AND. If the top two values of the stack are
# both true, push 1, otherwise push 0. If the stack underflows, push nothing. A
# logical and instruction has the format: 011
def logical_and(instruction):
    and_function = lambda a, b: 1.0 if isTrue(a) and isTrue(b) else 0.0
    binary_comparison(instruction, "011", and_function)
    
# Interpret and execute a logical OR. If either of the top two values of the
# stack are true, push 1, otherwise push 0. If the stack underflows, push
# nothing. A logical or instruction has the format: 012
def logical_or(instruction):
    or_function = lambda a, b: 1.0 if isTrue(a) or isTrue(b) else 0.0
    binary_comparison(instruction, "012", or_function)
    
# Interpret and execute a comparison. If the top of the stack is less than the
# second-highest value of the stack, push 1, otherwise push 0. If the stack
# underflows, push nothing. A logical less than instruction has the format: 013
def less_than(instruction):
    less_than_function = lambda a, b: 1.0 if a < b else 0.0
    binary_comparison(instruction, "013", less_than_function)

# Interpret and execute a comparison. If the top of the stack is greater than
# the second-highest value of the stack, push 1, otherwise push 0. If the stack
# underflows, push nothing. A logical greater than instruction has the format:
# 014
def greater_than(instruction):
    greater_than_function = lambda a, b: 1.0 if a > b else 0.0
    binary_comparison(instruction, "014", greater_than_function)

# Interpret and execute a comparison.
# If the abs(top of stack - second-highest value of stack) < 0.0001, push 1,
# otherwise push 0. If the stack underflows, push nothing. The format for an
# equality instruction is: 015
def equal(instruction):
    equality_function = lambda a, b: 1.0 if abs(a - b) < 0.0001 else 0.0
    binary_comparison(instruction, "015", equality_function)

# Interpret and execute floating point addition. Pop the top two values of the
# stack and push the sum. If the stack underflows, push nothing. The format for
# an addition instruction is: 016
def add(instruction):
    addition_function = lambda a, b: a + b
    binary_comparison(instruction, "016", addition_function)

# Interpret and execute floating point subtraction. The second highest value on
# the stack is subtracted from the highest value on the stack, and the result is
# pushed. If the stack underflows, push nothing. The format of a subtraction
# instruction is: 017
def subtract(instruction):
    subtraction_function = lambda a, b: a - b
    binary_comparison(instruction, "017", subtraction_function)

# Interpret and execute floating point multiplication. Pop the top two values of
# the stack and push the product. If the stack underflows, push nothing. The
# format of a multiplication instruction is: 018
def multiply(instruction):
    multiplication_function = lambda a, b: a * b
    binary_comparison(instruction, "018", multiplication_function)

# Interpret and execute floating point division. The highest value on the stack
# is divided by the second-highest value on the stack. If the division raises an
# exception or the stack underflows, push nothing.
def divide(instruction):
    division_function = lambda a, b: a / b
    try:
        binary_comparision(instruction, "019", division_function)
    # Swallow exceptions
    except:
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

# A lookup table matching opcodes to the Python functions that handle them
FUNCTIONS = {"001" : push_integer, "002" : push_float, "003" : read_float, \
             "004" : read_string, "005" : print_float, "006": print_char, \
             "007" : create_label, "008" : conditional_branch, \
             "009" : coerce_to_boolean, "010" : logical_not, "011" : \
             logical_and, "012" : logical_or, "013" : less_than, "014" : \
             greater_than, "015" : equal, "016" : add, "017" : subtract, \
             "018" : multiply, "019" : divide}

# Read a source file
source = load_MN_file("kitbash.magic")
# Parse the file's contents
program_statements = parse_MN_program_source(source)
# Declare labels
declare_MN_labels(program_statements)
# Execute the program
execute_MN_program(program_statements)
