from .symbol import Symbol

class Scope:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, type):
        symbol = Symbol(name, type)
        self.symbols[name] = symbol
        return symbol

    def resolve(self, name):
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol
        if self.parent is not None:
            return self.parent.resolve(name)
        return None

    def __repr__(self):
        return f"<Scope(symbols={self.symbols}, parent={self.parent})>"
