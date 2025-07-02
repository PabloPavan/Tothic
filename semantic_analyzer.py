from semantic_error import *
from symbol_table import *
from ast_tree import *

class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable()
        self.literal_count = 0

        self.global_scope.symbols["print"] = Symbol(
            name="PRINT",
            typ="func",
            scope=self.global_scope.scope_name,
            params=[("value", None)],
            return_type="void"
        )
        self.global_scope.symbols["halt"] = Symbol(
            name="HALT",
            typ="func",
            scope=self.global_scope.scope_name,
            params=[],
            return_type="void"
        )
        self.current_scope = self.global_scope

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"Nenhum visitador definido para {node.__class__.__name__}")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_NamespaceDecl(self, node):
        new_scope = SymbolTable(parent=self.current_scope, scope_name=node.name)
        old_scope = self.current_scope
        self.current_scope = new_scope
        for decl in node.declarations:
            self.visit(decl)
        self.current_scope = old_scope

    def visit_Decl(self, node):
        self.current_scope.insert(node.name, node.type)

    def visit_FunctionDecl(self, node):
        self.current_scope.symbols[node.name] = Symbol(
            name=node.name,
            typ="func",
            scope=self.current_scope.scope_name,
            params=node.params,
            return_type=node.return_type
        )
        func_scope = SymbolTable(parent=self.current_scope, scope_name=node.name)
        for param_name, param_type in node.params:
            func_scope.insert(param_name, param_type)
        old_scope = self.current_scope
        self.current_scope = func_scope
        self.visit(node.body)
        self.current_scope = old_scope

    def visit_ArrayDecl(self, node):
        self.visit(node.size)
        self.current_scope.insert(node.name, f"{node.type}[]")

    def visit_AutoDecl(self, node):
        expr_type = self.visit(node.expr)
        self.current_scope.insert(node.name, expr_type)

    def visit_ExprStmt(self, node):
        return self.visit(node.expr)

    def visit_Assign(self, node):
        if isinstance(node.name, ArrayAccess):
            array_symbol = self.current_scope.lookup(node.name.name)
            if not array_symbol.type.endswith("[]"):
                raise SemanticError(f"'{node.name.name}' não é um array")
            element_type = array_symbol.type[:-2]
            index_type = self.visit(node.name.index)
            if index_type != "int":
                raise SemanticError("O índice do array deve ser do tipo 'int'")
            expr_type = self.visit(node.expr)
            if element_type != expr_type:
                raise SemanticError(f"Tipo incompatível na atribuição ao array: esperado {element_type}, encontrado {expr_type}")
        else:
            var = self.current_scope.lookup(node.name.name)
            expr_type = self.visit(node.expr)
            if var.type != expr_type:
                raise SemanticError(f"Incompatibilidade de tipos: variável '{node.name}' é '{var.type}', mas expressão é '{expr_type}'")

    def visit_If(self, node):
        cond_type = self.visit(node.condition)
        if cond_type != "bool":
            raise SemanticError("Condição do if deve ser do tipo 'bool'")
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_BinaryOp(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        if node.op in {'+', '-', '*', '/'}:
            if left_type != right_type:
                raise SemanticError(f"Operação '{node.op}' entre tipos incompatíveis: {left_type} e {right_type}")
            return left_type
        elif node.op in {'==', '!=', '<', '>', '<=', '>='}:
            return "bool"
        elif node.op in {'&&', '||'}:
            if left_type != "bool" or right_type != "bool":
                raise SemanticError(f"Operadores lógicos requerem booleanos, mas obtido {left_type} e {right_type}")
            return "bool"
        else:
            raise SemanticError(f"Operador desconhecido: {node.op}")

    def visit_VarRef(self, node):
        symbol = self.current_scope.lookup(node.name)
        return symbol.type

    def visit_ArrayAccess(self, node):
        symbol = self.current_scope.lookup(node.name)
        if not symbol.type.endswith("[]"):
            raise SemanticError(f"'{node.name}' não é um array")
        self.visit(node.index)
        return symbol.type[:-2]

    def visit_QualifiedRef(self, node):
        # Simulação simplificada — assume símbolo como válido
        return "float"  # Ex: math.pi

    def visit_Literal(self, node):
        self.global_scope.register_literal(node)
        return node.type

    def visit_TypeCast(self, node):
        self.visit(node.expr)
        return node.target_type
    
    def visit_Call(self, node):
        symbol = self.current_scope.lookup(node.name)
        if symbol.type != "func":
            raise SemanticError(f"'{node.name}' não é uma função")
        if len(symbol.params) != len(node.args):
            raise SemanticError(f"Função '{node.name}' espera {len(symbol.params)} argumentos, mas recebeu {len(node.args)}")
        for (arg_expr, (param_name, param_type)) in zip(node.args, symbol.params):
            arg_type = self.visit(arg_expr)
            if arg_type != param_type:
                raise SemanticError(f"Tipo do argumento '{param_name}' deve ser '{param_type}', mas foi '{arg_type}'")
        return symbol.return_type 

    def visit_Print(self, node):
        symbol = self.current_scope.lookup(node.name)
        if len(symbol.params) != len(node.args):
            raise SemanticError(f"Função '{node.name}' espera {len(symbol.params)} argumentos, mas recebeu {len(node.args)}")
        return symbol.return_type 

    def visit_Halt(self, node):
        symbol = self.current_scope.lookup(node.name)
        return symbol.return_type       

    def visit_Return(self, node):
        self.visit(node.expr)  
        return "void"  

