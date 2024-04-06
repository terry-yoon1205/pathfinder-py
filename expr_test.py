import ast
import unittest
from path_visitor import UnreachablePathVisitor


class ExprTest(unittest.TestCase):
    def test_unreachable_unary_neg(self):
        code = """def example(x):
                    y = -5
                    if y > 0:
                        return True
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([4], visitor.output)

    def test_unreachable_unary_double_neg(self):
        code = """def example(x):
                    y = --0.5
                    if y < 0:
                        return True
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([4], visitor.output)

    def test_unreachable_unary_pos(self):
        code = """def example(x):
                    if +5 != 5:
                        return True
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([3], visitor.output)

    # def test_unreachable_unary_invert(self):
    #     code = """def example(x):
    #                 y = True
    #                 if ~y:
    #                     return True
    #                 return False
    #     """
    #
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     visitor.visit(tree)
    #
    #     self.assertListEqual([5], visitor.output)

    def test_unreachable_unary_not(self):
        code = """def example(x):
                    y = True
                    if not y:
                        return True
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([4], visitor.output)

    def test_unreachable_bool_or(self):
        code = """def example(x):
                    if True or False or True:
                        c = 1
                    else:
                        c = 2
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([5], visitor.output)

    def test_unreachable_bool_and(self):
        code = """def example(x):
                    if True and False:
                        c = 1
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([3], visitor.output)

    def test_unreachable_bool_and_or(self):
        code = """def example(x):
                    y = True
                    if False or (y and True):
                        c = 2
                    else:
                        c = 1
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6], visitor.output)

    def test_unreachable_bin_add(self):
        code = """def example(x):
                    y = 1 + 2
                    if y == 3:
                        c = 2
                    else:
                        c = 1
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6], visitor.output)

    def test_unreachable_bin_sub(self):
        code = """def example(x):
                    y = 2 - 1
                    if y == 1:
                        c = 2
                    else:
                        c = 1
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6], visitor.output)

    def test_unreachable_bin_sub2(self):
        code = """def example(x):
                    y = 2 - 1
                    if y == 2:
                        c = 2
                    else:
                        c = 1
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6], visitor.output)

    def test_unreachable_bin_mult(self):
        code = """def example(x):
                    y = 2 * 2
                    if y == 4:
                        c = 2
                    else:
                        c = 1
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6], visitor.output)

    def test_unreachable_bin_Div(self):
        code = """def example(x):
                    y = 2 / 2
                    if y == 1:
                        c = 2
                    else:
                        c = 1
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6], visitor.output)

    def test_unreachable_bin_Div_fail(self):
        code = """def example(x):
                    y = 2 / 2
                    if y == 2:
                        c = 2
                    else:
                        c = 1
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6], visitor.output)

    # def test_unreachable_bin_floorDiv(self):
    #     code = """def example(x):
    #                 y = 3 // 2
    #                 if y == 1:
    #                     c = 2
    #                 else:
    #                     c = 1
    #                 return False
    #     """
    #
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     visitor.visit(tree)
    #
    #     self.assertListEqual([6], visitor.output)
    #
    # def test_unreachable_bin_mod(self):
    #     code = """def example(x):
    #                 y = 3 % 2
    #                 if y == 1:
    #                     c = 2
    #                 else:
    #                     c = 1
    #                 return False
    #     """
    #
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     visitor.visit(tree)
    #
    #     self.assertListEqual([6], visitor.output)

    def test_unreachable_bin_pow(self):
        code = """def example(x):
                    y = 3 ** 2
                    if y == 9:
                        c = 2
                    else:
                        c = 1
                    return False
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6], visitor.output)


if __name__ == '__main__':
    unittest.main()
