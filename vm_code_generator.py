from ast_tree import *

class VMCodeGenerator:
    def __init__(self, tac_instructions, symbol_table):
        self.tac = tac_instructions
        self.vm_code = []
        self.symbol_table = symbol_table

    def generate(self):
        arg_stack = []
        main_code = []
        function_code = []
        current = main_code

        for instr in self.tac:

            if instr.op == 'label':
                current = function_code
                current.append(("LABEL", instr.result))

            elif instr.op == 'arg':
                if isinstance(instr.arg1, Literal):
                    current.append(("PUSH", instr.arg1.value))
                elif isinstance(instr.arg1, VarRef):
                    current.append(("LOAD", instr.arg1.name))
                else:
                    current.append(("LOAD", instr.arg1))

            elif instr.op == 'call':
                current.append(("CALL", instr.arg1))
                current.append(("STORE", instr.result))
                arg_stack.clear()

            elif instr.op == 'ret':
                if instr.arg1 is not None:
                    current.append(("LOAD", instr.arg1))
                current.append(("RET",))

            elif instr.op == '=':
                sym = self.symbol_table.VMlookup(instr.arg1) if isinstance(instr.arg1, str) else None

                if sym and sym.category == 'literal':
                    current.append(("PUSH", sym.value))
                elif isinstance(instr.arg1, (int, float)):
                    current.append(("PUSH", instr.arg1))
                else:
                    current.append(("LOAD", instr.arg1))

                current.append(("STORE", instr.result))

            elif instr.op in {'+', '-', '*', '/', '==', '!=', '<', '<=', '>', '>='}:
                current.append(("LOAD", instr.arg1))
                current.append(("LOAD", instr.arg2))
                op_map = {
                    '+': "ADD",
                    '-': "SUB",
                    '*': "MUL",
                    '/': "DIV",
                    '==': "EQ",
                    '!=': "NEQ",
                    '<':  "LT",
                    '<=': "LE",
                    '>':  "GT",
                    '>=': "GE"
                }
                current.append((op_map[instr.op],))
                current.append(("STORE", instr.result))

            elif instr.op == 'literal_init':
                current.append(("PUSH", instr.arg1)) 
                current.append(("STORE", instr.result))

            elif instr.op == 'alloc':
                current.append(("ALLOC", instr.result))

            elif instr.op == 'load':
                current.append(("LOAD_INDEX", instr.arg1, instr.arg2))

                current.append(("STORE", instr.result))

            elif instr.op == 'store':
                current.append(("LOAD", instr.arg1))
                current.append(("STORE_INDEX", instr.result, instr.arg2))

            elif instr.op == 'goto':
                current.append(("JUMP", instr.result))

            elif instr.op == 'ifz':
                current.append(("LOAD", instr.arg1))
                current.append(("JMP_IF_TRUE", f"NOT_{instr.result}"))
                current.append(("JUMP", instr.result))
                current.append(("LABEL", f"NOT_{instr.result}"))

            elif instr.op == 'param':
                current.append(("STORE", instr.result))

            elif instr.op == 'PRINT':
                current.append(("PRINT",))

            elif instr.op == 'HALT':
                current.append(("HALT",))

            else:
                current.append(("# UNHANDLED", str(instr)))

        self.vm_code = main_code + function_code
        return self.vm_code

