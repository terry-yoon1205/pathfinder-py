import ast
import unittest
from path_visitor import UnreachablePathVisitor


class TestPathVisitor(unittest.TestCase):
    def test_after_return(self):
        code = """def example():
            return 1
            print("This will never be reached")
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([3], visitor.output)

    def test_unreachable_if_block(self):
        code = """def example(x):
            if x > 5:
                return True
            elif x > 6:
                return False
            else:
                return True
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([5], visitor.output)

    def test_unreachable_nested(self):
        code = """def example(x, y):
                if x > 5:
                    if y > 14:
                        return True
                    elif y > 15:
                        return False;
                elif x > 6:
                    return False;
                else:
                    return True
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6, 8], visitor.output)

    def test_no_issues(self):
        code = """def example(x):
                if x > 5:
                    return True;
                elif x > 4:
                    return False;
                else:
                    return True
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([], visitor.output)

    def test_unreachable_else(self):
        code = """def example(x):
                if x >= 5:
                    return True;
                elif x < 5:
                    return False;
                else:
                    return null;   # python will throw excepetion if (x) is not an number and cannot be coerced into one.
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([7], visitor.output)

    def test_unreachable_while_simple(self):
        code = """def example(x):
                        while (False):
                            print("hello")
                        return 5
             """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([3], visitor.output)

    def test_unreachable_code_after_while(self):
        code = """def example(x):
                        i = 5
                        while (True):
                           i += 1
                           if i > 15:
                             print("not yet")
                           elif i > 16:
                             break
                        return 5
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([9], visitor.output)

    def test_unreachable_while_else(self):
        code = """def example(x):
                        while (True):
                            break
                        else:
                            return 11
                        return 5
             """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([5], visitor.output)


    def test_unreachable_for_simple(self):
        code = """def example(x):
                        for i in range(0, 0):
                           print("hello!")
                        return 6
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([3], visitor.output)

    def test_unreachable_for_return(self):
        code = """def example(x):
                        for i in range(0, 11):
                           return x;
                           print(x, " hello!")
                        return 6
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([4, 5], visitor.output)

    def test_unreachable_foreach(self):
        code = """def example(x):
                        numbers = []
                        for num in numbers:
                           print(num, " hello!")
                        return numbers
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([4], visitor.output)

    def test_call_to_undefined_function(self):
        code = """def some_function():
                    undefined_function()
                """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)
        self.assertIn(2, visitor.output, "The call to an undefined function should be detected as unrunnable")

    def test_call_with_extra_parameters(self):
        code = """  
def another_function(x):
    return x

def some_function():
    another_function(1, 2)
                """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertIn(6, visitor.output)

    def test_call_with_less_parameters(self):
        code = """  
def another_function(x, y):
    return x

def some_function():
    another_function(1)
                        """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertIn(6, visitor.output)

    def test_call_with_none_parameters(self):
        code = """
def another_function(x, y):
    x+=1
    return x + y

def some_function():
    print("2")
    another_function(None, 3)
                    """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)
        # print(visitor.output)
        self.assertIn(8, visitor.output, "None detected")

#       TODO: not passing right now since x is not None
#     def test_call_with_uninitialized_variable_parameters(self):
#         code = """
# def another_function(x, y):
#     return x + y
#
# def some_function():
#     another_function(x, 2)
#                             """
#         tree = ast.parse(code)
#         visitor = UnreachablePathVisitor()
#         visitor.visit(tree)
#
#         self.assertIn(6, visitor.output)

    def test_call_with_with_If(self):
        code = """  
def another_function(x):
    return x

def some_function():
    if (False):
        another_function(1, 2)
        another_function(None)
    x = 1+2
                        """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)
        self.assertIn(7, visitor.output)

    def test_call_with_with_for(self):
        code = """  
def another_function(x,y):
    return x

def some_function():
    for i in range(2):
        another_function(1, 2)
        another_function(None)
    x = 1+2
                        """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)
        self.assertIn(8, visitor.output)

    def test_call_z3_instance(self):
        code = """x = Int('x')
y = Int('y')
f = Function('f', IntSort(), IntSort())
s = Solver()
s.add(f(f(x)) == x, f(x) == y, x != y)"""
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)
        # print(visitor.output)
        self.assertEqual(0, len(visitor.output))

#     def test_instance_methods(self):
#         code = """class Calculator:
#     def add(self, a, b):
#         return a + b
#
# calc = Calculator()
#
# result = calc.add(5, 3)
#
# print("The result is:", result)
# """
#         tree = ast.parse(code)
#         visitor = UnreachablePathVisitor()
#         visitor.visit(tree)
#         print(visitor.output)
#         self.assertEqual(0, len(visitor.output))
if __name__ == '__main__':
    unittest.main()
