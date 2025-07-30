from typing import Callable, TypeVar, Generic
from abc import ABC
from parsing.ast import NodeAST

T = TypeVar("T")


class NodeVisitor(Generic[T], ABC):
    def visit(self, node: NodeAST) -> T:
        method_name = f"visit_{type(node).__name__}"
        visitor: Callable[[NodeAST], T] = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: NodeAST) -> T:
        raise NotImplementedError(f"No visit_{type(node).__name__} method implemented")
