import re

class Token:
    def __init__(self, type_, value, line, col_start, col_end):
        self.type = type_
        self.value = value
        self.line = line
        self.col_start = col_start
        self.col_end = col_end

    def __repr__(self):
        return f"{self.type}('{self.value}') @({self.line}:{self.col_start}-{self.col_end})"
    
class Lexer:
    def __init__(self, source_code):
        self.code = source_code
        self.tokens = []
        self.keywords = {
            'int', 'float', 'bool', 'string', 'auto', 'namespace', 'if', 'else', 'halt', 'print', 'return'
        }
        self.token_specification = [
            ('FLOAT_LITERAL', r'\d+\.\d+'),
            ('INT_LITERAL',   r'\d+'),
            ('STRING_LITERAL',r'"[^"]*"'),
            ('BOOL_LITERAL',  r'\btrue\b|\bfalse\b'),
            ('IDENT',         r'[A-Za-z_][A-Za-z0-9_]*'),
            ('OP',            r'==|!=|<=|>=|[+\-*/=<>(){}\[\].,;]'),
            ('SKIP',          r'[ \t]+'),
            ('NEWLINE',       r'\n'),
            ('MISMATCH',      r'.'),
        ]

    def tokenize(self):
        # Remove comentários de linha iniciados por //
        self.code = re.sub(r'//.*', '', self.code)

        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specification)
        line_num = 1
        line_start = 0
        for mo in re.finditer(tok_regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            col_start = mo.start() - line_start
            col_end = mo.end() - line_start

            if kind == 'NEWLINE':
                line_num += 1
                line_start = mo.end()
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Caractere inesperado '{value}' na linha {line_num}, colunas {col_start}-{col_end}")
            else:
                if kind == 'IDENT' and value in self.keywords:
                    kind = value.upper()  # Palavra-chave vira tipo próprio
                token = Token(kind, value, line_num, col_start, col_end)
                self.tokens.append(token)

        return self.tokens

# Classe TokenStream para o Parser
class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self, n=0):
        pos = self.index + n
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None  # fim dos tokens

    def consume(self):
        tok = self.peek()
        if tok:
            self.index += 1
        return tok

    def expect(self, kind):
        tok = self.consume()
        if not tok or tok.type != kind:
            raise SyntaxError(f"Esperado token '{kind}', mas encontrado '{tok}'")
        return tok
