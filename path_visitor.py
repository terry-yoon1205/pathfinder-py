import ast
from z3 import *
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
    ctx_vars: list[Var] = []  # current variable(s) we're working with
    path_conds: list[list[BoolRef]] = []

    output: list[int] = []  # line numbers (?)

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
        src_var = self.variables[node.id]

        if self.is_assignment():
            for var in self.ctx_vars:
                var.eqs = [substitute(eq, (src_var.ref, var.ref)) for eq in src_var.eqs]
        else:
            return [src_var], [src_var.ref > 0]

    def visit_Constant(self, node):
        try:
            val = float(node.value)
        except ValueError:
            return

        if self.is_assignment():
            for var in self.ctx_vars:
                var.eqs = [var.ref == val]
        else:
            return [], [val > 0]

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
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue

            name = target.id
            if name not in self.variables:
                # create new variable
                self.variables[name] = Var(name, Const(name, RealSort()))

            self.ctx_vars.append(self.variables[name])

        self.visit(node.value)
        self.ctx_vars.clear()  # always clear at the end

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
        # visit should return a list of variables and a list of constraints
        cond_vars, if_conds = self.visit(node.test)
        var_conds = [cond for var in cond_vars for cond in var.eqs]
        path_conds = [cond for lst in self.path_conds for cond in lst]

        solver = Solver()
        solver.push()
        for cond in var_conds + if_conds + path_conds:
            solver.add(cond)

        if solver.check() == unsat:
            # no solution, if branch unreachable
            first_line = node.body[0]
            self.output.append(first_line.lineno)
        else:
            self.path_conds.append(if_conds)

            for child in node.body:
                self.visit(child)

            self.path_conds.pop()

        if len(node.orelse) == 0:   # no else branch, return
            return

        else_conds = [Not(cond) for cond in if_conds]

        solver.pop()
        for cond in var_conds + else_conds + path_conds:
            solver.add(cond)

        if solver.check() == unsat:
            # no solution, else branch unreachable
            first_line = node.orelse[0]
            self.output.append(first_line.lineno)
        else:
            # spawn a copy of this visitor to traverse the else branch
            else_visitor = UnreachablePathVisitor()
            else_visitor.variables = self.variables.copy()
            else_visitor.path_conds = self.path_conds.copy().append(else_conds)
            else_visitor.output = self.output  # append to the same list instance

            for child in node.orelse:
                else_visitor.visit(child)

            # merge the visitors together (maybe change to analyze all branches separately)
            for var_name in self.variables:
                if_result = simplify(And(*self.variables[var_name].eqs))
                else_result = simplify(And(*else_visitor.variables[var_name].eqs))

                self.variables[var_name].eqs = [Or(if_result, else_result)]

    def visit_For(self, node):
        # TODO
        self.generic_visit(node)

    def visit_While(self, node):
        # TODO
        self.generic_visit(node)

    """
    Helpers
    """

    def is_assignment(self):
        return len(self.ctx_vars) > 0


class FunctionCollector(ast.NodeVisitor):
    # TODO: we can maybe use another visitor to collect FunctionDef nodes, so we can traverse
    #       through function calls.
    def visit_FunctionDef(self, node):
        return node.name  # stub


if __name__ == "__main__":
    '''
    for manual testing w/ debugger
    
    x = 1
    y = 2
    if y:
        y = 3
    else:
        y = 1
    '''
    code = 'x = 1\ny = 2\nif y:\n    y = 3\nelse:\n    y = 1'

    tree = ast.parse(code)
    visitor = UnreachablePathVisitor()
    visitor.visit(tree)
