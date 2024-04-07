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
    whileloop_break_detector_stack: stack used for tracking if an reachable break exists inside a while loop.
    line_after_while_block: used to track the line no. of line right after a while block.
    """

    def __init__(self, all_visitors=None):
        self.variables_stack: list[dict[str, ArithRef | BoolRef]] = [{}]
        self.functions_stack = [{}]
        self.path_conds: list[BoolRef] = []

        self.output: set[int] = set()
        self.whileloop_break_detector_stack = []
        self.line_after_while_block = None

        if all_visitors is None:
            self.all_visitors = [self]
        else:
            all_visitors.append(self)
            self.all_visitors = all_visitors

        self.symbol_prefix = 'var'
        self.symbol_idx = 0

        self.return_flag = object()
        self.return_val = None

    """
    Root
    """

    def visit_Module(self, node):
        # self.func_nodes.update(analyze_code(node))
        self.collect_functions(node.body)
        visitors = self.all_visitors

        for stmt in node.body:
            curr_visitors = len(visitors)
            for i in range(curr_visitors):
                visitors[i].visit(stmt)

            # newly spawned visitors should have an identical
            # output to the root visitor
            for i in range(curr_visitors, len(visitors)):
                visitors[i].output = self.output.copy()

        for visitor in self.all_visitors:
            self.output &= visitor.output

        final_output = list(self.output)
        final_output.sort()

        return final_output

    """
    Literals and variable names
    """

    def visit_Name(self, node):
        # if node.id not in self.func_variables:
        #     return "temp"
        return self.variables()[node.id]

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
        if not isinstance(node.func, ast.Name):
            # unsupported
            return

        func = self.get_function(node.func.id)
        if func is None:
            return

        args = [self.visit(arg) for arg in node.args]

        self.new_scope()

        for i, param in enumerate(func.args.args):
            self.variables()[param.arg] = args[i]

        self.visit_until_return(func.body)
        self.teardown_scope()

        return self.return_val

    def visit_UnaryOp(self, node):
        op = node.op
        value = self.visit(node.operand)

        match type(op):
            case ast.USub:
                return -value
            case ast.UAdd:
                return +value
            case ast.Not:
                return not value
            case _:
                # unsupported operations
                return None

    def visit_BinOp(self, node):
        left, right = self.visit(node.left), self.visit(node.right)
        op = node.op

        match type(op):
            case ast.Add:
                return left + right
            case ast.Sub:
                return left - right
            case ast.Mult:
                return left * right
            case ast.Div:
                return left / right
            case ast.Pow:
                return left ** right
            case _:
                # unsupported operations
                return None

    def visit_BoolOp(self, node):
        op = node.op
        values = [self.visit(n) for n in node.values]

        match type(op):
            case ast.Or:
                return Or(*values)
            case ast.And:
                return And(*values)

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
                    # unsupported operations
                    pass

        return simplify(And(*eqs))

    """
    Statements
    """

    def visit_Assign(self, node):
        rhs = self.visit(node.value)

        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables()[target.id] = rhs

    def visit_AugAssign(self, node):
        # TODO
        self.generic_visit(node)

    def visit_Return(self, node):
        if node.value:
            self.return_val = self.visit(node.value)
        return self.return_flag

    def visit_Raise(self, node):
        return self.return_flag

    """
    Definitions
    """

    def visit_FunctionDef(self, node):
        self.new_scope()
        self.collect_functions(node.body)

        for arg in node.args.args:
            name = arg.arg
            self.variables()[name] = self.new_symbolic_var()

        self.visit_until_return(node.body)
        self.teardown_scope()

    """
    Control flow
    """

    def visit_If(self, node):
        if_block = node.body
        else_block = node.orelse

        if_returned = False
        else_returned = False

        if_cond = self.visit(node.test)
        if isinstance(if_cond, ArithRef):
            if_cond = if_cond > 0

        # save copies for the else-visitor
        else_visitor_variables = self.variables_stack.copy()
        else_visitor_functions = self.functions_stack.copy()
        else_visitor_path_conds = self.path_conds.copy()
        else_visitor_symbol_idx = self.symbol_idx

        solver = Solver()
        for cond in self.path_conds:
            solver.add(cond)

        solver.push()
        solver.add(if_cond)

        if solver.check() == unsat:
            # no solution, if branch unreachable
            first_line = if_block[0]
            self.output.add(first_line.lineno)

            # use this visitor to traverse the else branch
            else_visitor = self
        else:
            self.path_conds.append(if_cond)
            if_returned = self.visit_until_return(if_block)

            # spawn a copy of this visitor to traverse the else branch
            else_visitor = UnreachablePathVisitor(self.all_visitors)
            else_visitor.variables_stack = else_visitor_variables
            else_visitor.functions_stack = else_visitor_functions
            else_visitor.path_conds = else_visitor_path_conds
            else_visitor.output = self.output.copy()
            else_visitor.symbol_idx = else_visitor_symbol_idx

        else_cond = simplify(Not(if_cond))

        solver.pop()
        solver.add(else_cond)

        if solver.check() == unsat:
            # no solution, else branch unreachable
            else_returned = True

            if len(else_block) > 0:
                first_line = else_block[0]
                else_visitor.output.add(first_line.lineno)
        elif len(else_block) > 0:
            else_visitor.path_conds.append(else_cond)
            else_returned = else_visitor.visit_until_return(else_block)

        output_union = self.output.union(else_visitor.output)
        self.output = output_union
        else_visitor.output = output_union.copy()

        if if_returned and else_returned:
            return self.return_flag

    def visit_For(self, node):
        for_block = node.body

        if not isinstance(node.iter, ast.Call) or node.iter.func.id != "range":
            print("Warning: Unsupported for-loop iterable encountered.")
            return

        # case 1: check if we can enter for-loop.
        lhs = self.visit(node.iter.args[0])
        rhs = self.visit(node.iter.args[1])

        solver = Solver()
        for cond in self.path_conds:
            solver.add(cond)

        solver.push()
        solver.add(rhs > lhs)

        if solver.check() == unsat:
            # no solution, loop body unreachable.
            first_line = for_block[0]
            self.output.add(first_line.lineno)

    def visit_While(self, node):
        while_block = node.body
        else_block = node.orelse

        # used to check if we can ENTER loop
        if_cond = self.visit(node.test)

        if isinstance(if_cond, ArithRef):
            if_cond = if_cond > 0

        # used for checking if we can EXIT loop
        else_cond = simplify(Not(if_cond))

        solver = Solver()
        for cond in self.path_conds:
            solver.add(cond)

        solver.push()
        solver.add(if_cond)

        if solver.check() == unsat:
            # while loop body unreachable.
            first_line = while_block[0]
            self.output.add(first_line.lineno)
        else:
            # while loop body reachable.
            solver.pop()
            solver.add(else_cond)

            if solver.check() == unsat:
                # case where cond is always true, and we can't leave without a reachable break.

                if len(else_block) == 1:
                    # else block exists and is unreachable.
                    first_line = else_block[0]
                    self.output.add(first_line.lineno)

                self.whileloop_break_detector_stack.append(False)

                for line in while_block:
                    self.visit(line)

                if not self.whileloop_break_detector_stack.pop():
                    # all code after while_loop body is unreachable.
                    self.output.add(node.end_lineno + 1)

    def visit_Break(self, node):
        if len(self.whileloop_break_detector_stack) == 0:
            return

        solver = Solver()
        for cond in self.path_conds:
            solver.add(cond)

        solver.push()
        if solver.check() == sat:
            # this break is reachable, update the stack.
            self.whileloop_break_detector_stack.pop()
            self.whileloop_break_detector_stack.append(True)

    """
    Helpers
    """

    def new_symbolic_var(self):
        var = Const(self.symbol_prefix + str(self.symbol_idx), RealSort())
        self.symbol_idx += 1
        return var

    def visit_until_return(self, block):
        returned = False

        for i, stmt in enumerate(block):
            ret = self.visit(stmt)
            if ret == self.return_flag:
                returned = True

                if stmt.lineno < block[-1].lineno:
                    self.output.add(block[i + 1].lineno)

                break

        return returned

    def collect_functions(self, body):
        function_collector = FunctionCollector()
        self.functions_stack[-1] = function_collector.collect(body)

    def variables(self):
        return self.variables_stack[-1]

    def get_function(self, name):
        for scope in reversed(self.functions_stack):
            if name in scope:
                return scope[name]
        else:
            return None

    def new_scope(self):
        self.variables_stack.append({})
        self.functions_stack.append({})

    def teardown_scope(self):
        self.variables_stack.pop()
        self.functions_stack.pop()


class FunctionCollector(ast.NodeVisitor):
    def __init__(self):
        self.output = {}

    def collect(self, body):
        for stmt in body:
            self.visit(stmt)

        return self.output

    def visit_FunctionDef(self, node):
        self.output[node.name] = node


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
    v = UnreachablePathVisitor()
    v.visit(tree)

    print(v.output)
