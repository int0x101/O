from .scope import Scope


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope

    def analyze(self, node):
        method_name = f"analyze_{node[0]}"
        method = getattr(self, method_name, self.generic_analyze)
        return method(node)

    def generic_analyze(self, node):
        for child in node[1:]:
            if isinstance(child, tuple):
                self.analyze(child)

    def analyze_identifier(self, node):
        _, name = node
        symbol = self.global_scope.resolve(name)
        if symbol is None:
            raise Exception(f"Undefined variable '{name}'")

    def analyze_binop(self, node):
        _, _, left, right = node
        self.analyze(left)
        self.analyze(right)

    def analyze_comparison(self, node):
        _, _, left, right = node
        self.analyze(left)
        self.analyze(right)

    def analyze_var_def(self, node):
        _, type, name, *rest = node
        self.current_scope.define(name, type)

    def analyze_assignment(self, node):
        _, name, value = node
        symbol = self.current_scope.resolve(name)
        if symbol is None:
            raise Exception(f"Undefined variable '{name}'")
        self.analyze(value)
        if symbol.type.startswith(value[0]):
            raise Exception(
                f"Type mismatch: cannot assign {
                            value[0]} to {symbol[0]}"
            )

    def analyze_enum_def(self, node):
        _, name, values = node
        self.current_scope.define(name, ("enum", values))

    def analyze_lambda(self, node):
        _, params, body = node
        # Set parent to current scope
        function_scope = Scope(parent=self.current_scope)
        for param in params:
            function_scope.define(param[1], param[0])
        previous_scope = self.current_scope
        self.current_scope = function_scope
        self.analyze(body)
        self.current_scope = previous_scope

    def analyze_fun_def(self, node):
        _, _, rtype, name, params, body = node
        self.current_scope.define(name, ("function", rtype))
        # Set parent to current scope
        function_scope = Scope(parent=self.current_scope)
        for param in params:
            function_scope.define(param[1], param[0])
        previous_scope = self.current_scope
        self.current_scope = function_scope
        for statement in body:
            self.analyze(statement)
        self.current_scope = previous_scope

    def analyze_class_def(self, node):
        _, name, *body = node
        self.current_scope.define(name, ("class", body))
        class_scope = Scope(parent=self.current_scope)
        previous_scope = self.current_scope
        self.current_scope = class_scope
        for statement in body:
            self.analyze(statement)
        self.current_scope = previous_scope

    def analyze_when_stmts(self, node):
        _, *cases = node
        for case in cases:
            self.analyze(case)

    def analyze_when(self, node):
        _, condition, body = node
        self.analyze(condition)
        for statement in body:
            self.analyze(statement)

    def analyze_return(self, node):
        _, value = node
        self.analyze(value)

    def analyze_pass(self, node):
        pass
