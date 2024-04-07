import ast
import unittest
from path_visitor import UnreachablePathVisitor


class TestReturnRaise(unittest.TestCase):

    def setUp(self):
        self.visitor = UnreachablePathVisitor()

    def test_return_single_location(self):
        code = """def example():
            return 1
            print("This will never be reached")
        """

        tree = ast.parse(code)
        output = self.visitor.visit(tree)
        self.assertListEqual([3], output)

    def test_return_multi_location(self):
        code = """def example():
            return 1
            print("This will never be reached")
def example2():
    return 2
    print("This will also never be reached")
        """
        tree = ast.parse(code)
        output = self.visitor.visit(tree)
        self.assertListEqual([3, 6], output)

    def test_return_multi_line(self):
        code = """def example():
            return 1
            print("This will never be reached")
            print("This will still never be reached")
            print("This will still never be reached")
            print("This will still never be reached")
        """
        tree = ast.parse(code)
        output = self.visitor.visit(tree)
        self.assertListEqual([3], output)

    def test_return_if_cond(self):
        code = """def example(x):
            if True: 
                return x;
                print(x, " hello!")
            return 6
        """

        tree = ast.parse(code)
        output = self.visitor.visit(tree)

        self.assertListEqual([4, 5], output)

    def test_return_if_else(self):
        code = """def example(x):
                    if x > 0: 
                        return x
                    else:
                        return 0
                    return 6
                """

        tree = ast.parse(code)
        output = self.visitor.visit(tree)

        self.assertListEqual([6], output)

    def test_return_nested_if_else_1(self):
        code = """def example(x, y):
                    if x > 0: 
                        if y < 0:
                            return x
                        elif x > 2:
                            return 2
                        else:
                            return 0
                    elif y > 0:
                        return y
                    else:
                        return 0
                    return 6
                """

        tree = ast.parse(code)
        output = self.visitor.visit(tree)

        self.assertListEqual([13], output)

    def test_return_nested_if_else_2(self):
        code = """def example(x, y):
                    if x > 0: 
                        if y < 0:
                            return x
                        elif x > 2:
                            x = x + 1
                        else:
                            return 0
                    else:
                        return 0
                    return 6
                """

        tree = ast.parse(code)
        output = self.visitor.visit(tree)

        self.assertListEqual([], output)

    def test_return_meaningless_statements(self):
        code = \
            """def func1():
    return 0

def func():
    return 3
    
def example(x, y):
    if x > 0: 
        if y < 0:
            x + y
            y = x
            return x
        elif x > 2:
            x = x + 1
            x = y - 1
        else:
            x = func()
            return 0
    else:
        y = x + 3
        return 0
    x = y
    return 6
"""

        tree = ast.parse(code)
        output = self.visitor.visit(tree)

        self.assertListEqual([], output)

    def test_raise_single_location(self):
        code = """def example():
            x = 0
            raise Exception("Can't divide by 0")
            y = 10 / x
        """
        tree = ast.parse(code)
        output = self.visitor.visit(tree)

        self.assertListEqual([4], output)

    def test_raise_multiple_location(self):
        code = """def example():
            x = 0
            if x == 0:
                raise Exception("Can't divide by 0")
                x = 1
            y = 10 / x
        """
        tree = ast.parse(code)
        output = self.visitor.visit(tree)

        self.assertListEqual([5, 6], output)


if __name__ == '__main__':
    unittest.main()
