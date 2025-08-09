# Custom Programming Language Interpreter

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A sophisticated, **Turing-complete** programming language interpreter featuring static type analysis, lexical scoping, and first-class function support. This implementation demonstrates advanced compiler construction techniques through a meticulously architected four-phase translation system, employing recursive descent parsing, semantic analysis with symbol table management, and tree-walking interpretation.

## Table of Contents

* [Overview](#overview)
* [Language Specification](#language-specification)
* [Architecture &amp; Implementation](#architecture--implementation)
* [Installation &amp; Usage](#installation--usage)
* [Language Reference](#language-reference)
* [Technical Implementation Details](#technical-implementation-details)
* [Error Handling &amp; Diagnostics](#error-handling--diagnostics)
* [Contributing](#contributing)

## Overview

This interpreter implements a  **statically-typed** , **imperative programming language** with comprehensive support for:

* **Computational Completeness** : Full Turing-complete computational model with conditional branching and iterative constructs
* **Type Safety** : Comprehensive static type system with compile-time type checking and inference
* **Lexical Scoping** : Hierarchical scope resolution with proper variable lifetime management
* **First-Class Functions** : Full support for function declarations, invocations, and return value semantics
* **Procedural Abstractions** : Distinguished procedure constructs for side-effect operations
* **Control Flow Primitives** : Structured programming constructs including conditional execution and iteration
* **Memory Safety** : Managed runtime environment with automatic scope-based resource deallocation

### Key Architectural Innovations

* **Multi-Phase Translation Pipeline** : Employs a classical four-stage compilation architecture
* **Recursive Descent Parser** : Hand-crafted top-down parser with predictive parsing capabilities
* **Visitor Pattern Implementation** : Clean separation of concerns through polymorphic dispatch
* **Scoped Symbol Table Management** : Hierarchical symbol resolution with O(1) lookup performance
* **Tree-Walking Interpreter** : Direct AST evaluation with optimized node traversal

## Language Specification

### Computational Model

The language operates on a **von Neumann architecture** model with:

* **Mutable State** : Variables with assignment semantics
* **Immutable Constants** : Compile-time constant declarations with immutability guarantees
* **Subroutine Abstractions** : Functions (pure) and procedures (side-effects)
* **Structured Control Flow** : Conditional branching and bounded iteration
* **Expression Evaluation** : Full arithmetic and logical expression support with operator precedence

### Type System

* **Static Typing** : All variables must be explicitly typed at declaration
* **Primitive Types** : `int`, `float`, `string`, `bool`
* **Type Inference** : Limited inference within expression contexts
* **Type Compatibility** : Strict type checking with no implicit conversions

## Architecture & Implementation

### Phase 1: Lexical Analysis (Tokenization)

 **Components** : `LexicalAnalyzer`, `Token`, `TokenType`

The **lexical analyzer** performs morphological analysis, transforming the input character stream into a sequence of lexemes. Key features:

* **Maximal Munch Principle** : Longest possible token matching
* **Position Tracking** : Line and column information for comprehensive error reporting
* **Multi-Character Operator Recognition** : Efficient finite automaton for operator disambiguation
* **String Literal Processing** : Full escape sequence support with delimiter matching
* **Numeric Literal Parsing** : IEEE 754-compliant floating-point and arbitrary-precision integer support
* **Reserved Word Classification** : Keyword recognition with identifier disambiguation

### Phase 2: Syntactic Analysis (Parsing)

 **Components** : `SyntacticAnalyzer`, Abstract Syntax Tree Nodes

Implements a **recursive descent parser** with the following characteristics:

* **Top-Down Parsing** : LL(1) grammar with predictive parsing
* **Left-Recursion Elimination** : Grammar transformation for proper precedence handling
* **Operator Precedence Climbing** : Efficient expression parsing with associativity handling
* **Error Recovery** : Synchronization points for robust error handling
* **Abstract Syntax Tree Construction** : Intermediate representation generation

 **Grammar Properties** :

* **Context-Free** : Formal CFG specification with unambiguous productions
* **Deterministic** : Single-pass parsing without backtracking
* **Precedence-Aware** : Mathematical operator precedence preservation

### Phase 3: Semantic Analysis (Type Checking & Symbol Resolution)

 **Components** : `SemanticAnalyzer`, `ScopedSymbolTable`, Symbol Hierarchy

The semantic analyzer performs  **static program analysis** :

* **Symbol Table Management** : Hierarchical scope tracking with efficient lookup
* **Type Checking** : Static type validation with compatibility analysis
* **Declaration Analysis** : Duplicate declaration detection and scope violation checking
* **Usage Validation** : Undefined variable detection and constant assignment prevention
* **Subroutine Analysis** : Parameter arity checking and return value validation
* **Control Flow Analysis** : Proper `give` statement validation within function contexts

 **Symbol Table Implementation** :

* **Scoped Resolution** : Lexical scoping with enclosing scope chain traversal
* **O(1) Lookup** : Hash-table based symbol storage for optimal performance
* **Type Annotation** : Full type information preservation for runtime execution

### Phase 4: Interpretation (Runtime Execution)

 **Components** : `Interpreter`, Runtime Environment

The **tree-walking interpreter** provides direct AST evaluation:

* **Environment Management** : Dynamic scope creation and destruction
* **Expression Evaluation** : Recursive descent evaluation with type preservation
* **Control Flow Implementation** : Native support for branching and iteration
* **Function Call Semantics** : Stack-based activation record management
* **Built-in Operations** : Native implementation of arithmetic and logical operations
* **Memory Management** : Automatic garbage collection through Python's runtime

## Installation & Usage

### Prerequisites

* **Python 3.10+** (Required for structural pattern matching and enhanced type hints)
* **Modern Operating System** (Windows 10+, macOS 10.15+, Linux)

### Installation

```bash
git clone https://github.com/your-username/custom-programming-language
cd custom-programming-language
```

### Execution Modes

#### Static Analysis Only

Performs lexical, syntactic, and semantic analysis without execution:

```bash
python main.py program.txt
```

#### Full Interpretation

Complete pipeline including runtime execution:

```bash
python main.py program.txt --run
```

### Example Program

```javascript
{
    // Variable declarations with type annotations
    let int fibonacci_limit = 20
    let int a, b = 0, 1
    keep string greeting = "Fibonacci Sequence Generator"

    // Procedure for output operations
    proc displayMessage(string message) {
        show message
    }

    // Pure function with mathematical computation
    func computeFibonacci(int n, int current, int next) -> int {
        if n <= 0 {
            give current
        }
        give computeFibonacci(n - 1, next, current + next)
    }

    // Program execution
    exec displayMessage(greeting)
  
    let int result = computeFibonacci(fibonacci_limit, a, b)
    show "Result: "
    show result
}
```

## Language Reference

### Lexical Structure

#### Identifiers

```
IDENTIFIER ::= [a-zA-Z_][a-zA-Z0-9_]*
```

#### Literals

```
INT_LITERAL    ::= [0-9]+
FLOAT_LITERAL  ::= [0-9]*"."[0-9]+
STRING_LITERAL ::= ('"' [^"\n]* '"') | ("'" [^'\n]* "'")
BOOL_LITERAL   ::= "true" | "false"
```

### Type System

#### Primitive Types

* `int`: 64-bit signed integers
* `float`: IEEE 754 double-precision floating-point
* `string`: UTF-8 encoded character sequences
* `bool`: Boolean truth values

#### Type Declarations

```javascript
let int variable_name = expression
let float x, y, z = 1.0, 2.0, 3.14159
keep bool immutable_flag = true
```

### Control Structures

#### Conditional Execution

```javascript
if boolean_expression {
    statements
} elif boolean_expression {
    statements
} else {
    statements
}
```

#### Iterative Control

```javascript
while boolean_expression {
    statements
    skip  // Continue to next iteration
    stop  // Break from loop
}
```

### Subroutine Definitions

#### Functions (Pure)

```javascript
func function_name(type param1, type param2) -> return_type {
    statements
    give return_expression
}
```

#### Procedures (Side-Effects)

```javascript
proc procedure_name(type param1, type param2) {
    statements
    give  // Optional empty return
}
```

### Expression System

#### Operator Precedence (Highest to Lowest)

1. **Unary** : `+`, `-`, `not`
2. **Power** : `**` (Right-associative)
3. **Multiplicative** : `*`, `/`, `//`, `%`
4. **Additive** : `+`, `-`
5. **Relational** : `<`, `>`, `<=`, `>=`
6. **Equality** : `==`, `!=`
7. **Logical AND** : `and`
8. **Logical OR** : `or`

## Technical Implementation Details

### Parser Implementation

The **recursive descent parser** employs the following techniques:

* **Predictive Parsing** : Single-token lookahead for deterministic parsing
* **Precedence Climbing** : Efficient operator precedence resolution
* **Left-Factoring** : Grammar transformation to eliminate ambiguity
* **Error Synchronization** : Strategic recovery points for robust error handling

### Symbol Table Architecture

```python
class ScopedSymbolTable:
    - Hierarchical scope management
    - O(1) symbol lookup via hash tables
    - Automatic built-in type registration
    - Scope-based symbol lifetime management
```

### AST Node Hierarchy

Comprehensive node taxonomy with:

* **Statement Nodes** : Executable constructs
* **Expression Nodes** : Value-producing constructs
* **Type Nodes** : Type annotation representations
* **Literal Nodes** : Constant value representations

### Memory Management

* **Scope-Based Allocation** : Variables allocated within lexical scopes
* **Automatic Deallocation** : Python GC handles memory reclamation
* **Symbol Table Cleanup** : Automatic scope destruction on exit

## Error Handling & Diagnostics

### Comprehensive Error Taxonomy

#### Lexical Errors

* **Invalid Character Sequences** : Unrecognized character patterns
* **Malformed Literals** : Syntactically incorrect numeric or string literals
* **Unterminated Constructs** : Unclosed strings or comments

#### Syntactic Errors

* **Grammar Violations** : Productions not matching formal grammar
* **Token Mismatches** : Unexpected token sequences
* **Structural Inconsistencies** : Mismatched delimiters or block structures

#### Semantic Errors

* **Type Mismatches** : Incompatible type operations
* **Undefined Symbols** : References to undeclared identifiers
* **Scope Violations** : Invalid variable access patterns
* **Arity Mismatches** : Incorrect function parameter counts
* **Const Violations** : Illegal assignments to immutable bindings

#### Runtime Errors

* **Arithmetic Exceptions** : Division by zero, overflow conditions
* **Invalid Operations** : Type-incompatible runtime operations

### Diagnostic Quality

All error messages include:

* **Precise Location** : Line and column information
* **Contextual Information** : Relevant code context
* **Suggested Fixes** : Actionable error resolution guidance

## Contributing

We welcome contributions that enhance the interpreter's capabilities and robustness.

### Development Workflow

1. **Fork Repository** : Create personal development fork
2. **Feature Branch** : `git checkout -b feature/enhancement-name`
3. **Implementation** : Follow established architectural patterns
4. **Testing** : Comprehensive test coverage for new features
5. **Documentation** : Update grammar specifications and README
6. **Pull Request** : Submit with detailed description

### Code Quality Standards

* **Type Annotations** : Comprehensive static type information
* **Documentation** : Docstrings following Google style
* **Error Handling** : Robust exception handling with meaningful messages
* **Performance** : Consider algorithmic complexity in implementations
* **Memory Efficiency** : Utilize `__slots__` for optimal memory usage

### Architecture Guidelines

* **Separation of Concerns** : Maintain clear phase boundaries
* **Visitor Pattern** : Extend functionality through visitor implementations
* **Immutable Data Structures** : Prefer immutable constructs where possible
* **Comprehensive Logging** : Detailed execution tracing for debugging

## Performance Characteristics

* **Time Complexity** : O(n) parsing and interpretation for program size n
* **Space Complexity** : O(d) for maximum nesting depth d
* **Memory Efficiency** : Optimized through `__slots__` usage
* **Scalability** : Handles moderately complex programs efficiently

## License

This project is licensed under the **MIT License** - see the [LICENSE]() file for complete terms and conditions.

## Acknowledgments

This implementation draws inspiration from:

* **Classical Compiler Theory** : Aho, Sethi, Ullman principles
* **Modern Language Design** : Contemporary programming language innovations
* **Academic Research** : Formal language theory and type system design
* **Industry Best Practices** : Production-quality interpreter architecture

---

*For detailed technical documentation, API references, and extended examples, please refer to the project wiki and documentation directory.*
