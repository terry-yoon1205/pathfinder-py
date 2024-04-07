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
        output = visitor.visit(tree)

        self.assertListEqual([], output)

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
        output = visitor.visit(tree)

        self.assertListEqual([5], output)

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
        output = visitor.visit(tree)

        self.assertListEqual([7], output)

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
        output = visitor.visit(tree)

        self.assertListEqual([6, 8], output)

    def test_consecutive(self):
        code = """def example(x, y):
    if x > 0:
        y = -1
    else:
        x = -1
        y = 10
        
    if x > 0 and y > 0:
        return x
    else:
        return y
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([9], output)

    def test_consecutive_nested(self):
        code = """def example(x, y):
    if x > 0:
        if x > 5:
            y = 5
        elif x > 6:
            y = 5
        else:
            y = 0
    else:
        x = -1
        y = -1

    if x > 0 and y == 5:
        return x
    elif x < 0 and y > 0:
        return y
    else:
        return 0
                        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([6, 16], output)

    def test_combined(self):
        code = """def example(x, y):
    z = x - y
    if z > 0:
        x = x + y
    elif z > 3:
        x = x + y + 3
    else:
        y = 0

    while x > y:
        print(y)
        y = add_two(y)

def add_two(n):
    return n + 2"""

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([6], output)


if __name__ == '__main__':
    unittest.main()
