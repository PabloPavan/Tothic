from dataclasses import dataclass
from typing import List, Optional, Union, Tuple

class Node: pass

@dataclass
class Literal(Node):
    value: Union[int, float]
    type: str

@dataclass
class VarRef(Node):
    name: str

@dataclass
class BinaryOp(Node):
    op: str
    left: Node
    right: Node

@dataclass
class TypeCast(Node):
    target_type: str
    expr: Node

@dataclass
class Assign(Node):
    name: Node
    expr: Node

@dataclass
class Decl(Node):
    name: str
    type: str

@dataclass
class AutoDecl(Node):
    name: str
    expr: Node

@dataclass
class If(Node):
    condition: Node
    then_branch: Node
    else_branch: Optional[Node] = None

@dataclass
class Block(Node):
    statements: List[Node]

@dataclass
class NamespaceDecl(Node):
    name: str
    declarations: List[Node]

@dataclass
class ArrayDecl(Node):
    name: str
    type: str
    size: Node

@dataclass
class ArrayAccess(Node):
    name: str
    index: Node

@dataclass
class QualifiedRef(Node):
    namespace: str
    name: str

@dataclass
class ExprStmt(Node):
    expr: Node

@dataclass
class FunctionDecl(Node):
    name: str
    params: List[Tuple[str, str]]  # (nome, tipo)
    return_type: str
    body: Block

@dataclass
class Call(Node):
    name: str
    args: List[Node]

@dataclass
class Print(Node):
    name: str
    args: List[Node]

@dataclass
class Halt(Node):
    name: str
    args: List[Node]

@dataclass
class Return(Node):
    expr: Node

@dataclass
class Program(Node):
    statements: List[Node]
