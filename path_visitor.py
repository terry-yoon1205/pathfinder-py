import ast
from z3 import *


class UnreachablePathVisitor(ast.NodeVisitor):
    """
    variables: a dictionary mapping variable names to its symbolic representation.
               may be a boolean or an arithmetic expression.
    func_nodes: a collection of ast.FunctionDef nodes, used for traversing function calls.
    path_conds: a stack of boolean expressions representing path conditions.
    output: a list of line numbers that are deemed unreachable.
    """
    def __init__(self):
        self.variables: dict[str, ArithRef | BoolRef] = {}
        self.func_nodes = {}
        self.path_conds: list[BoolRef] = []
        self.output: list[int] = []

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
        return self.variables[node.id]

    def visit_Constant(self, node):
        try:
            if isinstance(node.value, bool):
                return BoolVal(node.value)
            else:
                return RealVal(float(node.value))
        except ValueError:
            # unsupported value
            return None

    """
    Expressions
    """
    def visit_Call(self, node):
        # TODO
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        op = node.op
        operand = node.operand
        value = self.visit(operand)

        match type(op):
            case ast.USub:
                result = -value
            case ast.UAdd:
                result = +value
            case ast.Not:
                result = Not(value)
            # case ast.Invert:
            #     result = ~value
            case _:     # Unsupported
                return None

        return result

    def visit_BinOp(self, node):
        # TODO
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # TODO
        self.generic_visit(node)

    def visit_Compare(self, node):
        comparators = [self.visit(comparator) for comparator in [node.left] + node.comparators]
        eqs = []

        for i in range(len(comparators) - 1):   # len(comparators) == len(node.ops) + 1
            lhs = comparators[i]
            rhs = comparators[i + 1]
            op = node.ops[i]

            match type(op):
                case ast.Eq:
                    eqs.append(lhs == rhs)
                case ast.NotEq:
                    eqs.append(lhs != rhs)
                case ast.Lt:
                    eqs.append(lhs < rhs)
                case ast.LtE:
                    eqs.append(lhs <= rhs)
                case ast.Gt:
                    eqs.append(lhs > rhs)
                case ast.GtE:
                    eqs.append(lhs >= rhs)
                case _:
                    # unsupported
                    pass

        return simplify(And(*eqs))

    """
    Statements
    """
    def visit_Assign(self, node):
        rhs = self.visit(node.value)

        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables[target.id] = rhs

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
        # TODO: create a symbolic variable (with some arbitrary name) for each function argument
        #       before traversing the function.
        self.generic_visit(node)

    """
    Control flow
    """
    def visit_If(self, node):
        if_cond = self.visit(node.test)
        if isinstance(if_cond, ArithRef):
            if_cond = if_cond > 0

        solver = Solver()
        for cond in self.path_conds:
            solver.add(cond)

        solver.push()
        solver.add(if_cond)

        if solver.check() == unsat:
            # no solution, if branch unreachable
            first_line = node.body[0]
            self.output.append(first_line.lineno)
        else:
            self.path_conds.append(if_cond)

            for child in node.body:
                self.visit(child)

            self.path_conds.pop()

        if len(node.orelse) == 0:   # no else branch, return
            return

        else_cond = Not(if_cond)

        solver.pop()
        solver.add(else_cond)

        if solver.check() == unsat:
            # no solution, else branch unreachable
            first_line = node.orelse[0]
            self.output.append(first_line.lineno)
        else:
            # spawn a copy of this visitor to traverse the else branch
            else_visitor = UnreachablePathVisitor()
            else_visitor.variables = self.variables.copy()
            else_visitor.path_conds = self.path_conds.copy() + [else_cond]
            else_visitor.output = self.output  # append to the same list instance

            for child in node.orelse:
                else_visitor.visit(child)

            # merge the visitors together (maybe change to analyze all branches separately)
            for var_name in self.variables:
                if_result = self.variables[var_name]
                else_result = else_visitor.variables[var_name]

                self.variables[var_name] = Or(if_result, else_result)

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
    '''
    for manual testing w/ debugger
    
    x = 1
    y = 2
    if x < y < 4:
        y = 3
    else:
        y = 1
    '''
    code = 'x = 1\ny = 2\nif x < y < 4:\n    y = 3\nelse:\n    y = 1'

    tree = ast.parse(code)
    visitor = UnreachablePathVisitor()
    visitor.visit(tree)

    print(visitor.output)
