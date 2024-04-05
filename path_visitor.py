import ast
from dataclasses import dataclass, field
from z3 import *
import builtins


@dataclass
class CurrentScope:
    """
    Used to keep track of scope for return/raise related analysis.
    For naming's sake, return here refers to both return and raise

    name: Name of the current function
    end_no: Line number where the function ends
    return_no: Line number of the return statement
    return_exists: flag to determine if return statement exists in a code block
    """
    name: str
    end_no: int
    return_no: int = -1
    return_exists: bool = False
    edge_cases: list[int] = field(default_factory=list)


class UnreachablePathVisitor(ast.NodeVisitor):
    """
    variables: a dictionary mapping variable names to its symbolic representation.
               may be a boolean or an arithmetic expression.
    func_nodes: a collection of ast.FunctionDef nodes, used for traversing function calls.
    path_conds: a stack of boolean expressions representing path conditions.
    output: a list of line numbers that are deemed unreachable.
    """
    variables: dict[str, ArithRef | BoolRef] = {}
    func_nodes = {}
    path_conds: list[BoolRef] = []
    output: list[int] = []
    scope: CurrentScope = {}

    symbol_prefix = 'var'
    symbol_idx = 0

    """
    Call for every visit
    """

    def generic_visit(self, node):
        try:
            return_no: int = self.scope.return_no
            edge: list[int] = self.scope.edge_cases
            if node.lineno not in self.output:
                if node.lineno in edge:
                    self.output = sorted(list(set(self.output + edge)))
                elif node.lineno > return_no != -1:
                    self.output.append(node.lineno)
        except:
            pass

        super().generic_visit(node)

    """
    Root
    """

    def visit_Module(self, node):
        self.func_nodes.update(analyze_code(node))
        self.generic_visit(node)

    """
    Literals and variable names
    """

    def visit_Name(self, node):
        if node.id not in self.variables:
            return "temp"
        return self.variables[node.id]

    def visit_Constant(self, node):
        try:
            return RealVal(float(node.value))
        except ValueError:
            # unsupported value
            return None

    """
    Expressions
    """

    def visit_Call(self, node):
        # TODO
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            if func_name in self.func_nodes:
                prepared_args = []
                for arg in node.args:
                    if isinstance(arg, ast.Name) and arg.id in self.variables:
                        prepared_args.append(self.variables[arg.id])
                    elif isinstance(arg, ast.Constant):
                        prepared_args.append(arg.value)
                    else:
                        self.generic_visit(arg)

                handler = self.func_nodes[func_name]
                if None in prepared_args:
                    self.output.append(node.lineno)

                if hasattr(handler.args, 'args'):
                    num_required_arguments = len(handler.args.args)
                else:
                    num_required_arguments = len(handler.args)

                if num_required_arguments != len(prepared_args):
                    self.output.append(node.lineno)
                return prepared_args

            else:
                self.output.append(node.lineno)
                print(f"Warning: Function {func_name} not defined, added to output.")
        else:
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
        comparators = [self.visit(comparator) for comparator in [node.left] + node.comparators]
        eqs = []

        for i in range(len(comparators) - 1):  # len(comparators) == len(node.ops) + 1
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
        self.scope.return_no = node.lineno
        self.scope.return_exists = True
        self.generic_visit(node)

    def visit_Raise(self, node):
        self.scope.return_no = node.lineno
        self.scope.return_exists = True
        self.generic_visit(node)

    """
    Definitions
    """

    def visit_FunctionDef(self, node):
        self.scope = CurrentScope(node.name, node.end_lineno)

        for arg in node.args.args:
            name = arg.arg
            self.variables[name] = self.new_symbolic_var()

        for child in node.body:
            self.visit(child)

    """
    Control flow
    """

    def visit_If(self, node):
        self.scope = CurrentScope("if", node.end_lineno)

        if_cond = self.visit(node.test)
        if isinstance(if_cond, ArithRef):
            if_cond = if_cond > 0

        else_cond = simplify(Not(if_cond))

        # spawn a copy of this visitor to traverse the else branch
        else_visitor = UnreachablePathVisitor()
        else_visitor.variables = self.variables.copy()
        else_visitor.path_conds = self.path_conds.copy()
        else_visitor.output = self.output  # append to the same list instance
        else_visitor.symbol_idx = self.symbol_idx

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

        if len(node.orelse) == 0:  # no else branch, return
            self.check_for_return_raise(node)
            return

        solver.pop()
        solver.add(else_cond)

        if solver.check() == unsat:
            # no solution, else branch unreachable
            first_line = node.orelse[0]
            self.output.append(first_line.lineno)
        else:
            else_visitor.path_conds.append(else_cond)
            for child in node.orelse:
                else_visitor.visit(child)

            # merge the visitors together (maybe change to analyze all branches separately)
            for var_name in self.variables:
                if_result = self.variables[var_name]
                else_result = else_visitor.variables[var_name]

                # TODO: this currently blindly chooses the result of if branch, will need some
                #       more implementation changes to merge correctly (or make it traverse separately)
                self.variables[var_name] = if_result

    def visit_For(self, node):
        self.scope = CurrentScope(node.name, node.end_lineno)
        # TODO

        # for case where code block runs, add this
        self.check_for_return_raise(node)

        self.generic_visit(node)

    def visit_While(self, node):
        self.scope = CurrentScope(node.name, node.end_lineno)
        # TODO
        self.generic_visit(node)

    """
    Helpers
    """

    def new_symbolic_var(self):
        var = Const(self.symbol_prefix + str(self.symbol_idx), RealSort())
        self.symbol_idx += 1
        return var

    def check_for_return_raise(self, node):
        scope = self.scope
        if scope.return_exists:  # return statement inside if block
            scope.return_exists = False
            scope.edge_cases.append(node.end_lineno + 1)
            if scope.return_no < scope.end_no:
                scope.edge_cases.append(scope.return_no + 1)


