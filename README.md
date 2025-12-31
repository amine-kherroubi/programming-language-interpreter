
# Custom Programming Language Interpreter

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A simple custom turing-complete programming language interpreter with static typing and lexical scoping. The language syntax draws inspiration from Python, C, and Ada, combining Python's keywords (`if`, `elif`, `else`, `while`, `and`, `or`, `not`) with C-style braces and Ada-like distinction between functions and procedures, along with new stylish keywords like `give`, `show`, `skip`, `stop`. The interpreter implements a four-phase architecture with lexical analysis, recursive descent parsing, semantic analysis, and tree-walking interpretation.

<img width="1854" height="1040" alt="image" src="https://github.com/user-attachments/assets/96369f90-90ca-477a-a610-e7ff7be93494" />

---

## Language Features

* **Type System** : Static type checking with three core types: `number` (supports both integers and floats), `string`, and `boolean`. The compiler performs comprehensive type checking at compile-time with detailed error reporting.
* **Variable Management** : Declare mutable variables with `let` and immutable constants with `keep`. Multiple declarations and initializations are supported in a single statement for clean, concise code.
* **Functions & Procedures** : Functions return values using the elegant `give` statement, while procedures handle side-effects without returns. Both support parameters, lexical scoping, and proper activation record management.
* **Control Flow** : Intuitive conditional execution with `if`/`elif`/`else` chains and `while` loops. Loop control uses the expressive `skip` (continue) and `stop` (break) keywords that make intent crystal clear.
* **Rich Expressions** : Full arithmetic support including `+`, `-`, `*`, `/`, `%`, `//`, `**` with proper precedence. Boolean operations with `and`, `or`, `not` and comprehensive comparison operators. Function calls seamlessly integrate into expressions.

---

## Installation and Usage

Requires Python 3.10+. Clone and run directly on your source files:

```bash
git clone https://github.com/amine-kherroubi/programming-language-interpreter
cd programming-language-interpreter
```

**Static Analysis Only** (syntax and semantic checking):

```bash
python main.py examples/example.lang
```

**Full Interpretation** (analysis + execution):

```bash
python main.py examples/example.lang --run
```

---

## Language Syntax

**Variable Declarations** with optional initialization:

```
let number x, y, z = 10, 3.14, 2.71  # Mutable variables
keep string greeting = "Hello World"  # Immutable constant
```

**Functions** with typed parameters and return types:

```
func fibonacci(number n) -> number {
    if n <= 1 {
        give n
    }
    give fibonacci(n - 1) + fibonacci(n - 2)  # Recursive calls supported
}

let number result = fibonacci(8)  # Clean function calls
```

**Procedures** for side-effect operations:

```
proc displayMessage(string msg, number count) {
    let number i = 0
    while i < count {
        show msg
        i = i + 1
    }
}

exec displayMessage("Hello!", 3)  # Explicit procedure execution
```

**Control Flow** with natural syntax:

```
if score >= 90 {
    show "Excellent!"
} elif score >= 70 {
    show "Good job"
} else {
    show "Keep practicing"
}

while running and not finished {
    # Process logic here
    if should_continue {
        skip  # Continue to next iteration
    }
    if should_exit {
        stop  # Break out of loop
    }
}
```

---

## Complete Example

Here's a program showcasing the language:

```
{
    keep number limit = 10
    keep string title = "Fibonacci Sequence Generator"
  
    func fibonacci(number n) -> number {
        if n <= 1 {
            give n
        }
        give fibonacci(n - 1) + fibonacci(n - 2)
    }
  
    proc printSequence(number max) {
        show title
        show "Generating fibonacci numbers:"
      
        let number i = 0
        while i < max {
            let number value = fibonacci(i)
            show "F(" + i + ") = " + value
            i = i + 1
          
            if i > 5 {
                stop  # Exit loop after 5 iterations
            }
        }
    }
  
    exec printSequence(limit)
  
    let boolean should_display = true
    if should_display {
        show "Program completed successfully!"
    }
}
```
