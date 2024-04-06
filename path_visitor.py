import ast
from z3 import *
import builtins


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
        self.defined_functions = {}

        self.symbol_prefix = 'var'
        self.symbol_idx = 0

    """
    Root
    """

    def visit_Module(self, node):
        # TODO
        self.func_nodes.update(analyze_code(node))
        self.generic_visit(node)

    """
    Literals and variable names
    """

    def visit_Name(self, node):
        if (node.id not in self.variables):
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
                    elif isinstance(arg, ast.Call):
                        prepared_args.append(arg.func)
                    else:
                        self.generic_visit(arg)

                handler = self.func_nodes[func_name]
                if None in prepared_args:
                    self.output.append(node.lineno)

                if hasattr(handler.args, 'args'):
                    num_required_arguments = len(handler.args.args)
                    count_func = len([elem for elem in handler.args.args if isinstance(elem, ast.Call)])
                else:
                    num_required_arguments = len(handler.args)
                    count_func = len([elem for elem in handler.args if isinstance(elem, ast.Call)])

                if num_required_arguments != len(prepared_args):
                    if (num_required_arguments - count_func) != len(prepared_args):
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
        # TODO
        self.generic_visit(node)

    def visit_Raise(self, node):
        # TODO
        self.generic_visit(node)

    """
    Definitions
    """

    def visit_FunctionDef(self, node):
        # function_name = node.name
        # parameters = [param.arg for param in node.args.args]  # Collecting parameter names
        # start_line = node.lineno
        # self.func_nodes[function_name] = node
        #     # FunctionInfo(name=function_name, node=node, parameters=parameters,
        #     #                                               start_line=start_line)
        for arg in node.args.args:
            name = arg.arg
            self.variables[name] = self.new_symbolic_var()

        for child in node.body:
            self.visit(child)

    """
    Control flow
    """

    def visit_If(self, node):
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

                # TODO: fix this
                self.variables[var_name] = Or(if_result, else_result)

    def visit_For(self, node):
        # TODO
        self.generic_visit(node)
        # self.visit(node.iter)

    def visit_While(self, node):
        # TODO
        self.generic_visit(node)

    """
    Helpers
    """

    def new_symbolic_var(self):
        var = Const(self.symbol_prefix + str(self.symbol_idx), RealSort())
        self.symbol_idx += 1
        return var


class FunctionCollector(ast.NodeVisitor):
    def __init__(self):
        self.current_class = None
        self.called_functions = {}
        self.called_functionsNames = set()
        self.defined_function = {}
        self.defined_functionNames = set()
        self.constructor_calls = {}
        self.instance_calls = {}
        self.defined_class = {}

    def visit_Assign(self, node):
        # Check for constructor calls (e.g. s.add())
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.constructor_calls[target.id] = node.value.func.id
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.defined_class[node.name] = []
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        for class_name in self.defined_class:
            if self.current_class == class_name:
                self.defined_class[class_name].append(node.name)
        self.defined_functionNames.add(node.name)
        self.defined_function[node.name] = node
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called_functions[node.func.id] = node
            self.called_functionsNames.add(node.func.id)
        else:
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                obj = node.func.value.id
                method = node.func.attr
                if obj in self.constructor_calls:
                    self.instance_calls[self.constructor_calls[obj]] = method
                    self.called_functions[node.func.attr] = node
                    self.called_functionsNames.add(node.func.attr)
        self.generic_visit(node)


def analyze_code(tree):
    built_in_functions = set(dir(builtins))
    z3_contents = dir(z3)
    z3_functions = set([name for name in z3_contents if callable(getattr(z3, name))])

    func_collector = FunctionCollector()
    func_collector.visit(tree)

    called_functions = func_collector.called_functions
    called_function_names = func_collector.called_functionsNames
    defined_function_names = func_collector.defined_functionNames
    defined_instance_methods = set(name for name in func_collector.constructor_calls)
    defined_class_names = set(name for name in func_collector.defined_class)
    for method in func_collector.instance_calls:
        try:
            attribute_of_function = getattr(z3, method)
            if attribute_of_function:
                if callable(attribute_of_function):
                    defined_instance_methods.update(dir(attribute_of_function))
        except AttributeError:
            if method in func_collector.defined_class:
                defined_instance_methods.update(func_collector.defined_class[method])

    valid_calls = called_function_names & (defined_function_names | built_in_functions
                                           | z3_functions | defined_instance_methods | defined_class_names)

    filtered_functions = {k: called_functions[k] for k in valid_calls if k in called_functions}
    filtered_functions.update(func_collector.defined_function)

    return filtered_functions

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
