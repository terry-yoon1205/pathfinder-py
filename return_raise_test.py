import ast
import unittest
from path_visitor import UnreachablePathVisitor


class TestReturnRaise(unittest.TestCase):

    def setUp(self):
        self.visitor = UnreachablePathVisitor()
        self.visitor.output = []

    def test_return_single_location(self):
        code = """def example():
            return 1
            print("This will never be reached")
        """

        tree = ast.parse(code)
        self.visitor.visit(tree)
        self.assertListEqual([3], self.visitor.output)

    def test_return_multi_location(self):
        code = """def example():
            return 1
            print("This will never be reached")
def example2():
    return 2
    print("This will also never be reached")
        """
        tree = ast.parse(code)
        self.visitor.visit(tree)
        self.assertListEqual([3, 6], self.visitor.output)


    def test_return_multi_line(self):
        code = """def example():
            return 1
            print("This will never be reached")
            print("This will still never be reached")
            print("This will still never be reached")
            print("This will still never be reached")
        """
        tree = ast.parse(code)
        self.visitor.visit(tree)
        self.assertListEqual([3, 4, 5, 6], self.visitor.output)

    def test_return_if_cond(self):
        code = """def example(x):
            if True: 
                return x;
                print(x, " hello!")
            return 6
        """

        tree = ast.parse(code)
        self.visitor.visit(tree)

        self.assertListEqual([4, 5], self.visitor.output)

    def test_raise_single_location(self):
        code = """def example():
            x = 0
            raise Exception("Can't divide by 0")
            y = 10 / x
        """
        tree = ast.parse(code)
        self.visitor.visit(tree)

        self.assertListEqual([4], self.visitor.output)

    def test_raise_multiple_location(self):
        code = """def example():
            x = 0
            if x == 0:
                raise Exception("Can't divide by 0")
                x = 1
            y = 10 / x
        """
        tree = ast.parse(code)
        self.visitor.visit(tree)

        self.assertListEqual([5, 6], self.visitor.output)
    


if __name__ == '__main__':
    unittest.main()
