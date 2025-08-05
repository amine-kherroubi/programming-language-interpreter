from typing import Callable, TypeVar, Generic
from abc import ABC
from syntactic_analysis.ast import NodeAST


# Generic type variable for visitor return types
# This allows visitors to return different types (e.g., str, int, None, custom objects)
T = TypeVar("T")


class NodeVisitor(Generic[T], ABC):
    """
    Abstract base class implementing the Visitor design pattern for AST traversal.

    This visitor provides a generic framework for traversing Abstract Syntax Tree (AST)
    nodes and performing operations on them. It uses Python's dynamic method dispatch
    to automatically call the appropriate visit method based on the node type.

    The visitor pattern separates tree traversal logic from node-specific operations,
    making it easy to add new operations without modifying the AST node classes.
    This is particularly useful for compiler phases like semantic analysis,
    code generation, optimization passes, and pretty printing.

    Type Parameters:
        T: The return type of visit methods. This allows different visitors to
           return different types (e.g., None for side-effect visitors,
           str for code generators, or custom objects for analyzers)

    Usage Example:
        class CodeGenerator(NodeVisitor[str]):
            def visit_ProgramNode(self, node: ProgramNode) -> str:
                return f"program {node.name};"

            def visit_VariableNode(self, node: VariableNode) -> str:
                return node.name
    """

    def visit(self, node: NodeAST) -> T:
        """
        Dispatch to the appropriate visit method based on node type.

        This is the main entry point for visiting AST nodes. It uses Python's
        dynamic method resolution to find and call the specific visit method
        for the given node type. The method name is constructed by prepending
        "visit_" to the node's class name.

        For example:
        - ProgramNode -> visit_ProgramNode()
        - VariableDeclarationNode -> visit_VariableDeclarationNode()
        - BinaryOperationNode -> visit_BinaryOperationNode()

        If no specific visit method is found, it falls back to generic_visit()
        which must be implemented by subclasses to handle unimplemented cases.

        Args:
            node: The AST node to visit

        Returns:
            The result of the specific visit method, with type T

        Raises:
            NotImplementedError: If no visit method exists and generic_visit
                                is not properly implemented in the subclass
        """
        # Construct method name from node class name
        # e.g., "ProgramNode" becomes "visit_ProgramNode"
        method_name: str = f"visit_{type(node).__name__}"

        # Get the visitor method using getattr with generic_visit as fallback
        # This allows for graceful handling of unimplemented visit methods
        visitor: Callable[[NodeAST], T] = getattr(self, method_name, self.generic_visit)

        # Call the visitor method with the node and return the result
        return visitor(node)

    def generic_visit(self, node: NodeAST) -> T:
        """
        Default fallback method for unimplemented visit methods.

        This method is called when no specific visit method exists for a node type.
        Subclasses must override this method to define the default behavior for
        unhandled node types. Common implementations include:

        1. Raising NotImplementedError (strict mode - forces implementation)
        2. Returning a default value (permissive mode - allows partial visitors)
        3. Recursively visiting child nodes (traversal mode - continues traversal)

        The current implementation enforces strict mode by raising NotImplementedError,
        which helps catch missing visit method implementations during development.

        Args:
            node: The AST node that doesn't have a specific visit method

        Returns:
            Type T - though this implementation always raises an exception

        Raises:
            NotImplementedError: Always raised in this base implementation to
                                force subclasses to implement all required visit methods
        """
        raise NotImplementedError(
            f"No visit_{type(node).__name__} method implemented for {type(self).__name__}. "
            f"Please implement visit_{type(node).__name__}() method or override generic_visit() "
            f"to handle unimplemented node types."
        )
