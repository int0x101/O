class ScopeStack:
    def __init__(self):
        self.scope_stack = [{}]

    def define(self, name, value):
        self.scope_stack[-1][name] = value

    def enter(self):
        self.scope_stack.append({})

    def leave(self):
        self.scope_stack.pop()

    def current(self):
        return self.scope_stack[-1]

    def resolve(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        raise NameError(f"Name {name} is not defined")
