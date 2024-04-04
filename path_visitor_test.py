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
            elif x > 6:
                return False
            else:
                return True
        """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([5], visitor.output)

    def test_unreachable_nested(self):
        code = """def example(x, y):
                if x > 5:
                    if y > 14:
                        return True
                    elif y > 15:
                        return False;
                elif x > 6:
                    return False;  
                else:
                    return True
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([6, 8], visitor.output)

    def test_no_issues(self):
        code = """def example(x):
                if x > 5:
                    return True;
                elif x > 4:
                    return False;  
                else:
                    return True
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([], visitor.output)

    def test_unreachable_else(self):
        code = """def example(x):
                if x >= 5:
                    return True;
                elif x < 5:
                    return False;
                else:
                    return null;   # python will throw excepetion if (x) is not an number and cannot be coerced into one.
            """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([7], visitor.output)

    def test_unreachable_while_simple(self):
        code = """def example(x):
                        while (False): 
                            print("hello")
                        return 5
             """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([3], visitor.output)

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


    def test_unreachable_for_simple(self):
        code = """def example(x):
                        for i in range(0, 0): 
                           print("hello!")
                        return 6
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([3], visitor.output)

    def test_unreachable_for_return(self):
        code = """def example(x):
                        for i in range(0, 11): 
                           return x;
                           print(x, " hello!")
                        return 6
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([4, 5], visitor.output)

    def test_unreachable_foreach(self):
        code = """def example(x):
                        numbers = []
                        for num in numbers: 
                           print(num, " hello!")
                        return numbers
                    """

        tree = ast.parse(code)
        visitor = UnreachablePathVisitor()
        visitor.visit(tree)

        self.assertListEqual([4], visitor.output)






if __name__ == '__main__':
    unittest.main()
