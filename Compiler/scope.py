class ScopeStack:
    def __init__(self):
        self.scope_stack = [{}]

    def enter_scope(self):
        self.scope_stack.append({})

    def exit_scope(self):
        self.scope_stack.pop()

    def current_scope(self):
        return self.scope_stack[-1]

    def resolve(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        raise NameError(f"Name {name} is not defined")
