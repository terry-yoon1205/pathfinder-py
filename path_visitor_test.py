import ast
import unittest
from path_visitor import UnreachablePathVisitor


class TestPathVisitor(unittest.TestCase):
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

    def test_unreachable_while_complicated_func_call(self):
        code = """def example(x):
                   return x
        
                  def example2(x):
                        y = 69
                        while (example(x) - x != 0): 
                            print("hello")
                        return 5
             """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([3], visitor.output)

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

    def test_call_with_uninitialized_variable_parameters(self):
        code = """
def another_function(x, y):
    return x + y

def some_function():
    y = 2
    another_function(x, 2)
                            """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertIn(7, visitor.output)

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

    def test_instance_methods(self):
        code = """class Calculator:
    def add(self, a, b):
        return a + b

calc = Calculator()

result = calc.add(5, 3)

print("The result is:", result)
"""
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)
        print(visitor.output)
        # not passing right now as return None
        self.assertEqual(0, len(visitor.output))

    def test_call_with_nested_call(self):
        code = """def outer_function(text):
    def inner_function(subtext):
        return subtext.upper()
    
    x = 3
    result = inner_function(text)
    return result"""
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)
        # print(visitor.output)
        self.assertEqual(0, len(visitor.output))

if __name__ == '__main__':
    unittest.main()
