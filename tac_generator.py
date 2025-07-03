from ast_tree import *
from tac_instruction import *

class TempVar:
    def __init__(self):
        self.counter = 0

    def new_temp(self):
        name = f"t{self.counter}"
        self.counter += 1
        return name

class TACGenerator:
    def __init__(self, symbol_table):
        self.instructions = []
        self.temps = TempVar()
        self.symbol_table = symbol_table; 

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"Nenhum visitador TAC definido para {node.__class__.__name__}")

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)
        return self.instructions
    
    def visit_Decl(self, node):
        self.instructions.append(TACInstruction("alloc", 1, None, node.name))

    def visit_FunctionDecl(self, node):
        self.instructions.append(TACInstruction("label", None, None, node.name))
        for param_name, _ in node.params:
            # assume que cada parâmetro já está em uma variável correspondente
            self.instructions.append(TACInstruction("param", None, None, param_name))
        self.visit(node.body)

    def visit_AutoDecl(self, node):
        self.instructions.append(TACInstruction("alloc", 1, None, node.name))  # string
        value = self.visit(node.expr)
        self.instructions.append(TACInstruction("=", value, None, node.name))

    def visit_NamespaceDecl(self, node):
        for decl in node.declarations:
            self.visit(decl)

    def visit_ArrayDecl(self, node):
        size = self.visit(node.size)
        self.instructions.append(TACInstruction("alloc", size, None, node.name))

    def visit_ArrayAccess(self, node):
        index = self.visit(node.index)
        temp = self.temps.new_temp()
        self.instructions.append(TACInstruction("load", f"{node.name}", index, temp))
        return temp

    def visit_ExprStmt(self, node):
        self.visit(node.expr)

    def visit_Assign(self, node):
        value = self.visit(node.expr)
        if isinstance(node.name, VarRef):
            self.instructions.append(TACInstruction("=", value, None, node.name.name))
        elif isinstance(node.name, ArrayAccess):
            index = self.visit(node.name.index)
            self.instructions.append(TACInstruction("store", value, index, node.name.name))
        else:
            raise Exception(f"Tipo de destino inválido em Assign: {type(node.name)}")

    def visit_If(self, node):
        cond = self.visit(node.condition)
        label_else = f"L{self.temps.new_temp()}"
        label_end = f"L{self.temps.new_temp()}"

        self.instructions.append(TACInstruction("ifz", cond, None, label_else))
        self.visit(node.then_branch)
        self.instructions.append(TACInstruction("goto", None, None, label_end))
        self.instructions.append(TACInstruction("label", None, None, label_else))
        if node.else_branch:
            self.visit(node.else_branch)
        self.instructions.append(TACInstruction("label", None, None, label_end))

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.temps.new_temp()
        self.instructions.append(TACInstruction(node.op, left, right, temp))
        return temp

    def visit_VarRef(self, node):
        return node.name

    def visit_QualifiedRef(self, node):
        return f"{node.namespace}.{node.name}"

    def visit_Literal(self, node):
        # label = self.symbol_table.register_literal(node)
        # self.instructions.append(TACInstruction("alloc", None, None, label))     
        # self.instructions.append(TACInstruction('literal_init', node.value, None, label))  
        return node.value

    def visit_TypeCast(self, node):
        value = self.visit(node.expr)
        temp = self.temps.new_temp()
        self.instructions.append(TACInstruction("cast_" + node.target_type, value, None, temp))
        return temp

    def visit_Call(self, node):
        for arg in node.args:
            if isinstance(arg, Literal):
                self.instructions.append(TACInstruction("arg", arg))  # passa o nó Literal
            elif isinstance(arg, VarRef):
                self.instructions.append(TACInstruction("arg", arg))  # passa o nó VarRef
            else:
                temp = self.visit(arg)  # para BinaryOp, Call aninhada, etc.
                self.instructions.append(TACInstruction("arg", temp))

        temp = self.temps.new_temp()
        self.instructions.append(TACInstruction("call", node.name, len(node.args), temp))
        return temp
    
    def visit_Print(self, node):
        for arg in node.args:
            if isinstance(arg, Literal):
                self.instructions.append(TACInstruction("arg", arg))  # passa o nó Literal
            elif isinstance(arg, VarRef):
                self.instructions.append(TACInstruction("arg", arg))  # passa o nó VarRef
            else:
                temp = self.visit(arg)  # para BinaryOp, Call aninhada, etc.
                self.instructions.append(TACInstruction("arg", temp))

        self.instructions.append(TACInstruction("PRINT"))

    def visit_Halt(self, node):
        self.instructions.append(TACInstruction("HALT"))
            
    
    def visit_Return(self, node):
        value = self.visit(node.expr)
        self.instructions.append(TACInstruction("ret", value))










