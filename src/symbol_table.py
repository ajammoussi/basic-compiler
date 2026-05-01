class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name, var_type, line=None, column=None):
        current_scope = self.scopes[-1]
        if name in current_scope:
            return False, f"Variable '{name}' already declared in this scope"
        current_scope[name] = {'type': var_type, 'line': line, 'column': column}
        return True, None

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def get_type(self, name):
        symbol = self.lookup(name)
        if symbol:
            return symbol['type']
        return None

    def is_declared(self, name):
        return self.lookup(name) is not None

    def is_in_current_scope(self, name):
        return name in self.scopes[-1]