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
        output = visitor.visit(tree)

        self.assertListEqual([3], output)

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
        output = visitor.visit(tree)

        self.assertListEqual([3], output)

    def test_call_to_undefined_function(self):
        code = """def some_function():
                    undefined_function()
                """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)
        self.assertIn(2, output, "The call to an undefined function should be detected as unrunnable")

    def test_call_with_extra_parameters(self):
        code = """  
def another_function(x):
    return x

def some_function():
    another_function(1, 2)
                """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertIn(6, output)

    def test_call_with_less_parameters(self):
        code = """  
def another_function(x, y):
    return x

def some_function():
    another_function(1)
                        """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertIn(6, output)

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
        output = visitor.visit(tree)

        self.assertIn(8, output, "None detected")

    def test_call_with_uninitialized_variable_parameters(self):
        code = """ 
def another_function(x, y):
    return x + y

def some_function():
    another_function(x, 2)
                            """
        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertIn(6, output)

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
        output = visitor.visit(tree)
        self.assertIn(7, output)

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
        output = visitor.visit(tree)
        self.assertIn(8, output)


#     def test_call_complex(self):
#         code = """x = Int('x')
# y = Int('y')
# f = Function('f', IntSort(), IntSort())
# s = Solver()
# s.add(f(f(x)) == x, f(x) == y, x != y)"""
#         tree = ast.parse(code)
#         visitor = UnreachablePathVisitor()
#         output = visitor.visit(tree)
#         print(output)
#         self.assertIn(0, output)

if __name__ == '__main__':
    unittest.main()
