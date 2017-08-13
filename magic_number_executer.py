#!/bin/python3

import re
import copy
import sys

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
           "multiplication", "019" : "division", "020" : "pop", "021" : \
           "duplicate", "022" : "remainder"}

# A lookup table mapping opcodes to the fixed length of the instruction they
# specify. Instruction lengths include the opcode.
INSTRUCTION_LENGTHS = {"001" : 10, "002" : 13, "003" : 3, "004" : 3, "005" : 3,\
                       "006" : 3, "007" : 9, "008" : 9, "009" : 3, "010" : 3, \
                       "011" : 3, "012" : 3, "013" : 3, "014" : 3, "015" : 3, \
                       "016" : 3, "017" : 3, "018" : 3, "019" : 3, "020" : 3, \
                       "021" : 3, "022" : 3}

# Any value different from zero by at least 0.0001 is considered true, but for
# convenience and the result of operations, 1 is used to indicate true.
TRUE = 1.0

# Any value different from zero by less than 0.0001 is considered false, but for
# convenience and the result of operations, 0 is used to indicate false.
FALSE = 0.0

# Convenience function to test if a float is considered true
def isTrue(floating_point):
    return abs(floating_point) >= 0.0001

# If debug mode is enabled via a command-line flag, debugging information is
# displayed when the MN program completes
debug = False

# If scripting mode is enabled via an argument to `run_interpreter_from_python`,
# then `input()` takes the next element from scripted_input instead of from
# standard input
scripting = False

# A list of every instruction executed, in the order in which they were executed.
# This list is used only if `debug` is true.
instruction_trace = []

# A list containing a copy of the stack after every instruction was executed in
# order. This is only used if `debug` is true.
stack_history = []

# A string containing all output to standard output during program execution.
# This is only used if `debug` is true.
printed_output = ""

# A list containing lines to be used as input in place of standard in. This list
# is only used if `scripting` is true. If an attempt is made to take input
# from the list when it is empty that is an error for the MN program. This is
# meant to be used only to facilitate unit testing
scripted_input = []

# Note the execution of an instruction if debugging is on.
def record_debugging_information(instruction):
    if debug:
        instruction_trace.append(instruction)
        stack_history.append(copy.deepcopy(stack))

# Append a copy of text being sent to standard output if debugging is enabled.
def record_standard_output(recordand):
    global printed_output
    if debug:
        printed_output += recordand

# Get the next line of input. If `scripting` is true, take the line from the
# preset list of input, otherwise, read a line from standard in. If preset input
# is needed but no more is available, that is an error for the MN program.
def get_next_input_line():
    # If scripting, retrieve next preset input and remove it from the list
    if scripting:
        # Ensure there is more input to read, otherwise fail
        if len(scripted_input) == 0:
            raise OutOfScriptedInputException()
        input_line = scripted_input.pop(0)
    # Just read and return a line from standard input
    else:
        input_line = input()
    return input_line

# Reset the state of the interpreter.
def reset_interpreter():
    global stack
    global labels
    global instruction_trace
    global stack_history
    global printed_output
    global debug
    global scripted
    global scripted_input
    stack = []
    labels = {}
    instruction_trace = []
    debug = False
    stack_history = []
    printed_output = ""
    scripted = False
    scripted_input = []
        
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
        instruction = program_source[index : index + \
                                     INSTRUCTION_LENGTHS[opcode]]
        program_statements.append(instruction)
        index += len(instruction)
    return program_statements

# Iterate through the statements in an MN program and declare all the labels
def declare_MN_labels(program_statements):
    for statement_number in range(len(program_statements)):
        # Get the current instruction and its opcode
        instruction = program_statements[statement_number]
        opcode = instruction[:3]
        # If the opcode is 007 "create label", mark the statement as a label
        if opcode == "007":
            create_label(instruction, statement_number)
            record_debugging_information(instruction)
            