class FunctionCollector(ast.NodeVisitor):
    def __init__(self):
        self.called_functions = {}
        self.called_functionsNames = set()
        self.defined_function = {}
        self.defined_functionNames = set()

    def visit_FunctionDef(self, node):
        self.defined_functionNames.add(node.name)
        self.defined_function[node.name] = node
        self.generic_visit(node)
        # return node.name  # stub

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called_functions[node.func.id] = node
            self.called_functionsNames.add(node.func.id)
        else:
            if isinstance(node.func, ast.Attribute):
                # dir(Solver)
                # TODO: add attribute object class defined functions
                self.called_functions[node.func.attr] = node
                self.called_functionsNames.add(node.func.attr)
        self.generic_visit(node)


def analyze_code(tree):
    z3_contents = dir(z3)
    z3_functions = set([name for name in z3_contents if callable(getattr(z3, name))])

    func_collector = FunctionCollector()

    func_collector.visit(tree)
    called_functions = func_collector.called_functions
    called_functionNames = func_collector.called_functionsNames
    defined_functionNames = func_collector.defined_functionNames

    built_in_functions = set(dir(builtins))
    valid_calls = called_functionNames & (defined_functionNames | built_in_functions | z3_functions)

    filtered_functions = {k: called_functions[k] for k in valid_calls if k in called_functions}
    filtered_functions.update(func_collector.defined_function)
    return filtered_functions


# @dataclass
# class FunctionInfo:
#     name: str
#     node: ast.FunctionDef
#     parameters: List[str] = field(default_factory=list)
#     start_line: int = 0


if __name__ == "__main__":
    '''
    for manual testing w/ debugger
    
    def func(x, y):
        if y < x:
            x = y
        else:
            x = 1
    '''
    code = 'def func(x, y):\n    if y < x:\n        x = y\n    else:\n        x = 1'

    tree = ast.parse(code)
    visitor = UnreachablePathVisitor()
    visitor.visit(tree)

    print(visitor.output)
