import ast
import unittest
from path_visitor import UnreachablePathVisitor


class LoopTest(unittest.TestCase):
    def test_unreachable_while_simple(self):
        code = """def example(x):
                        while (False):
                            print("hello")
                        else:
                            print("hello2")
                        return 5
             """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([3], output)

    def test_while_reachable_break1(self):
        code = """def example(x):
                        while (True):
                            x = 6
                            if x > 3:
                              break
                        return 5
             """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([], output)

    def test_while_reachable_break_nested(self):
        code = """def example(x):
                        while (True):
                            while (True):
                               if (True):
                                break
                            break
                        return 5
             """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([], output)

    def test_unreachable_while_complicated(self):
        code = """def example(x):
                        y = 69
                        while (x * (y - y + x - x) != 0):
                            print("hello")
                        return 5
             """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([4], output)

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
        output = visitor.visit(tree)

        self.assertListEqual([6, 8, 9], output)

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
        output = visitor.visit(tree)

        self.assertListEqual([5], output)

    def test_unreachable_for_simple(self):
        code = """def example(x):
                        for i in range(0, 0):
                           print("hello!")
                        return 6
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([3], output)

    def test_unreachable_for_variables(self):
        code = """def example(x):
                        y = 5
                        for i in range(x - y - x + y, x*y - x*y):
                           print("hello!")
                        return 6
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([4], output)

    def test_unreachable_for_func_call(self):
        code = """
def helper1(x):
    return x + 4

def helper2(x):
    return x + 4

def example(x):
    y = 5
    for i in range(helper1(x), helper2(x)):
        print("hello!")
    return 6
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([11], output)

    def test_reachable_for_func_call(self):
        code = """
def helper1(x):
    return x + 4

def helper2(x):
    return x + 5

def example(x):
    y = 5
    for i in range(helper1(x), helper2(x)):
        print("hello!")
    return 6
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([], output)


if __name__ == '__main__':
    unittest.main()
