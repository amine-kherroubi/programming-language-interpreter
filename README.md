# Custom Programming Language Interpreter

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A Turing-complete programming language interpreter with static typing and lexical scoping. The language syntax draws inspiration from Python, C-family languages, Pascal, and Go, combining Python's keywords (`if`, `elif`, `else`, `while`, `and`, `or`, `not`) with C-style braces and Pascal-like explicit type declarations. The interpreter implements a four-phase architecture with lexical analysis, recursive descent parsing, semantic analysis, and tree-walking interpretation.

## Language Features

The language provides static type checking with four primitive types: `int`, `float`, `string`, and `bool`. Variables are declared using `let` for mutable bindings and `keep` for immutable constants. The type system enforces compile-time type checking with comprehensive error reporting.

Functions are named constructs that return values using the `give` statement, while procedures handle side-effect operations without return values. Both support parameter passing and lexical scoping with proper variable lifetime management.

Control flow includes conditional execution with `if`, `elif`, and `else` statements, along with `while` loops. Loop control is provided through `skip` for continue semantics and `stop` for break semantics. All constructs support proper nesting and scoping rules.

Expression evaluation supports full arithmetic operations including addition, subtraction, multiplication, division, modulo, floor division, and exponentiation. Logical operations include `and`, `or`, and `not`, with comparison operators for relational testing. Operator precedence follows mathematical conventions.

## Installation and Usage

The interpreter requires Python 3.10 or higher. Clone the repository and run the interpreter directly on source files.

```bash
git clone <repository-url>
cd custom-programming-language
```

To perform static analysis only, run the interpreter without execution flags:

```bash
python main.py program.txt
```

For complete interpretation including runtime execution, use the run flag:

```bash
python main.py program.txt --run
```

## Language Syntax

Variable declarations support single and multiple bindings with optional initialization:

```javascript
let int x = 10
let float y, z = 3.14, 2.71
keep string message = "Hello World"
```

Functions declare parameters with types and specify return types using arrow notation:

```javascript
func add(int a, int b) -> int {
    give a + b
}

func max(int x, int y) -> int {
    if x > y {
        give x
    } else {
        give y
    }
}
```

Procedures operate similarly but omit return type specifications:

```javascript
proc printValue(int value) {
    show value
}

proc processData(string data) {
    show "Processing: "
    show data
}
```

Control flow structures support nested execution with proper scoping:

```javascript
if condition {
    # statements
} elif alternative_condition {
    # statements
} else {
    # statements
}

while expression {
    # statements
    skip  # continue to next iteration
    stop  # exit loop
}
```

## Complete Example

```javascript
{
    let int fibonacci_limit = 10
    let int a, b = 0, 1
    keep string title = "Fibonacci Generator"

    func fibonacci(int n) -> int {
        if n <= 1 {
            give n
        }
        give fibonacci(n - 1) + fibonacci(n - 2)
    }

    proc printSequence(int limit) {
        show title
        let int i = 0
        while i < limit {
            show fibonacci(i)
            i = i + 1
        }
    }

    exec printSequence(fibonacci_limit)

    if fibonacci(5) > 3 {
        show "Fibonacci(5) is greater than 3"
    }
}
```