# Execute a MN program. Iterate through the list of program statements executing
# each sequentially, changing the instruction pointer appropriately as the
# result of branches.
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
            # Even no-ops are recorded for debugging purposes
            record_debugging_information(instruction)
            instruction_pointer += 1
        # Handle the special case of a conditional branch
        elif opcode == "008":
            new_instruction_pointer = conditional_branch(instruction)
            record_debugging_information(instruction)
            if new_instruction_pointer != -1:
                instruction_pointer = new_instruction_pointer
            else:
                instruction_pointer += 1
        # "create label" is a no-op here; it is done prior to program execution
        else:
            instruction_pointer += 1

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
        raise StackUnderflowException()
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
    if re.match("^\d{10}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction was actually an integer push
    opcode = instruction[:3]
    if opcode != "001":
        raise MisinterpretedInstructionException(OPCODES[opcode], \
                                                 OPCODES["001"])
    # Ensure the sign is valid
    sign = instruction[3]
    if sign != "0" and sign != "1":
        raise InvalidMNInstructionException(instruction)
    sign_multiplier = 1 if sign == "0" else -1
    # Parse the integer and push it onto the stack
    integer = sign_multiplier * int(instruction[4:])
    push(float(integer))

# Interpret and execute a push of a floating point constant. A floating point
# push has the format: 002deesmmmmmm, d = 0 -> positive exponent, d = 1 ->
# negative exponent, e = decimal digit of exponent, s = 0 -> positive mantissa,
# s = 1 -> negative mantiss, m = decimal digit of mantissa
# Example: 0021021000002 is -2e-2 == -.02
def push_float(instruction):
    # Ensure the instruction is 13 digits
    if re.match("^\d{13}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction was actually a push of a float
    opcode = instruction[:3]
    if opcode != "002":
        raise MisinterpretedInstructionException(OPCODES[opcode],OPCODES["002"])
    # Ensure the signs of the exponent and mantissa are valid
    exponent_sign = instruction[3]
    mantissa_sign = instruction[6]
    if exponent_sign != "0" and exponent_sign != "1" and \
       mantissa_sign != "0" and mantissa_sign != "1":
        raise InvalidMNInstructionException(instruction)
    exponent_multiplier = 1 if exponent_sign == "0" else -1
    mantissa_multiplier = 1 if mantissa_sign == "0" else -1
    # Parse the float and push it onto the stack
    exponent = exponent_multiplier * int(instruction[4:6])    
    mantissa = mantissa_multiplier * int(instruction[7:13])
    floating_point = float(mantissa * 10 ** exponent)
    push(floating_point)

# Interpret and execute a pop of the stack meant to discard an item. If the
# stack underflows, do nothing. The format for a pop instruction is: 020
def pop_discard(instruction):
    # Ensure the instruction is 3 digits
    if re.match("^\d{3}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)        
    # Ensure the instruction was actually pop
    opcode = instruction[:3]
    if opcode != "020":
        raise MisinterpretedInstructionException(OPCODES[opcode],OPCODES["020"])
    # Ensure stack is not empty
    if stack_is_empty():
        return
    # Pop the top element and discard it
    pop()

# Interpret and execute a duplication of the top element of the stack. Pop the
# top of the stack, then push that popped value onto the stack twice. If the
# stack underflows, push nothing. The format for a duplication instruction is:
# 021
def duplicate(instruction):
    # Ensure the instruction is 3 digits
    if re.match("^\d{3}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)        
    # Ensure the instruction was actually duplicate
    opcode = instruction[:3]
    if opcode != "021":
        raise MisinterpretedInstructionException(OPCODES[opcode],OPCODES["021"])
    # Ensure stack is not empty
    if stack_is_empty():
        return
    # Pop the top element and push it back twice
    floating_point = pop()
    push(floating_point)
    push(floating_point)
    
# Interpret and execute the reading of a float from standard input, to be put
# onto the stack. If the read succeeds, a truthy value is placed onto the stack
# on top of the float. If the read fails, only a falsy value is added to the
# stack. A floating point read has the format: 003
def read_float(instruction):
    # Ensure the instruction is 3 digits
    if re.match("^\d{3}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)        
    # Ensure the instruction was actually read of a float
    opcode = instruction[:3]
    if opcode != "003":
        raise MisinterpretedInstructionException(OPCODES[opcode], OPCODES["003"])
    # Read a float. If the read succeeds, push the float and then push true
    try:
        floating_point = float(get_next_input_line())
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
    if re.match("^\d{3}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction was actually read a string
    opcode = instruction[:3]
    if opcode != "004":
        raise MisinterpretedInstructionException(OPCODES[opcode], OPCODES["004"])
    # Read a string. If the read succeeds, push the characters, then push true
    try:
        string = get_next_input_line()
        # Traverse the string backwards and push each character
        for index in range(len(string) - 1, -1, -1):
            numeric_value = float(ord(string[index]))
            push(numeric_value)
        push(TRUE)
    # If the read failed push false
    except:
        push(FALSE)

# Interpret and execute the printing of a float to standard output. No control
# over precision displayed is provided. If the stack is empty, this instruction
# has no effect. A print float instruction has the format: 005
def print_float(instruction):
    # Ensure the instruction is 3 digits
    if re.match("^\d{3}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction was actually print a float
    opcode = instruction[:3]
    if opcode != "005":
        raise MisinterpretedInstructionException(OPCODES[opcode], OPCODES["005"])
    # Try to pop the stack and print the value to standard output.
    if stack_is_empty():
        return
    floating_point = pop()
    output = str(floating_point)
    record_standard_output(output)
    print(output, end="")

# Interpret and execute the printing of a char to standard output. Pop the top
# of the stack, truncate the float to be a true integer, then test to see if
# it is in the range of a valid Unicode char. If the integer corresponds to an
# Unicode value, print that character. If the stack is empty or the truncated
# float is not a valid Unicode char, this instruction does nothing. A print char
# instruction has the format: 006
def print_char(instruction):
    # Ensure the instruction is 3 digits
    if re.match("^\d{3}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction was actually print a char
    opcode = instruction[:3]
    if opcode != "006":
        raise MisinterpretedInstructionException(OPCODES[opcode], OPCODES["006"])
    # Try to pop the stack and make the value into a Unicode char
    if stack_is_empty():
        return
    floating_point = pop()
    integer = int(floating_point)
    # Ensure integer is in range of valid Unicode chars, then print char.
    if 0 <= integer and integer <= 1114111:
        char = chr(integer)
        record_standard_output(char)
        print(char, end="")
    # Otherwise do nothing

# Interpret and execute the declaration of a label at the current position in
# the program. Create labe instructions are interpreted before runtime and
# ignored during runtime. A create label instruction has the format: 007dddddd,
# d = decimal digit of label name
def create_label(instruction, statement_number):
    # Ensure the instruction is 9 digits
    if re.match("^\d{9}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction was actually create a label
    opcode = instruction[:3]
    if opcode != "007":
        print("\"" + instruction + "\"")
        raise MisinterpretedInstructionException(OPCODES[opcode], OPCODES["007"])
    # Create a label with the six variable digits of the instruction as a name.
    label_name = instruction[3:]
    labels[label_name] = statement_number
    
# Interpret and execute a conditional branching instruction. If the top of the
# stack is a truthy value, jump to the label specified in the instruction by
# returning the new value for the instruction pointer. If the top of the stack
# was falsy, the stack underflowed, or the top value was truthy but the branch
# was not defined, return -1.  A branch if equal instruction has the format:
# 008dddddd, d = decimal digit of label name
def conditional_branch(instruction):
    # Ensure the instruction is 9 digits
    if re.match("^\d{9}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction was actually conditional branch
    opcode = instruction[:3]
    if opcode != "008":
        raise MisinterpretedInstructionException(OPCODES[opcode], OPCODES["008"])
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
    if re.match("^\d{3}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction was actually coerce to boolean
    opcode = instruction[:3]
    if opcode != "009":
        raise MisinterpretedInstructionException(OPCODES[opcode], OPCODES["009"])
    # Try to pop the stack
    if stack_is_empty():
        return
    # Coerce the value to a boolean
    floating_point = pop()
    boolean = TRUE if isTrue(floating_point) else FALSE
    push(boolean)

# Interpret and execute a logical NOT. If the top of the stack is a truthy
# value, push 0, otherwise push 1. If the stack underflows, push nothing.
# A logical not instruction has the format: 010
def logical_not(instruction):
    # Ensure the instruction is 3 digits
    if re.match("^\d{3}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction was actually logical not
    opcode = instruction[:3]
    if opcode != "010":
        raise MisinterpretedInstructionException(OPCODES[opcode], OPCODES["010"])
    # Try to pop the stack
    if stack_is_empty():
        return
    # Push the logical negation of the stack value
    operand = pop()
    if isTrue(operand):
        push(FALSE)
    else:
        push(TRUE)

# There are several binary operations that take two operands. This function
# abstracts these. Pop the top two values from the stack, then perform the
# binary_function passed in. Finally, push the function's result. If the stack
# underflows, push nothing. The format for all these instructions is simply:
# ddd, where ddd = the opcode of the instruction
def binary_operation(instruction, proper_opcode, binary_function):
    # Ensure the instruction is 3 digits
    if re.match("^\d{3}$", instruction) == None:
        raise InvalidMNInstructionException(instruction)
    # Ensure the instruction has the proper opcode for this type of instruction
    opcode = instruction[:3]
    if instruction != proper_opcode:
        raise MisinterpretedInstructionException(OPCODES[opcode], OPCODES[proper_opcode])
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
    and_function = lambda a, b: TRUE if isTrue(a) and isTrue(b) else FALSE
    binary_operation(instruction, "011", and_function)
    
# Interpret and execute a logical OR. If either of the top two values of the
# stack are true, push 1, otherwise push 0. If the stack underflows, push
# nothing. A logical or instruction has the format: 012
def logical_or(instruction):
    or_function = lambda a, b: TRUE if isTrue(a) or isTrue(b) else FALSE
    binary_operation(instruction, "012", or_function)
    
# Interpret and execute a comparison. If the top of the stack is less than the
# second-highest value of the stack, push 1, otherwise push 0. If the stack
# underflows, push nothing. A logical less than instruction has the format: 013
def less_than(instruction):
    less_than_function = lambda a, b: TRUE if a < b else FALSE
    binary_operation(instruction, "013", less_than_function)

# Interpret and execute a comparison. If the top of the stack is greater than
# the second-highest value of the stack, push 1, otherwise push 0. If the stack
# underflows, push nothing. A logical greater than instruction has the format:
# 014
def greater_than(instruction):
    greater_than_function = lambda a, b: TRUE if a > b else FALSE
    binary_operation(instruction, "014", greater_than_function)

# Interpret and execute a comparison.
# If the abs(top of stack - second-highest value of stack) < 0.0001, push 1,
# otherwise push 0. If the stack underflows, push nothing. The format for an
# equality instruction is: 015
def equal(instruction):
    equality_function = lambda a, b: TRUE if abs(a - b) < 0.0001 else FALSE
    binary_operation(instruction, "015", equality_function)

# Interpret and execute floating point addition. Pop the top two values of the
# stack and push the sum. If the stack underflows, push nothing. The format for
# an addition instruction is: 016
def add(instruction):
    addition_function = lambda a, b: a + b
    binary_operation(instruction, "016", addition_function)

# Interpret and execute floating point subtraction. The second highest value on
# the stack is subtracted from the highest value on the stack, and the result is
# pushed. If the stack underflows, push nothing. The format of a subtraction
# instruction is: 017
def subtract(instruction):
    subtraction_function = lambda a, b: a - b
    binary_operation(instruction, "017", subtraction_function)

# Interpret and execute floating point multiplication. Pop the top two values of
# the stack and push the product. If the stack underflows, push nothing. The
# format of a multiplication instruction is: 018
def multiply(instruction):
    multiplication_function = lambda a, b: a * b
    binary_operation(instruction, "018", multiplication_function)

# Interpret and execute floating point division. The highest value on the stack
# is divided by the second-highest value on the stack. If the division raises an
# exception or the stack underflows, push nothing. The format for the division
# operation is: 019
def divide(instruction):
    division_function = lambda a, b: a / b
    try:
        binary_operation(instruction, "019", division_function)
    # Swallow exceptions
    except:
        pass

# Interpret and execute the remainder operator. The highest value on the stack,
# trucated to an integer, is divided by the second-highest value on the stack,
# truncated to an integer. The remainder is pushed onto the stack. If the
# operation raises an exception, push nothing. The format for the remainder
# operation is: 022
def remainder(instruction):
    remainder_function = lambda a, b: float(int(a) % int(b))
    try:
        binary_operation(instruction, "022", remainder_function)
    # Swallow exceptions
    except:
        pass

# Simple custom exception signifying underflow of the MN program's stack
class StackUnderflowException(BaseException):
    def __init__(self, message):
        self.message = "Magic Number Executer attempted to underflow the" + \
                       " stack. Although this is caused by the MN program," + \
                       "the exception should have been handled internally."

# Simple custom exception signifying that the format of an instruction being
# executed is invalid.
class InvalidMNInstructionException(BaseException):
    def __init__(self, instruction):
        self.message = "Magic Number Executer encountered an instruction " + \
                       "which was invalid: {}. Although this is caused by " + \
                       "the MN program, the exception should have been " + \
                       "gracefully treated as a no-op.".format(instruction)

# Simple custom exception signifying that the opcode of an instruction passed to
# a function meant to execute a specific type of instruction is the opcode for a
# different instruction, eg add() is passed a subtract instruction.
class MisinterpretedInstructionException(BaseException):
    def __init__(self, actual, intended):
        self.message = "Magic Number Executer misinterpreted {} as {}. " + \
                       "This is an internal error.".format(actual, intended)

# Simple custom exception signifiying that there is no more preset input
# available for the program to read, but more was requested. This can occur
# only when `scripting` is true, such as during unit testing.
class OutOfScriptedInputException(BaseException):
    def __init__(self):
        self.message = "Magic Number Executer has no more scripted input, " + \
                       "but program is attempting a read."

# A lookup table matching opcodes to the Python functions that handle them
FUNCTIONS = {"001" : push_integer, "002" : push_float, "003" : read_float, \
             "004" : read_string, "005" : print_float, "006": print_char, \
             "007" : create_label, "008" : conditional_branch, \
             "009" : coerce_to_boolean, "010" : logical_not, "011" : \
             logical_and, "012" : logical_or, "013" : less_than, "014" : \
             greater_than, "015" : equal, "016" : add, "017" : subtract, \
             "018" : multiply, "019" : divide, "020" : pop_discard, "021" : \
             duplicate, "022" : remainder}

# Run the Magic Number interpreter using the command line arguments or arguments
# from another source.
def run_interpreter_from_cli(arguments):
    # Ensure a program file was passed in
    if len(arguments) != 2 and len(arguments) != 3 or len(arguments) == 3 and \
       arguments[1] != "--debug":
        print("Usage: ./magic_number_executer.py [--debug] program_file.magic")
        sys.exit(1)
    # Set the debug flag conditionally
    is_debugging = arguments[1] == "--debug"
    # Read a source file
    source = load_MN_file(arguments[len(arguments) - 1])
    # Execute the files contents, passing the debug flag
    run_interpreter_from_python(source, is_debugging)

# Run the Magic Number interpreter, taking as input the string source code and
# the desired value of the debugging flag.
def run_interpreter_from_python(program_source, is_debugging, \
                                is_scripting = False, preset_input = []):
    global debug
    global scripting
    global scripted_input
    # Ensure the state of the program is clean
    reset_interpreter()
    # Set debugging and testing variables
    debug = is_debugging
    scripting = is_scripting
    scripted_input = preset_input
    # Parse the file's contents
    program_statements = parse_MN_program_source(program_source)
    # Declare labels
    declare_MN_labels(program_statements)
    # Execute the program
    execute_MN_program(program_statements)
    # Print debugging information if requested
    if debug:
        print("Program execution terminated\n" + "-"*28)
        print("Standard output:\n\"" + printed_output + "\"")
        for index in range(len(instruction_trace)):
            print("{:<16} {}".format(instruction_trace[index], \
                                     str(stack_history[index])))

# Only start the interpreter if the program is invoked directly
if __name__ == "__main__":
    run_interpreter_from_cli(sys.argv)
