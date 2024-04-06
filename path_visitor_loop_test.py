import ast
import unittest
from path_visitor import UnreachablePathVisitor


class TestPathVisitor(unittest.TestCase):
    # def test_unreachable_while_simple(self):
    #     code = """def example(x):
    #                     while (False):
    #                         print("hello")
    #                     else:
    #                         print("hello2")
    #                     return 5
    #
    #          """
    #
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     visitor.visit(tree)
    #
    #     self.assertListEqual([3], visitor.output)

    # def test_while_reachable_break1(self):
    #     code = """def example(x):
    #                     while (True):
    #                         x = 6
    #                         if x > 3:
    #                           break
    #                     return 5
    #          """
    #
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     visitor.visit(tree)
    #
    #     self.assertListEqual([], visitor.output)
    #
    # def test_while_reachable_break_nested(self):
    #     code = """def example(x):
    #                     while (True):
    #                         while (True):
    #                            if (True):
    #                             break
    #                         break
    #                     return 5
    #          """
    #
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     visitor.visit(tree)
    #
    #     self.assertListEqual([], visitor.output)
    #
    def test_unreachable_while_complicated(self):
        code = """def example(x):
                        y = 69
                        while (x * (y - y + x - x) != 0):
                            print("hello")
                        return 5
             """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([4], visitor.output)

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
        visitor.visit(tree)

        self.assertListEqual([9], visitor.output)

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
        visitor.visit(tree)

        self.assertListEqual([5], visitor.output)
    #
    # def test_unreachable_for_simple(self):
    #     code = """def example(x):
    #                     for i in range(0, 0):
    #                        print("hello!")
    #                     return 6
    #                 """
    #
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     visitor.visit(tree)
    #
    #     self.assertListEqual([3], visitor.output)

    # def test_unreachable_for_variables(self):
    #     code = """def example(x):
    #                     y = 5
    #                     for i in range(x - y - x + y, x*y - x*y):
    #                        print("hello!")
    #                     return 6
    #                 """
    #
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     visitor.visit(tree)
    #
    #     self.assertListEqual([4], visitor.output)

#     def test_unreachable_for_func_call(self):
#         code = """
# def helper1(x):
#     return x + 4
#
# def helper2(x):
#     return x + 4
#
# def example(x):
#     y = 5
#     for i in range(helper1(x), helper2(x)):
#         print("hello!")
#     return 6
#                     """
#
#         tree = ast.parse(code)
#         visitor = UnreachablePathVisitor()
#         visitor.visit(tree)
#
#         self.assertListEqual([11], visitor.output)

#     # TODO: get jeff to fix this test, if possible.
#     def test_reachable_for_func_call(self):
#             code = """
# def helper1(x):
#     return x + 4
#
# def helper2(x):
#     return x + 4
#
# def example(x):
#     y = 5
#     for i in range(helper1(x), helper2(x)):
#         print("hello!")
#     return 6
#                         """
#
#             tree = ast.parse(code)
#             visitor = UnreachablePathVisitor()
#             visitor.visit(tree)
#
#             self.assertListEqual([], visitor.output)

    # def test_unreachable_foreach(self):
    #     code = """def example(x):
    #                     numbers = []
    #                     for num in numbers:
    #                        print(num, " hello!")
    #                     return numbers
    #                 """
    #
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     visitor.visit(tree)
    #
    #     self.assertListEqual([4], visitor.output)
    #


if __name__ == '__main__':
    unittest.main()
