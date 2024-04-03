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


    

if __name__ == '__main__':
    unittest.main()
