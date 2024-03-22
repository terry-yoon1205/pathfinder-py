import ast

class State:
    def __init__(self):
        self.variables = []

class Visitor(ast.NodeVisitor):
    def __init__(self, state):
        self.state = state

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.state.variables.append(node.id)
        self.generic_visit(node)

def analyze_code(code):
    tree = ast.parse(code)
    state = State()
    visitor = Visitor(state)
    visitor.visit(tree)
    print("Variables:", state.variables)

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

analyze_code(code)