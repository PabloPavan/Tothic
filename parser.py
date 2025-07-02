from ast_tree import *

class SyntaxError(Exception): pass

class Parser:
    def __init__(self, token_stream):
        self.tokens = token_stream

    def match(self, type_, *values):
        tok = self.tokens.peek()
        return tok and tok.type == type_ and (tok.value in values if values else True)

    def parse_program(self):
        namespaces = []
        while self.tokens.peek() is not None:
            namespaces.append(self.parse_namespace())
        return Program(namespaces)

    def parse_namespace(self):
        self.tokens.expect("NAMESPACE")
        name_tok = self.tokens.expect("IDENT")
        self.tokens.expect("OP")
        if self.tokens.peek(-1).value != "{":
            raise SyntaxError("Esperado '{'")
        declarations = []
        while True:
            tok = self.tokens.peek()
            if tok is None:
                raise SyntaxError("Fim inesperado do namespace")
            if tok.type == "OP" and tok.value == "}":
                self.tokens.consume()
                break

            stmt = self.parse_declaration()
            if isinstance(stmt, list):
                declarations.extend(stmt)
            else:
                declarations.append(stmt)
        return NamespaceDecl(name_tok.value, declarations)

    def parse_declaration(self):
        tok = self.tokens.peek()
        if tok.type in {"INT", "FLOAT", "BOOL", "STRING"}:
            if self.tokens.peek(2) and self.tokens.peek(2).value == "(":
                return self.parse_function_decl()
            return self.parse_decl_or_array()
        elif tok.type == "AUTO":
            return self.parse_auto_decl()
        elif tok.type == "IF":
            return self.parse_if()
        elif tok.type == "OP" and tok.value == "{":
            return self.parse_block()
        elif tok.type == "IDENT":
            return self.parse_assign()
        elif tok.type == "RETURN":
            return self.parse_return()
        else:
            expr = self.parse_expr()
            self.tokens.expect("OP")
            if self.tokens.peek(-1).value != ";":
                raise SyntaxError("Esperado ';' após expressão")
            return ExprStmt(expr)

    def parse_decl_or_array(self):
        type_tok = self.tokens.consume()
        name_tok = self.tokens.expect("IDENT")
        if self.tokens.peek().type == "OP" and self.tokens.peek().value == "[":
            self.tokens.consume()
            size_expr = self.parse_expr()
            self.tokens.expect("OP")
            if self.tokens.peek(-1).value != "]":
                raise SyntaxError("Esperado ']'")
            self.tokens.expect("OP")
            if self.tokens.peek(-1).value != ";":
                raise SyntaxError("Esperado ';'")
            return ArrayDecl(name_tok.value, type_tok.value, size_expr)
        else:
            if self.tokens.peek().type == "OP" and self.tokens.peek().value == "=":
                self.tokens.consume()  # consome '='
                expr = self.parse_expr()
                self.tokens.expect("OP")
                if self.tokens.peek(-1).value != ";":
                    raise SyntaxError("Esperado ';'")
                return [Decl(name_tok.value, type_tok.value), Assign(VarRef(name_tok.value), expr)]
            else:
                self.tokens.expect("OP")
                if self.tokens.peek(-1).value != ";":
                    raise SyntaxError("Esperado ';'")
                return Decl(name_tok.value, type_tok.value)
        
    def parse_function_decl(self):
        return_type = self.tokens.consume().value
        name = self.tokens.expect("IDENT").value
        self.tokens.expect("OP")
        if self.tokens.peek(-1).value != "(":
            raise SyntaxError("Esperado '(' após nome da função")

        params = []
        if self.tokens.peek().type in {"INT", "FLOAT", "BOOL", "STRING"}:
            while True:
                param_type = self.tokens.consume().value
                param_name = self.tokens.expect("IDENT").value
                params.append((param_name, param_type))
                if self.tokens.peek().type == "OP" and self.tokens.peek().value == ",":
                    self.tokens.consume()
                else:
                    break

        self.tokens.expect("OP")
        if self.tokens.peek(-1).value != ")":
            raise SyntaxError("Esperado ')' após parâmetros da função")

        body = self.parse_block()
        return FunctionDecl(name=name, params=params, return_type=return_type, body=body)

    def parse_auto_decl(self):
        self.tokens.consume()
        name_tok = self.tokens.expect("IDENT")
        self.tokens.expect("OP")
        if self.tokens.peek(-1).value != "=":
            raise SyntaxError("Esperado '='")
        expr = self.parse_expr()
        self.tokens.expect("OP")
        if self.tokens.peek(-1).value != ";":
            raise SyntaxError("Esperado ';'")
        return AutoDecl(name_tok.value, expr)

    def parse_assign(self):
        tok = self.tokens.peek()
        if tok.type != "IDENT":
            raise SyntaxError("Esperado identificador no início da atribuição")
        ident = self.tokens.consume().value

        if self.tokens.peek() and self.tokens.peek().type == "OP" and self.tokens.peek().value == "[":
            # Atribuição em array
            self.tokens.consume()
            index = self.parse_expr()
            self.tokens.expect("OP")
            if self.tokens.peek(-1).value != "]":
                raise SyntaxError("Esperado ']' no acesso ao array")
            self.tokens.expect("OP")
            if self.tokens.peek(-1).value != "=":
                raise SyntaxError("Esperado '=' em atribuição")
            expr = self.parse_expr()
            self.tokens.expect("OP")
            if self.tokens.peek(-1).value != ";":
                raise SyntaxError("Esperado ';' no final da atribuição")
            return Assign(ArrayAccess(ident, index), expr)
        else:
            self.tokens.expect("OP")
            if self.tokens.peek(-1).value != "=":
                raise SyntaxError("Esperado '='")
            expr = self.parse_expr()
            self.tokens.expect("OP")
            if self.tokens.peek(-1).value != ";":
                raise SyntaxError("Esperado ';'")
            return Assign(VarRef(ident), expr)
        
    def parse_return(self):
        self.tokens.expect("RETURN")
        expr = self.parse_expr()
        self.tokens.expect("OP")
        if self.tokens.peek(-1).value != ";":
            raise SyntaxError("Esperado ';' após return")
        return Return(expr)

    def parse_block(self):
        self.tokens.expect("OP")
        if self.tokens.peek(-1).value != "{":
            raise SyntaxError("Esperado '{'")
        statements = []
        while True:
            tok = self.tokens.peek()
            if tok is None:
                raise SyntaxError("Fim inesperado no bloco")
            if tok.type == "OP" and tok.value == "}":
                self.tokens.consume()
                break
            stmt = self.parse_declaration()
            if isinstance(stmt, list):
                statements.extend(stmt)
            else:
                statements.append(stmt)

        return Block(statements)

    def parse_if(self):
        self.tokens.expect("IF")
        self.tokens.expect("OP")
        if self.tokens.peek(-1).value != "(":
            raise SyntaxError("Esperado '('")
        condition = self.parse_expr()
        self.tokens.expect("OP")
        if self.tokens.peek(-1).value != ")":
            raise SyntaxError("Esperado ')'")
        then_branch = self.parse_block()
        else_branch = None
        if self.tokens.peek() and self.tokens.peek().type == "ELSE":
            self.tokens.consume()
            else_branch = self.parse_block()
        return If(condition, then_branch, else_branch)

    def parse_expr(self): return self.parse_logical_or()

    def parse_logical_or(self):
        expr = self.parse_logical_and()
        while self.match("OP", "||"):
            op = self.tokens.consume().value
            right = self.parse_logical_and()
            expr = BinaryOp(op, expr, right)
        return expr

    def parse_logical_and(self):
        expr = self.parse_equality()
        while self.match("OP", "&&"):
            op = self.tokens.consume().value
            right = self.parse_equality()
            expr = BinaryOp(op, expr, right)
        return expr

    def parse_equality(self):
        expr = self.parse_relational()
        while self.match("OP", "==", "!="):
            op = self.tokens.consume().value
            right = self.parse_relational()
            expr = BinaryOp(op, expr, right)
        return expr

    def parse_relational(self):
        expr = self.parse_additive()
        while self.match("OP", "<", ">", "<=", ">="):
            op = self.tokens.consume().value
            right = self.parse_additive()
            expr = BinaryOp(op, expr, right)
        return expr

    def parse_additive(self):
        expr = self.parse_multiplicative()
        while self.match("OP", "+", "-"):
            op = self.tokens.consume().value
            right = self.parse_multiplicative()
            expr = BinaryOp(op, expr, right)
        return expr

    def parse_multiplicative(self):
        expr = self.parse_unary()
        while self.match("OP", "*", "/"):
            op = self.tokens.consume().value
            right = self.parse_unary()
            expr = BinaryOp(op, expr, right)
        return expr

    def parse_unary(self):
        if self.match("OP", "-", "!"):
            op = self.tokens.consume().value
            expr = self.parse_unary()
            return BinaryOp(op, Literal(0, "int"), expr)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.tokens.peek()
        if tok.type == "INT_LITERAL":
            self.tokens.consume()
            return Literal(int(tok.value), "int")
        elif tok.type == "FLOAT_LITERAL":
            self.tokens.consume()
            return Literal(float(tok.value), "float")
        elif tok.type == "STRING_LITERAL":
            self.tokens.consume()
            return Literal(tok.value.strip('"'), "string")
        elif tok.type == "BOOL_LITERAL":
            self.tokens.consume()
            return Literal(tok.value == "true", "bool")
        elif tok.type == "IDENT" or tok.type in {"PRINT", "HALT"}:
            ident = self.tokens.consume().value
            if self.tokens.peek() and self.tokens.peek().type == "OP":
                if self.tokens.peek().value == "(":
                    self.tokens.consume()
                    args = []
                    if self.tokens.peek().type != "OP" or self.tokens.peek().value != ")":
                        while True:
                            args.append(self.parse_expr())
                            if self.tokens.peek().type == "OP" and self.tokens.peek().value == ",":
                                self.tokens.consume()
                            else:
                                break
                    self.tokens.expect("OP")
                    if self.tokens.peek(-1).value != ")":
                        raise SyntaxError("Esperado ')' após argumentos da função")
                    
                    if tok.type == "PRINT":
                        return Print(name=ident, args=args)
                    if tok.type == "HALT":
                        return Halt(name=ident, args=args)
                        
                    return Call(name=ident, args=args)  
                elif self.tokens.peek().value == ".":
                    self.tokens.consume()
                    name = self.tokens.expect("IDENT").value
                    return QualifiedRef(ident, name)
                elif self.tokens.peek().value == "[":
                    self.tokens.consume()
                    index = self.parse_expr()
                    self.tokens.expect("OP")
                    if self.tokens.peek(-1).value != "]":
                        raise SyntaxError("Esperado ']'")
                    return ArrayAccess(ident, index)     
            return VarRef(ident)
        elif tok.type == "OP" and tok.value == "(":
            self.tokens.consume()
            expr = self.parse_expr()
            self.tokens.expect("OP")
            if self.tokens.peek(-1).value != ")":
                raise SyntaxError("Esperado ')'")
            return expr
        else:
            raise SyntaxError(f"Expressão primária inválida: {tok}")










