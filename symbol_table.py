from semantic_error import *

class Symbol:
    def __init__(self, name, typ, scope, params=None, return_type=None, category="var", value=None):
        self.name = name
        self.type = typ
        self.scope = scope
        self.params = params or []
        self.return_type = return_type
        self.category = category
        self.value = value

    def __repr__(self):
        if self.type == "func":
            sig = ", ".join(f"{n}:{t}" for n, t in self.params)
            return f"{self.name}({sig}) -> {self.return_type} [{self.scope}]"
        
        return f"{self.name}:{self.type} ({self.scope}) ({self.category})"

class SymbolTable:
    def __init__(self, parent=None, scope_name="global"):
        self.symbols = {}
        self.parent = parent
        self.scope_name = scope_name
        self.literal_count = 0

    def insert(self, name, typ, category = "var", value = None):
        if name in self.symbols:
            raise SemanticError(f"Identificador '{name}' já declarado no escopo '{self.scope_name}'")
        self.symbols[name] = Symbol(name, typ, self.scope_name, None, None, category, value)

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            raise SemanticError(f"Identificador '{name}' não declarado no escopo '{self.scope_name}'")
        
    def VMlookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.VMlookup(name)
    
    def register_literal(self, node):
        for sym in self.symbols.values():
            if sym.category == 'literal' and sym.value == node.value:
                return sym.name 

        label = f"literal_{self.literal_count}"
        self.literal_count += 1
        self.insert(name=label, typ=node.type, category="literal", value=node.value)
        return label

    def __repr__(self):
        return f"Escopo '{self.scope_name}': {list(self.symbols.values())}"

