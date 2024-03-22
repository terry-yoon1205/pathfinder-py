import ast

class State:
    def __init__(self):
        self.variables = []
        self.conditionals = {}
        self.loops = {}
        self.functions = {}

class Visitor(ast.NodeVisitor):
    def __init__(self, state):
        self.state = state

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.state.variables.append((node.id, node.lineno))
        self.generic_visit(node)

    def visit_If(self, node):
        self.state.conditionals[node.lineno] = ast.dump(node.test)
        self.generic_visit(node)

    def visit_For(self, node):
        self.state.loops[node.lineno] = ast.dump(node.target)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.state.functions[node.name] = node.lineno
        self.generic_visit(node)

def analyze_code(code):
    tree = ast.parse(code)
    state = State()
    visitor = Visitor(state)
    visitor.visit(tree)

    print("Variables:", state.variables)
    print("Conditionals:", state.conditionals)
    print("Loops:", state.loops)
    print("Functions:", state.functions)

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
