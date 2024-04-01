import ast
from z3 import ArithRef, BoolRef, Const, RealSort, substitute

from dataclasses import dataclass, field


@dataclass
class Var:
    """
    Represents a numerical variable. Supported types are int, float, and bool.

    name: The name of the variable.
    ref: The corresponding real-valued Z3 constant.
    eqs: System of Z3 constraints ("applications") containing this variable.
    """
    name: str
    ref: ArithRef
    eqs: list[BoolRef] = field(default_factory=list)


class UnreachablePathVisitor(ast.NodeVisitor):
    variables: dict[str, Var] = {}  # key: variable name
    function_nodes = {}  # maybe use to traverse through function calls?
    output: list[int] = []  # line numbers (?)
    ctx_vars: list[Var] = []  # current variable(s) we're working with (?)

    """
    Root
    """

    def visit_Module(self, node):
        # TODO
        self.generic_visit(node)

    """
    Literals and variable names
    """

    def visit_Name(self, node):
        if self.variables:
            src_var = self.variables[node.id]

        for var in self.ctx_vars:
            var.eqs = [substitute(eq, (src_var.ref, var.ref)) for eq in src_var.eqs]

    def visit_Constant(self, node):
        try:
            val = float(node.value)
            for var in self.ctx_vars:
                var.eqs = [var.ref == val]
        except ValueError:
            return

    """
    Expressions
    """

    def visit_Call(self, node):
        # TODO
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        # TODO
        self.generic_visit(node)

    def visit_BinOp(self, node):
        # TODO
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # TODO
        self.generic_visit(node)

    def visit_Compare(self, node):
        # TODO
        self.generic_visit(node)

    """
    Statements
    """

    def visit_Assign(self, node):
        self.ctx_vars.clear()

        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue

            name = target.id
            if name not in self.variables:
                # create new variable
                self.variables[name] = Var(name, Const(name, RealSort()))

            self.ctx_vars.append(self.variables[name])

        self.visit(node.value)

    def visit_AugAssign(self, node):
        # TODO
        self.generic_visit(node)

    def visit_Return(self, node):
        # TODO
        self.generic_visit(node)

    def visit_Raise(self, node):
        # TODO
        self.generic_visit(node)

    """
    Definitions
    """

    def visit_FunctionDef(self, node):
        # TODO
        self.generic_visit(node)

    """
    Control flow
    """

    def visit_If(self, node):
        # TODO
        self.generic_visit(node)

    def visit_For(self, node):
        # TODO
        self.generic_visit(node)

    def visit_While(self, node):
        # TODO
        self.generic_visit(node)


class FunctionCollector(ast.NodeVisitor):
    # TODO: we can maybe use another visitor to collect FunctionDef nodes, so we can traverse
    #       through function calls.
    def visit_FunctionDef(self, node):
        return node.name  # stub


if __name__ == "__main__":
    # manual testing w/ debugger
    code = 'x = 1\ny = 2\nz = x'

    tree = ast.parse(code)
    visitor = UnreachablePathVisitor()
    visitor.visit(tree)
