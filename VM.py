class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.static_memory = {}
        self.labels = {}
        self.instructions = []
        self.pc = 0
        self.call_stack = []
        self.functions = set()
        self.running = True

    def run(self, instructions):
        self.instructions = instructions
        self.find_labels_and_functions()
        self.pc = 0
        self.running = True
        while self.pc < len(self.instructions) and self.running:
            instr = self.instructions[self.pc]
            op = instr[0]
            args = instr[1:]

            if op == "LABEL" and instr[1] in self.functions:
                self.pc = self.skip_function_body(self.pc)
                continue

            if hasattr(self, f"op_{op}"):
                getattr(self, f"op_{op}")(*args)
            self.pc += 1

    def find_labels_and_functions(self):
        for idx, instr in enumerate(self.instructions):
            if instr[0] == "LABEL":
                self.labels[instr[1]] = idx
        for instr in self.instructions:
            if instr[0] == "CALL":
                self.functions.add(instr[1])

    def skip_function_body(self, start):
        for i in range(start + 1, len(self.instructions)):
            if self.instructions[i][0] == "RET":
                return i + 1
        return len(self.instructions)

    def op_HALT(self):
        self.running = False

    def op_ALLOC(self, varname, value=0):
        self.static_memory[varname] = value

    def op_LOAD(self, varname):
        self.stack.append(self.static_memory[varname])

    def op_STORE(self, varname):
        self.static_memory[varname] = self.stack.pop()

    def op_PUSH(self, value):
        self.stack.append(value)

    def op_POP(self):
        self.stack.pop()

    def op_ADD(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a + b)

    def op_SUB(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a - b)

    def op_MUL(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a * b)

    def op_EQ(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(1 if a == b else 0)

    def op_NEQ(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(1 if a != b else 0)

    def op_LT(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(1 if a < b else 0)

    def op_LE(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(1 if a <= b else 0)

    def op_GT(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(1 if a > b else 0)

    def op_GE(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(1 if a >= b else 0)

    def op_PRINT(self):
        print(">>", self.stack.pop())

    def op_LABEL(self, label):
        pass

    def op_JUMP(self, label):
        self.pc = self.labels[label] - 1

    def op_JMP_IF_TRUE(self, label):
        condition = self.stack.pop()
        if condition:
            self.pc = self.labels[label] - 1

    def op_CALL(self, label):
        self.call_stack.append((self.pc, self.static_memory.copy()))
        self.pc = self.labels[label]

    def op_RET(self):
        if not self.call_stack:
            raise RuntimeError("RET called without active CALL")
        self.pc, self.static_memory = self.call_stack.pop()

    def op_LOAD_ADDR(self, varname):
        self.stack.append(("ref", varname))

    def op_DEREF(self):
        ref = self.stack[-1]
        if isinstance(ref, tuple) and ref[0] == "ref":
            self.stack.append(self.static_memory[ref[1]])
        else:
            raise RuntimeError("Invalid reference")

    def op_STORE_AT_ADDR(self):
        value = self.stack.pop()
        ref = self.stack.pop()
        if isinstance(ref, tuple) and ref[0] == "ref":
            self.static_memory[ref[1]] = value
        else:
            raise RuntimeError("Invalid reference")
