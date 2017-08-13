# Some tests for the Magic Number interpreter.

import magic_number_executer as MNE
import unittest

# Ensure that the stack contains the proper values after executing various
# instructions.
class StackTesting(unittest.TestCase):
    def test_stack_cleanliness(self):
        """Test basic push/pop with stack."""
        MNE.run_interpreter_from_cli(["", "--debug", "hello_world.magic"])
        self.assertEqual(MNE.stack, [])
    def test_push_integer_0(self):
        """Test push integer 0"""
        MNE.run_interpreter_from_python("0010000000", True)
        self.assertEqual(MNE.stack, [0])
    def test_push_integer_999999(self):
        """Test push integer 999999"""
        MNE.run_interpreter_from_python("0010999999", True)
        self.assertEqual(MNE.stack, [999999.0])
    def test_push_integer_negative_7669(self):
        """Test push integer 7669"""
        MNE.run_interpreter_from_python("0011007669", True)
        self.assertEqual(MNE.stack, [-7669.0])
    def test_push_float_0(self):
        """Test push float 0"""
        MNE.run_interpreter_from_python("0020000000000" + "0021000000000" + \
                                        "0020100000000" + "0021100000000", True)
        self.assertAlmostEqual(MNE.stack, [0.0] * 4)
    def test_push_float_minus_0_123456(self):
        """Test push float -0.123456"""
        MNE.run_interpreter_from_python("0021061123456", True)
        self.assertAlmostEqual(MNE.stack, [-.123456])
    def test_push_float_123456e99(self):
        """Test push float 123456e99"""
        MNE.run_interpreter_from_python("0020990123456", True)
        self.assertAlmostEqual(MNE.stack, [123456e99])
    def test_push_float_100(self):
        """Test push float 10000e-2"""
        MNE.run_interpreter_from_python("0021020010000", True)
        self.assertAlmostEqual(MNE.stack, [100.0])
    def test_push_float_1e_minus_99(self):
        """Test push float 1e-99"""
        MNE.run_interpreter_from_python("0021990000001", True)
        self.assertAlmostEqual(MNE.stack[0] * 1e99, 1.0)
    def test_push_pop(self):
        """Test integer push followed by vanilla pop"""
        MNE.run_interpreter_from_python("0010000001020", True)
        self.assertEqual(MNE.stack, [])
    def test_pop_stack_underflow(self):
        """Test that stack underflow due to popping is handled safely"""
        MNE.run_interpreter_from_python("020", True)

