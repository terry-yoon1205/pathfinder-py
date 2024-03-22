import ast

def analyze_code(code):
    tree = ast.parse(code)

    def check_unreachable(node):
        if isinstance(node, (ast.Return, ast.Break, ast.Continue, ast.Raise)):
            # Check if the statement is followed by more code
            for sibling in ast.walk(node):
                if sibling != node and not isinstance(sibling, ast.Pass):
                    print(f"Unreachable code found after line {node.lineno}")

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for statement in node.body:
                check_unreachable(statement)
        elif isinstance(node, ast.If):
            check_unreachable(node)

code = """
def example_function():
    return 1
    print("This will never be reached")

example_function()
"""

analyze_code(code)
