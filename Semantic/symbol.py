class Symbol:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"<Symbol(name={self.name}, type={self.type})>"
