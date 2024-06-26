import ast
from z3 import *


class UnreachablePathVisitor(ast.NodeVisitor):
    """
    variables_stack: a stack of dictionaries mapping variable names to its symbolic representation. each stack
        represents a scope. the symbolic representation may be a boolean or an arithmetic expression.
    functions_stack: a stack of dictionaries mapping function names to ast.FunctionDef nodes, used for traversing
        function calls. similarly to above, each stack represents a scope.
    path_conds: a stack of expressions representing path conditions.

    output: a set of line numbers that are deemed unreachable.

    whileloop_break_detector_stack: stack used for tracking if a reachable break exists inside a while loop.
    line_after_while_block: used to track the line no. of line right after a while block.
    """

    def __init__(self, parent=None):
        self.variables_stack: list[dict[str, ArithRef | BoolRef]] = [{}]
        self.functions_stack = [{}]
        self.path_conds: list[ast.expr] = []

        self.output: set[int] = set()
        self.whileloop_break_detector_stack = []
        self.line_after_while_block = None

        self.child_visitors = []
        self.parent = parent
        if parent is not None:
            parent.child_visitors.append(self)

        self.symbol_prefix = 'var'
        self.symbol_idx = 0

        self.return_flag = object()
        self.return_val = None

    """
    Root
    """

    def visit_Module(self, node):
        self.collect_functions(node.body)

        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                child = UnreachablePathVisitor(self)
                child.variables_stack = copy.deepcopy(self.variables_stack)
                child.functions_stack = copy.deepcopy(self.functions_stack)
                child.visit(stmt)
            else:
                self.visit(stmt)

        final_output = set()
        for visitor in [self] + self.child_visitors:
            final_output = final_output.union(visitor.output)

        ret = list(final_output)
        ret.sort()

        return ret

    """
    Definitions
    """

    def visit_FunctionDef(self, node):
        self.new_scope()
        self.collect_functions(node.body)

        for arg in node.args.args:
            name = arg.arg
            self.variables()[name] = self.new_symbolic_var()

        body = node.body
        for i, stmt in enumerate(body):
            curr_visitors = self.child_visitors.copy()

            for visitor in [self] + curr_visitors:
                ret = visitor.visit(stmt)

                if ret == visitor.return_flag:
                    if stmt.lineno < body[-1].lineno:
                        visitor.output.add(body[i + 1].lineno)

            # newly spawned visitors should have an identical output to the parent visitor
            for v_i in range(len(curr_visitors), len(self.child_visitors)):
                child = self.child_visitors[v_i]
                child.output = child.parent.output.copy()

        for visitor in self.child_visitors:
            self.output &= visitor.output

        # self.visit_until_return(node.body)
        self.teardown_scope()

    """
    Literals and variable names
    """

    def visit_Name(self, node):
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
                return Not(value)
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
    Control flow
    """

    def visit_If(self, node):
        if_block = node.body
        else_block = node.orelse
        test = node.test

        if_returned = False
        else_returned = False

        if_cond = self.visit(test)
        if isinstance(if_cond, ArithRef):
            if_cond = if_cond > 0

        else_cond = simplify(Not(if_cond))

        solver = Solver()
        for cond in self.path_conds:
            solver.add(self.visit(cond))

        solver.push()
        solver.add(if_cond)
        if_unreachable = solver.check() == unsat

        solver.pop()
        solver.add(else_cond)
        else_unreachable = solver.check() == unsat

        # save copies for the else-block's visitor
        else_visitor_variables = copy.deepcopy(self.variables_stack)
        else_visitor_functions = copy.deepcopy(self.functions_stack)
        else_visitor_path_conds = copy.deepcopy(self.path_conds)
        else_visitor_symbol_idx = self.symbol_idx

        if if_unreachable:
            # no solution, if branch unreachable
            first_line = if_block[0]
            self.output.add(first_line.lineno)
        else:
            self.path_conds.append(self.return_as_path_cond(test, True))
            if_returned = self.visit_until_return(if_block)

        if else_unreachable:
            # no solution, else branch unreachable
            else_returned = True

            if len(else_block) > 0:
                first_line = else_block[0]
                if isinstance(first_line, ast.If):
                    # elif present
                    self.output.add(first_line.lineno + 1)
                else:
                    self.output.add(first_line.lineno)
        else:
            if if_unreachable:
                # use this visitor to traverse the else branch
                else_visitor = self
            else:
                # spawn a copy of this visitor to traverse the else branch
                else_visitor = UnreachablePathVisitor(self)
                else_visitor.variables_stack = else_visitor_variables
                else_visitor.functions_stack = else_visitor_functions
                else_visitor.path_conds = else_visitor_path_conds
                else_visitor.output = self.output.copy()
                else_visitor.symbol_idx = else_visitor_symbol_idx

            else_visitor.path_conds.append(self.return_as_path_cond(test, False))
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
            solver.add(self.visit(cond))

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
            solver.add(self.visit(cond))

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
            solver.add(self.visit(cond))

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

    def return_as_path_cond(self, node, cond):
        ret = self.visit(node)

        # the return value of ast.parse will be wrapped in an ast.Module node
        # and an ast.Expr node as such:
        # Module(
        #     body=[
        #         Expr(
        #             value=<the ast.expr node we want>)],
        #     ...
        # )
        if isinstance(ret, BoolRef):
            if cond:
                return node
            else:
                return ast.parse('not ' + ast.unparse(node)).body[0].value
        elif isinstance(ret, ArithRef):
            if cond:
                return ast.parse(ast.unparse(node) + ' > 0').body[0].value
            else:
                return ast.parse(ast.unparse(node) + ' < 0').body[0].value

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
