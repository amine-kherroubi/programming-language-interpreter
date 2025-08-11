# Language Grammar Specification

## Lexical Grammar (For Tokenization)

### Identifiers and Literals

```bnf
IDENTIFIER                 ::= [a-zA-Z_][a-zA-Z0-9_]*
NUMBER_LITERAL             ::= [0-9]+("."[0-9]+)?
STRING_LITERAL             ::= ('"' [^"\n]* '"') | ("'" [^'\n]* "'")
BOOLEAN_LITERAL            ::= "true" | "false"
```

### Types

```bnf
NUMBER_TYPE                ::= "number"
STRING_TYPE                ::= "string"
BOOLEAN_TYPE               ::= "boolean"
```

### Keywords

```bnf
LET                        ::= "let"
KEEP                       ::= "keep"
FUNC                       ::= "func"
PROC                       ::= "proc"
EXEC                       ::= "exec"
GIVE                       ::= "give"
SHOW                       ::= "show"
IF                         ::= "if"
ELIF                       ::= "elif"
ELSE                       ::= "else"
WHILE                      ::= "while"
SKIP                       ::= "skip"
STOP                       ::= "stop"
```

### Operators

```bnf
ASSIGN                     ::= "="
ARROW                      ::= "->"
DOT                        ::= "."
EQUAL                      ::= "=="
NOT_EQUAL                  ::= "!="
LESS                       ::= "<"
LESS_EQUAL                 ::= "<="
GREATER                    ::= ">"
GREATER_EQUAL              ::= ">="
PLUS                       ::= "+"
MINUS                      ::= "-"
MULTIPLY                   ::= "*"
DIVIDE                     ::= "/"
MODULO                     ::= "%"
FLOOR_DIVIDE               ::= "//"
POWER                      ::= "**"
OR                         ::= "or"
AND                        ::= "and"
NOT                        ::= "not"
```

### Special

```bnf
EOF                        ::= end-of-file
```

### Delimiters

```bnf
LEFT_BRACE                 ::= "{"
RIGHT_BRACE                ::= "}"
LEFT_PAREN                 ::= "("
RIGHT_PAREN                ::= ")"
COMMA                      ::= ","
NEWLINE                    ::= "\n"
```

## Syntax Grammar (For Parsing)

### Program Structure

```bnf
program                    ::= block EOF

block                      ::= LEFT_BRACE (statement NEWLINE)* RIGHT_BRACE

statement                  ::= variable_declaration
                             | constant_declaration
                             | function_declaration
                             | procedure_declaration
                             | procedure_call
                             | assignment_statement
                             | give_statement
                             | show_statement
                             | if_statement
                             | while_statement
                             | skip_statement
                             | stop_statement
```

### Declarations

```bnf
variable_declaration       ::= LET type identifier_list (ASSIGN expression_list)?

constant_declaration       ::= KEEP type identifier_list ASSIGN expression_list

function_declaration       ::= FUNC IDENTIFIER LEFT_PAREN parameter_list? RIGHT_PAREN
                               return_type block

procedure_declaration      ::= PROC IDENTIFIER LEFT_PAREN parameter_list? RIGHT_PAREN block

parameter_list             ::= parameter (COMMA parameter)*
parameter                  ::= type IDENTIFIER
return_type                ::= ARROW type
type                       ::= NUMBER_TYPE | STRING_TYPE | BOOLEAN_TYPE

identifier_list            ::= IDENTIFIER (COMMA IDENTIFIER)*
expression_list            ::= expression (COMMA expression)*
```

### Function and Procedure Calls

```bnf
function_call              ::= IDENTIFIER LEFT_PAREN argument_list? RIGHT_PAREN

procedure_call             ::= EXEC IDENTIFIER LEFT_PAREN argument_list? RIGHT_PAREN

argument_list              ::= expression (COMMA expression)*
```

### Statements

```bnf
assignment_statement       ::= IDENTIFIER ASSIGN expression

give_statement             ::= GIVE expression?

show_statement             ::= SHOW expression

if_statement               ::= IF boolean_expression block elifs? else_clause?
elifs                      ::= (ELIF boolean_expression block)+
else_clause                ::= ELSE block

while_statement            ::= WHILE boolean_expression block

skip_statement             ::= SKIP

stop_statement             ::= STOP
```

### Expressions

```bnf
expression                 ::= boolean_expression | arithmetic_expression
```

### Boolean Expressions

```bnf
boolean_expression         ::= logical_or_expression

logical_or_expression      ::= logical_and_expression (OR logical_and_expression)*

logical_and_expression     ::= logical_not_expression (AND logical_not_expression)*

logical_not_expression     ::= NOT? comparison_expression

comparison_expression      ::= arithmetic_expression (comparison_operator arithmetic_expression)?

comparison_operator        ::= EQUAL | NOT_EQUAL | LESS | GREATER | LESS_EQUAL | GREATER_EQUAL
```

### Arithmetic Expressions

```bnf
arithmetic_expression      ::= additive_expression

additive_expression        ::= multiplicative_expression ((PLUS | MINUS) multiplicative_expression)*

multiplicative_expression  ::= power_expression ((MULTIPLY | DIVIDE | FLOOR_DIVIDE | MODULO) power_expression)*

power_expression           ::= unary_expression (POWER unary_expression)?

unary_expression           ::= (PLUS | MINUS)? primary_expression

primary_expression         ::= literal
                             | IDENTIFIER
                             | LEFT_PAREN arithmetic_expression RIGHT_PAREN
                             | function_call
```

### Literals

```bnf
literal                    ::= NUMBER_LITERAL | STRING_LITERAL | BOOLEAN_LITERAL
```
