import ast
import unittest
from path_visitor import UnreachablePathVisitor


class FunctionTest(unittest.TestCase):
    def test_call_with_if(self):
        code = """def example(x):
    if x > 0:
        x = add_one(x)
        if x < 0:
            return 0
        else:
            return x
    else:
        return x

def add_one(num):
    return num + 1
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([5], output)

    def test_call_unreachable_while_loop(self):
        code = """def example(x):
    return x

def example2(x):
    y = 69
    while example(x) - x != 0: 
        print("hello")
    return 5
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([7], output)

    def test_call_unreachable_if_block(self):
        code = """def another_function(x):
    return x < 0

def some_function():
    x = 1 + 2
    if another_function(x):
        return
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([7], output)

    def test_nested_functions(self):
        code = """def func(x, y):
    z = x + y
    
    def inner_func(n):
        return n * 0
    def inner_func_2(n):
        return n * 2
        
    if inner_func(z) >= 0:
        return 0
    elif inner_func_2(z) >= 0:
        return z
    else:
        return 1
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        output = visitor.visit(tree)

        self.assertListEqual([11], output)

    # def test_instance_methods(self):
    #     code = """class Calculator:
    #     def add(self, a, b):
    #         return a + b
    #
    # calc = Calculator()
    #
    # result = calc.add(5, 3)
    #
    # print("The result is:", result)
    # """
    #     tree = ast.parse(code)
    #     visitor = UnreachablePathVisitor()
    #     output = visitor.visit(tree)
    #     print(output)
    #     # not passing right now as return None
    #     self.assertEqual(0, len(output))


if __name__ == '__main__':
    unittest.main()
