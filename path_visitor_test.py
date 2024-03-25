import ast
import unittest
from path_visitor import UnreachablePathVisitor


class TestPathVisitor(unittest.TestCase):
    def test_simple(self):
        code = """
        x = 1
        y = 2
        if x < 5:
            z = x + y
        
        test_string = "test"
        
        def example_function():
            return 1
            print("This will never be reached")
        example_function()
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([10], visitor.output)


if __name__ == '__main__':
    unittest.main()
