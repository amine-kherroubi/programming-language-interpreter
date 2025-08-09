from abc import ABC
from typing import Callable, Generic, TypeVar
from syntactic_analysis.ast import NodeAST

T = TypeVar("T")


class NodeVisitor(Generic[T], ABC):
    def visit(self, node: NodeAST) -> T:
        method_name = f"visit_{type(node).__name__}"
        visitor: Callable[[NodeAST], T] = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: NodeAST) -> T:
        raise NotImplementedError(
            f"No visit_{type(node).__name__} method implemented for {type(self).__name__}. "
            f"Override generic_visit or implement visit_{type(node).__name__}()."
        )