class IOTesting(unittest.TestCase):
    def test_read_float_0(self):
        """Test read float "0" """
        MNE.run_interpreter_from_python("003", True, True, ["0"])
        self.assertAlmostEqual(MNE.stack, [0.0, 1.0])
    def test_read_float_3_14159(self):
        """Test read float "3.14159" """
        MNE.run_interpreter_from_python("003", True, True, ["3.14159"])
        self.assertAlmostEqual(MNE.stack, [3.14159, 1.0])
    def test_read_float_minus_1e99(self):
        """Test read float "-1e99" """
        MNE.run_interpreter_from_python("003", True, True, ["-1e99"])
        self.assertAlmostEqual(MNE.stack, [-1e99, 1.0])
    def test_read_float_failure(self):
        """Test read float "cheeseburger" """
        MNE.run_interpreter_from_python("003", True, True, ["cheeseburger"])
        self.assertAlmostEqual(MNE.stack, [0.0])
    def test_read_string_empty(self):
        """Test reading an empty string"""
        MNE.run_interpreter_from_python("004", True, True, [""])
        self.assertAlmostEqual(MNE.stack, [1.0])
    def test_read_string_hello_world(self):
        """Test read string "Hello, world!" """
        MNE.run_interpreter_from_python("004", True, True, ["Hello, world!"])
        self.assertAlmostEqual(MNE.stack, [33., 100., 108., 114., 111., 119., \
                               32., 44., 111., 108., 108., 101., 72., 1.])
    def test_read_string_unicode(self):
        """Test reading string with a unicode character"""
        MNE.run_interpreter_from_python("004", True, True, ["¯\_(ツ)_/¯"])
        self.assertAlmostEqual(MNE.stack, [175., 47., 95., 41., 12484., 40., \
                                           95., 92., 175., 1.])
    def test_print_float_0(self):
        """Test printing the float 0"""
        MNE.run_interpreter_from_python("0010000000005", True)
        self.assertAlmostEqual(float(MNE.printed_output), 0.0)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_print_float_minus_1(self):
        """Test printing the float -1"""
        MNE.run_interpreter_from_python("0011000001005", True)
        self.assertAlmostEqual(float(MNE.printed_output), -1.0)
        self.assertEqual(MNE.printed_output, "-1.0")
    def test_print_float_3_14159(self):
        """Test printing the float 3.14159"""
        MNE.run_interpreter_from_python("0021050314159005", True)
        self.assertAlmostEqual(float(MNE.printed_output), 3.14159)
        self.assertEqual(MNE.printed_output, "3.1415900000000003")
    def test_print_float_minus_1e_minus_99(self):
        """Test printing the float -1e-99"""
        MNE.run_interpreter_from_python("0021991000001005", True)
        self.assertAlmostEqual(float(MNE.printed_output), -1e-99)
        self.assertEqual(MNE.printed_output, "-1e-99")
    def test_print_float_1234e99(self):
        """Test printing the float 1234e99"""
        MNE.run_interpreter_from_python("0020990001234005", True)
        self.assertAlmostEqual(float(MNE.printed_output), 1234e99)
        self.assertEqual(MNE.printed_output, "1.234e+102")
    def test_print_char_hello(self):
        """Test print the characters in "Hello!" """
        MNE.run_interpreter_from_python("004020006006006006006006", True, \
                                        True, ["Hello!"])
        self.assertEqual(MNE.printed_output, "Hello!")
    def test_print_char_noisy(self):
        """Test print the characters in "cat" with noise added"""
        MNE.run_interpreter_from_python("00210100011650021020009799" + \
                                        "0021040991234006006006", True)
        self.assertEqual(MNE.printed_output, "cat")
    def test_print_char_unicode(self):
        """Test print the characters in "¯\_(ツ)_/¯", which has Unicode"""
        MNE.run_interpreter_from_python("004020006006006006006006006006006", \
                                        True, True, ["¯\_(ツ)_/¯"])
        self.assertEqual(MNE.printed_output, "¯\_(ツ)_/¯")
    def test_print_char_too_large(self):
        """Test printing a char whose numeric value is too large"""
        MNE.run_interpreter_from_python("0020990123456006", True)
    def test_print_char_too_small(self):
        """Test printing a char whose numeric value is too small"""
        MNE.run_interpreter_from_python("0020991123456006", True)

class ControlFlowTesting(unittest.TestCase):
    def test_simple_loop(self):
        """Test a simple loop counting from 10 to 1"""
        MNE.run_interpreter_from_python("00100000100070000000210050010000010" +\
                                        "0060011000001016021008000000", True)
        self.assertEqual(MNE.printed_output, "10.0\n9.0\n8.0\n7.0\n6.0\n5.0" + \
                         "\n4.0\n3.0\n2.0\n1.0\n")
    def test_declare_unused_label(self):
        """Test declaration of an unused label"""
        MNE.run_interpreter_from_python("0071234560010007669005", True)
        self.assertEqual(MNE.printed_output, "7669.0")
    def test_branch_undeclared_lable(self):
        """Test branch to nonexistant label"""
        MNE.run_interpreter_from_python("0010000001008123456", True)

