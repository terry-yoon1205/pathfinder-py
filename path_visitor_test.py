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

        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
