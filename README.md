# Magic Number

Magic Number is a simple, human-readable, procedural, stack-based esolang where a program's source code consists of a single unsigned integer.

## Mechanics
The stack stores exclusively floats. Instructions which necessarily operate on integers truncate operands to integers as necessary. Instructions which push a boolean push 1.0 for true and 0.0 for false. However, instructions which operate on booleans consider anything different from zero by at least 0.0001 to be true and anything else to be false.

Before interpreting a program, all non-digits are stripped from the program's source. Thus, comments and whitespace can be added, just not stray digits. Magic Number strives to fail silently, although currently this goal is only partially met. It is not an error for the stack to underflow; execution continues normally. Using the `--debug` flag is highly encouraged.

## Instructions

### Stack manipulation

#### Push integer
Format: 001sdddddd where s is 0 to denote non-negative and s is 1 to denote negative, dddddd is the integer to push.
Notes: The value pushed is always a float. This instruction is simply for convenience.

#### Push float
Format: 002deesmmmmmm where d is 0 to denote non-negative exponent and d is 1 to denote a negative exponent, ee is the scientific-notation exponent, s is 0 to denote a non-negative value and s is 1 to denote a negative value, and mmmmmm is an integer specifiying the "mantissa"

#### Pop stack
Format: 020
Notes: Discard the top value of the stack.

#### Duplicate top
Format: 021
Notes: Pop the top value of the stack and push it twice.

### IO

#### Read float
Format: 003
Notes: Reads a line of input from the user, converts to a float, and pushes the float onto the stack. Also pushes a 1.0 on top of the input if the read succeeds and a 0.0 if the read fails.

#### Read string
Format: 004
Notes: Reads a line of input from the user and pushes the numerical value of each character onto the stack in reverse order, so the start of the string is on top of the stack. Also pushes a 1.0 top on top of the stack at the end if the read succeeds and a 0.0 if the read fails. Unicode is supported.

#### Print float
Format: 005
Notes: Pop the stack and print the value. No control over formatting is provided.

#### Print char
Format: 006
Notes: Pop the stack, truncate to integer, if integer is a valid Unicode value, print the character, otherwise print nothing.

### Control flow

#### Declare label
Format: 007dddddd where dddddd serves as the identifier for the label.

#### Conditional branch
Format: 008dddddd where dddddd is the identifier for the label to branch to.
Notes: Pops the stack, if value is "true", next instruction is the one following wherever the label dddddd was declared. If value is false, stack underflows, or the label does not exist, execution falls through.

### Logic

#### Truthy Values
If |value| < .0001, the value is considered false, otherwise it is considered true.

#### Coerce to boolean
Format: 009
Notes: Pops the stack, if the value is true, push 1.0, otherwise push 0.0.

#### Logical Not
Format: 010
Notes: Pops the stack, if the value is true, push 0.0, otherwise push 1.0.

#### Logical And
Format: 011
Notes: Pops the stack twice, if both values are true, push 1.0, otherwise push 0.0.

#### Logical Or
Format: 012
Notes: Pops the stack twice, if either value is true, push 1.0, otherwise push 0.0.

#### Logical Less Than
Format: 013
Notes: Pop the stack twice. If the first value popped is less than the second value popped, push 1.0, otherwise push 0.0.

#### Logical Greater Than
Format: 014
Notes: Pop the stack twice. If the first value popped is greater than the second value popped, push 1.0, otherwise push 0.0.

#### Logical Equal
Format: 015
Notes: Pop the stack twice. If |first value - second value| < 0.0001, push 1.0, otherwise push 0.0.

### Arithmetic

#### Addition
Format: 016
Notes: Pop the stack twice, add the two values, then push the result.

#### Subtraction
Format: 017
Notes: Pop the stack twice, subtract the second value from the first value, then push the result.

#### Multiply
Format: 018
Notes: Pop the stack twice, multiply the two values, then push the result.

#### Division
Format: 019
Notes: Pop the stack twice, divide the first value by the second value, then push the result. If a divide-by-zero exception occurs, swallow the exception and push no result.

#### Remainder
Format: 022
Notes: Pop the stack twice, truncate both to integers, take the remainder of the first value divided by the second, then push that remainder. If an exception occurs, swallow the exception and push no result.