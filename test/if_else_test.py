import ast
import unittest
from path_visitor import UnreachablePathVisitor


class IfElseTest(unittest.TestCase):
    def test_ok(self):
        code = """def example(x):
                if x > 5:
                    return True
                elif x > 4:
                    return False
                else:
                    return True
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([], visitor.output)

    def test_unreachable_elif(self):
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

    def test_unreachable_else(self):
        code = """def example(x):
                if x >= 5:
                    return True
                elif x < 5:
                    return False
                else:
                    return null
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([7], visitor.output)

    def test_unreachable_nested(self):
        code = """def example(x, y):
                if x > 5:
                    if y > 14:
                        return True
                    elif y > 15:
                        return False
                elif x > 6:
                    return False
                else:
                    return True
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6, 8], visitor.output)


if __name__ == '__main__':
    unittest.main()
