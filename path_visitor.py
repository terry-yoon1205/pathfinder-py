import ast


class UnreachablePathVisitor(ast.NodeVisitor):
    variables = {}
    function_nodes = {}
    output = []     # line numbers

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
        # TODO
        return self.variables[node.id]

    def visit_Attribute(self, node):
        # TODO
        self.generic_visit(node)

    def visit_Subscript(self, node):
        # TODO
        self.generic_visit(node)

    def visit_Constant(self, node):
        # TODO
        self.generic_visit(node)

    def visit_List(self, node):
        # TODO
        self.generic_visit(node)

    def visit_Tuple(self, node):
        # TODO
        self.generic_visit(node)

    def visit_Dict(self, node):
        # TODO
        self.generic_visit(node)

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
        # TODO
        value = self.visit(node.value)

        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables[target.id] = value

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
    def visit_Name(self, node):
        return node.id  # stub
