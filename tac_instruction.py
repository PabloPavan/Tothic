class TACInstruction:
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __repr__(self):
        if self.op in {"copy"}:
            return f"{self.result} -> {self.arg1}"
        elif self.arg2 is not None:
            return f"{self.result} -> {self.arg1} {self.op} {self.arg2}"
        elif self.arg1 is not None:
            return f"{self.result} -> {self.op} {self.arg1}"
        else:
            return f"{self.op} {self.result}"