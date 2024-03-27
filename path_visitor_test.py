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
            elif x > 3:
                return False
            else:
                return True
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([4], visitor.output)


if __name__ == '__main__':
    unittest.main()
