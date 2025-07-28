import pytest
from typing import Union
from calc1 import Lexer, Parser


@pytest.mark.parametrize(
    "expression, expected",
    [
        # Basic operations
        ("1+2", 3),
        ("10-5", 5),
        ("3*4", 12),
        ("8/2", 4.0),
        ("100+222", 322),
        ("50-25", 25),
        ("7*8", 56),
        ("15/3", 5.0),
        # With spaces
        ("1 +  2", 3),
        ("10    - 5", 5),
        (" 3    * 4       ", 12),
        ("     8 /     2", 4.0),
        ("  5  +  3  ", 8),
        # Edge cases with zero
        ("0+1", 1),
        ("0-1", -1),
        ("0*5", 0),
        ("9/3", 3.0),
        ("5*0", 0),
        ("0+0", 0),
        ("0-0", 0),
        # Large numbers
        ("9999999+1", 10000000),
        ("100000-1", 99999),
        ("123*456", 56088),
        ("999999/3", 333333.0),
        # Negative results
        ("5-10", -5),
        ("100-200", -100),
        # Decimal results
        ("7/2", 3.5),
        ("5/4", 1.25),
        ("1/4", 0.25),
    ],
)
def test_basic_arithmetic(expression: str, expected: Union[int, float]) -> None:
    lexer = Lexer(expression)
    parser = Parser(lexer)
    result = parser.expr()
    assert result == expected


def test_division_by_zero() -> None:
    lexer = Lexer("5/0")
    parser = Parser(lexer)
    with pytest.raises(Exception, match="Division by zero"):
        parser.expr()


@pytest.mark.parametrize(
    "invalid_expression",
    [
        # Missing operands
        "1+",
        "+2",
        "1-",
        "*2",
        "1/",
        # Double operators
        "1++2",
        "1--2",
        "1**2",
        "1//2",
        # Missing operators
        "1 2",
        "12 34",
        "100 200",
        # Invalid characters
        "a+b",
        "1+a",
        "x*y",
        "1&2",
        "hello+world",
        # Empty and whitespace
        "",
        "   ",
        # Incomplete expressions
        "+",
        "-",
        "*",
        "/",
        # Unsupported formats
        "1.5+2",
        "(1+2)",
    ],
)
def test_invalid_expressions(invalid_expression: str) -> None:
    lexer = Lexer(invalid_expression)
    parser = Parser(lexer)
    with pytest.raises(Exception):
        parser.expr()
