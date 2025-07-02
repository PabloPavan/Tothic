from tac_instruction import *

class TACConstantFolder:
    def __init__(self, instructions):
        self.instructions = instructions

    def fold(self):
        optimized = []
        for instr in self.instructions:
            if instr.op in ['+', '-', '*', '/']:
                if isinstance(instr.arg1, (int, float)) and isinstance(instr.arg2, (int, float)):
                    result = eval(f"{instr.arg1} {instr.op} {instr.arg2}")
                    optimized.append(TACInstruction('=', result, None, instr.result))
                    continue
            optimized.append(instr)
        return optimized


class TACCopyPropagation:
    def __init__(self, instructions):
        self.instructions = instructions
        self.copy_map = {}

    def propagate(self):
        result = []

        for instr in self.instructions:
            # Se arg1 ou arg2 forem não-hashables (como VarRef), usamos como estão
            try:
                arg1 = self.copy_map.get(instr.arg1, instr.arg1)
            except TypeError:
                arg1 = instr.arg1

            try:
                arg2 = self.copy_map.get(instr.arg2, instr.arg2)
            except TypeError:
                arg2 = instr.arg2

            # Se for cópia válida: x = y
            if instr.op == '=' and isinstance(instr.arg1, str) and isinstance(instr.result, str):
                self.copy_map[instr.result] = arg1
                result.append(TACInstruction('=', arg1, None, instr.result))
            else:
                if isinstance(instr.result, str) and instr.result in self.copy_map:
                    del self.copy_map[instr.result]
                result.append(TACInstruction(instr.op, arg1, arg2, instr.result))

        return result


class TACConstantPropagation:
    def __init__(self, instructions):
        self.instructions = instructions
        self.env = {}

    def propagate(self):
        optimized = []
        for instr in self.instructions:
            if instr.op == '=' and isinstance(instr.arg1, (int, float, str, bool)):
                self.env[instr.result] = instr.arg1
                optimized.append(instr)
            elif instr.op in ['+', '-', '*', '/', '==', '!=', '<', '<=', '>', '>=']:
                a1 = self.env.get(instr.arg1, instr.arg1)
                a2 = self.env.get(instr.arg2, instr.arg2)
                optimized.append(TACInstruction(instr.op, a1, a2, instr.result))
            else:
                optimized.append(instr)
        return optimized


class TACCommonSubexpressionEliminator:
    def __init__(self, instructions):
        self.instructions = instructions
        self.expr_map = {}

    def eliminate(self):
        result = []
        for instr in self.instructions:
            key = None
            if instr.op in ['+', '-', '*', '/'] and all(isinstance(x, str) for x in [instr.arg1, instr.arg2]):
                key = (instr.op, instr.arg1, instr.arg2)
                if key in self.expr_map:
                    existing_result = self.expr_map[key]
                    result.append(TACInstruction('=', existing_result, None, instr.result))
                    continue
                else:
                    self.expr_map[key] = instr.result
            result.append(instr)
        return result


class TACDeadCodeEliminator:
    def __init__(self, instructions):
        self.instructions = instructions

    def eliminate(self):
        live_vars = set()
        optimized = []

        for instr in reversed(self.instructions):
            # Ignorar instruções de controle/declaração que sempre devem ser mantidas
            if instr.op not in {'=', '+', '-', '*', '/', 'cast'}:
                optimized.insert(0, instr)

                # Tenta adicionar args vivos
                for arg in [instr.arg1, instr.arg2]:
                    if isinstance(arg, str):
                        live_vars.add(arg)
                continue

            # Verificar se o resultado está vivo
            try:
                is_live = instr.result in live_vars
            except TypeError:
                is_live = False

            if not instr.result or not is_live:
                continue  # código morto

            # Mantém a instrução
            optimized.insert(0, instr)

            # Atualiza variáveis vivas com os argumentos usados
            for arg in [instr.arg1, instr.arg2]:
                if isinstance(arg, str):
                    live_vars.add(arg)

            # Remove variável definida (não é mais viva até outro uso)
            if isinstance(instr.result, str) and instr.result in live_vars:
                live_vars.remove(instr.result)

        return optimized

 

def optimize(instructions):
    passes = [
        TACConstantFolder,
        TACConstantPropagation,
        TACCopyPropagation,
        TACCommonSubexpressionEliminator,
        TACDeadCodeEliminator
    ]

    current = instructions
    while True:
        previous = current
        for opt_cls in passes:
            optimizer = opt_cls(previous)
            if hasattr(optimizer, "fold"):
                current = optimizer.fold()
            elif hasattr(optimizer, "propagate"):
                current = optimizer.propagate()
            elif hasattr(optimizer, "eliminate"):
                current = optimizer.eliminate()
        if str(current) == str(previous):
            break
    return current