class BooleanTesting(unittest.TestCase):
    def test_coerce_to_boolean_3_14159(self):
        """Test coerce to boolean on 3.14159"""
        MNE.run_interpreter_from_python("0021050314159009005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_coerce_to_boolean_0_0001(self):
        """Test coerce to boolean on 0.0001, the least positive true value"""
        MNE.run_interpreter_from_python("0021040000001009005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_coerce_to_boolean_0_0000999999(self):
        """Test coerce to boolean on a positive value which is barely false"""
        MNE.run_interpreter_from_python("0021100999999009005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_coerce_to_boolean_minus_0_0000999999(self):
        """Test coerce to boolean on a negative value which is barely false"""
        MNE.run_interpreter_from_python("0021101999999009005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_coerce_to_boolean_minus_0_0001(self):
        """Test coerce to boolean on -0.0001, the highest negative true value"""
        MNE.run_interpreter_from_python("0021041000001009005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_logical_not_0_0001(self):
        """Test logical not on 0.0001, the least positive true value"""
        MNE.run_interpreter_from_python("0021040000001010005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_logical_not_0_0000999999(self):
        """Test logical not on a positive value which is barely false"""
        MNE.run_interpreter_from_python("0021100999999010005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_logical_not_minus_0_0000999999(self):
        """Test logical not on a negative value which is barely false"""
        MNE.run_interpreter_from_python("0021101999999010005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_logical_not_minus_0_001(self):
        """Test logical not on -0.0001, the highest negative true value"""
        MNE.run_interpreter_from_python("0021040000001010005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_and_false_false(self):
        """Test AND by ANDing two false values"""
        MNE.run_interpreter_from_python("00100000000010000000011005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_and_false_true(self):
        """Test AND by ANDing false and true"""
        MNE.run_interpreter_from_python("00100000010010000000011005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_and_true_false(self):
        """Test AND by ANDing true and false"""
        MNE.run_interpreter_from_python("00100000000010000001011005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_and_true_true(self):
        """Test AND by ANDing true and true"""
        MNE.run_interpreter_from_python("00100000010010000001011005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_or_false_false(self):
        """Test OR by ORing false and false"""
        MNE.run_interpreter_from_python("00100000000010000000012005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_or_false_true(self):
        """Test OR by ORing false and true"""
        MNE.run_interpreter_from_python("00100000010010000000012005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_or_true_false(self):
        """Test OR by ORing true and false"""
        MNE.run_interpreter_from_python("00100000000010000001012005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_or_true_true(self):
        """Test OR by ORing true and true"""
        MNE.run_interpreter_from_python("00100000010010000001012005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_less_than_minus_1_1(self):
        """Test less than with -1 < 1"""
        MNE.run_interpreter_from_python("00100000010011000001013005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_less_than_1_1(self):
        """Test less than with 1 < 1"""
        MNE.run_interpreter_from_python("00100000010010000001013005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_less_than_1_minus_1(self):
        """Test less than with 1 < -1"""
        MNE.run_interpreter_from_python("00110000010010000001013005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_greater_than_minus_1_1(self):
        """Test greater than with -1 > 1"""
        MNE.run_interpreter_from_python("00100000010011000001014005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_greater_than_1_1(self):
        """Test greater than with 1 > 1"""
        MNE.run_interpreter_from_python("00100000010010000001014005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_greater_than_1_minus_1(self):
        """Test greater than with 1 > -1"""
        MNE.run_interpreter_from_python("00110000010010000001014005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_equal_0_0(self):
        """Test equal with 0 == 0"""
        MNE.run_interpreter_from_python("00100000000010000000015005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_equal_0_0001_0(self):
        """Test equal with 0.0001 == 0"""
        MNE.run_interpreter_from_python("00210400000010010000000015005", True)
        self.assertEqual(MNE.printed_output, "0.0")
    def test_equal_0_000999999_0(self):
        """Test equal with 0.0000999999 == 0"""
        MNE.run_interpreter_from_python("00211009999990010000000015005", True)
        self.assertEqual(MNE.printed_output, "1.0")
    def test_add_minus_1_1(self):
        """Test add with -1 + 1"""
        MNE.run_interpreter_from_python("00100000010011000001016", True)
        self.assertAlmostEqual(MNE.stack[0], 0.0)
    def test_add_1e99_1e_minus_99(self):
        """Test add with 1e99 + 1e-99"""
        MNE.run_interpreter_from_python("00209900000010021990000001016", True)
        self.assertAlmostEqual(MNE.stack[0], 1e99)
    def test_add_3_14159_minus_0_14159(self):
        """Test add with 3.14159 + -0.14159"""
        MNE.run_interpreter_from_python("00210503141590021051014159016", True)
        self.assertAlmostEqual(MNE.stack[0], 3.0)
    def test_subtract_1_1(self):
        """Test subtract with 1 - 1"""
        MNE.run_interpreter_from_python("00100000010010000001017", True)
        self.assertAlmostEqual(MNE.stack[0], 0.0)
    def test_subtract_1e99_1e_minus_99(self):
        """Test subtract with 1e99 - 1e-99"""
        MNE.run_interpreter_from_python("00219900000010020990000001017", True)
        self.assertAlmostEqual(MNE.stack[0], 1e99)
    def test_subtract_3_14159_minus_0_14159(self):
        """Test subtract with 3.14159 - 0.14159"""
        MNE.run_interpreter_from_python("00210500141590021050314159017", True)
        self.assertAlmostEqual(MNE.stack[0], 3.0)
    def test_multiply_1_1(self):
        """Test multiply with 1 * 1"""
        MNE.run_interpreter_from_python("00100000010010000001018", True)
        self.assertAlmostEqual(MNE.stack[0], 1.0)
    def test_multiply_minus_1_1(self):
        """Test multiply with -1 * 1"""
        MNE.run_interpreter_from_python("00100000010011000001018", True)
        self.assertAlmostEqual(MNE.stack[0], -1.0)
    def test_multiply_1e99_1e_minus_99(self):
        """Test multiply with 1e99 * 1e-99"""
        MNE.run_interpreter_from_python("00219900000010020990000001018", True)
        self.assertAlmostEqual(MNE.stack[0], 1.0)
    def test_multiply_1_1_1_1(self):
        """Test multiply with 1.1 * 1.1"""
        MNE.run_interpreter_from_python("00210100000110021010000011018", True)
        self.assertAlmostEqual(MNE.stack[0], 1.21)
    def test_divide_16_2(self):
        """Test divide with 16 / 2"""
        MNE.run_interpreter_from_python("00100000020010000016019", True)
        self.assertAlmostEqual(MNE.stack[0], 8.0)
    def test_divide_3_14159_minus_3_14159(self):
        """Test divide with 3.14159 / -3.14159"""
        MNE.run_interpreter_from_python("00210513141590021050314159019", True)
        self.assertAlmostEqual(MNE.stack[0], -1.0)
    def test_divide_1_1e_minus_99(self):
        """Test divide with 1 / 1e-99"""
        MNE.run_interpreter_from_python("00219900000010010000001019", True)
        self.assertAlmostEqual(MNE.stack[0], 1e99)
    def test_divide_1_21_1_1(self):
        """Test divide with 1.21 / 1.1"""
        MNE.run_interpreter_from_python("00210100000110021020000121019", True)
        self.assertAlmostEqual(MNE.stack[0], 1.1)
    def test_divide_by_zero(self):
        """Test divide by zero"""
        MNE.run_interpreter_from_python("00100000000010000001019", True)
        self.assertEqual(MNE.stack, [])
    def test_divide_indeterminate(self):
        """Test divide zero by zero"""
        MNE.run_interpreter_from_python("00100000000010000000019", True)
        self.assertEqual(MNE.stack, [])
    def test_remainder_5_3(self):
        """Test remainder 5 % 3"""
        MNE.run_interpreter_from_python("00100000030010000005022", True)
        self.assertAlmostEqual(MNE.stack[0], 2.0)
    def test_remainder_5_5(self):
        """Test remainder 5 % 5"""
        MNE.run_interpreter_from_python("00100000050010000005022", True)
        self.assertAlmostEqual(MNE.stack[0], 0.0)
    def test_remainder_undefined(self):
        """Test remainder when undefined"""
        MNE.run_interpreter_from_python("00100000000010000005022", True)
        self.assertEqual(MNE.stack, [])
    def test_remainder_13_3_2_99(self):
        """Test remainder with 13.3 % 2.99"""
        MNE.run_interpreter_from_python("00210200002990021010000133022", True)
        self.assertAlmostEqual(MNE.stack[0], 1.0)
    # Taking the remainder when one or both operands is negative is not
    # recommended and thus is not tested
    def test_pop(self):
        """Test pop"""
        MNE.run_interpreter_from_python("00100000010010000002020020", True)
        self.assertEqual(MNE.stack, [])
    def test_duplicate(self):
        """Test duplicate"""
        MNE.run_interpreter_from_python("00100000010210010000002021021", True)
        self.assertEqual(MNE.stack, [1.0, 1.0, 2.0, 2.0, 2.0])
        
if __name__ == "__main__":
    unittest.main()
 
