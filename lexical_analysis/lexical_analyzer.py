from typing import Optional
from lexical_analysis.tokens import Token, TokenType
from utils.error_handling import LexicalError, ErrorCode


class LexicalAnalyzer(object):
    """
    A lexical analyzer (tokenizer) that converts source code text into a sequence of tokens.

    This analyzer is designed for a Pascal-like programming language and supports:
    - Reserved keywords (PROGRAM, VAR, BEGIN, END, etc.)
    - Identifiers (program name, variable names, subroutine names)
    - Numeric literals (integers and floating-point numbers)
    - Single-character operators and punctuation
    - Assignment operator (:=)
    - Comments enclosed in curly braces {}
    - Whitespace handling and position tracking

    The analyzer maintains current position, line, and column information for error reporting
    and debugging purposes.
    """

    # Use __slots__ for memory efficiency - restricts instance attributes to these only
    __slots__ = ("text", "position", "current_char", "line", "column")

    def __init__(self, text: str) -> None:
        """
        Initialize the lexical analyzer with source code text.

        Args:
            text: The source code string to be tokenized
        """
        self.text: str = text  # Source code to analyze
        self.position: int = 0  # Current character position in text
        self.current_char: Optional[str] = (  # Current character being examined
            self.text[self.position] if self.text else None
        )
        self.line: int = 1  # Current line number (1-based)
        self.column: int = 1  # Current column number (1-based)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the analyzer."""
        return f"{self.__class__.__name__}(text={self.text})"

    def __str__(self) -> str:
        """Return a human-readable string showing current analyzer state."""
        return f"Character {self.current_char!r} at position {self.position} (line {self.line}, column {self.column})"

    @staticmethod
    def _build_reserved_keywords() -> dict[str, TokenType]:
        """
        Build a mapping of reserved keyword strings to their corresponding TokenType.

        This method extracts reserved keywords from the TokenType enum by finding
        all token types between PROGRAM and END (inclusive). This approach allows
        for easy maintenance - adding new keywords to the enum automatically
        includes them in the reserved keywords dictionary.

        Returns:
            Dictionary mapping uppercase keyword strings to TokenType values
        """
        token_types_list: list[TokenType] = list(TokenType)
        start_index: int = token_types_list.index(TokenType.PROGRAM)
        end_index: int = token_types_list.index(TokenType.END)

        # Create mapping from keyword string to TokenType for reserved words
        reserved_keywords: dict[str, TokenType] = {
            token_type.value: token_type
            for token_type in token_types_list[start_index : end_index + 1]
        }
        return reserved_keywords

    @staticmethod
    def _build_single_character_token_types() -> dict[str, TokenType]:
        """
        Build a mapping of single-character operators and punctuation to TokenType.

        This method extracts single-character tokens from the TokenType enum by finding
        all token types between PLUS and DOT (inclusive). This includes operators like
        +, -, *, /, parentheses, semicolons, etc.

        Returns:
            Dictionary mapping single characters to TokenType values
        """
        token_types_list: list[TokenType] = list(TokenType)
        start_index: int = token_types_list.index(TokenType.PLUS)
        end_index: int = token_types_list.index(TokenType.DOT)

        # Create mapping from single character to TokenType
        single_character_token_types: dict[str, TokenType] = {
            token_type.value: token_type
            for token_type in token_types_list[start_index : end_index + 1]
        }
        return single_character_token_types

    # Class-level constants built once when the class is defined
    # These are shared across all instances for memory efficiency
    RESERVED_KEYWORDS: dict[str, TokenType] = _build_reserved_keywords()
    SINGLE_CHARACTER_TOKEN_TYPES: dict[str, TokenType] = (
        _build_single_character_token_types()
    )

    def _advance(self) -> None:
        """
        Move to the next character in the source text.

        This method updates line and column counters, advances the position pointer,
        and updates current_char to the new character. Line and column tracking is
        essential for providing meaningful error messages and debugging information.
        """
        # Handle newline - increment line counter and reset column
        if self.current_char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        # Move to next position
        self.position += 1

        # Update current character - None if we've reached the end
        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]

    def _peek(self, offset: int = 1) -> Optional[str]:
        """
        Look ahead at a character without advancing the current position.

        This is useful for multi-character tokens like ":=" where we need to
        check if the next character completes the token before committing
        to consuming the first character.

        Args:
            offset: How many characters ahead to look (default: 1)

        Returns:
            The character at the peek position, or None if beyond text end
        """
        peek_position: int = self.position + offset
        if peek_position >= len(self.text):
            return None
        return self.text[peek_position]

    def _skip_whitespace(self) -> None:
        """
        Skip over whitespace characters (spaces, tabs, newlines, etc.).

        Whitespace is generally not significant in most programming languages
        except for line and column tracking, so we skip over it while maintaining
        accurate position information through _advance().
        """
        while self.current_char is not None and self.current_char.isspace():
            self._advance()

    def _skip_comment(self) -> None:
        """
        Skip over a comment enclosed in curly braces {}.

        Pascal-style comments start with { and end with }. This method
        consumes all characters until the closing } is found. If no closing
        brace is found, the comment extends to the end of the file.
        Note: This assumes we're already positioned at the opening {
        """
        # Skip characters until we find the closing } or reach end of file
        while self.current_char is not None and self.current_char != "}":
            self._advance()

        # If we found the closing brace, consume it
        if self.current_char == "}":
            self._advance()

    def _tokenize_number(self) -> Token:
        """
        Parse a numeric literal (integer or floating-point).

        This method handles integer literals (123, 0, 999) and floating-point
        literals (123.45, 0.5, .5). It validates against invalid formats like
        multiple decimal points or lone decimal points.

        Returns:
            Token with INTEGER_CONSTANT or REAL_CONSTANT type and the numeric value

        Raises:
            LexicalAnalyzerError: For invalid number formats
        """
        number_string: str = ""
        has_decimal_point: bool = False

        # Consume digits and at most one decimal point
        while self.current_char is not None and (
            self.current_char.isdigit() or self.current_char == "."
        ):
            if self.current_char == ".":
                # Check for multiple decimal points - invalid format
                if has_decimal_point:
                    raise LexicalError(
                        ErrorCode.INVALID_NUMBER_FORMAT,
                        "Invalid number format: multiple decimal points",
                        self.position,
                        self.line,
                        self.column,
                    )
                has_decimal_point = True

            number_string += self.current_char
            self._advance()

        # Handle edge case - lone decimal point without digits
        if number_string == ".":
            raise LexicalError(
                ErrorCode.INVALID_NUMBER_FORMAT,
                "Invalid number format: lone decimal point",
                self.position - 1,
                self.line,
                self.column,
            )

        # Return appropriate token type based on whether we found a decimal point
        if has_decimal_point:
            return Token(
                TokenType.REAL_CONSTANT, float(number_string), self.line, self.column
            )
        else:
            return Token(
                TokenType.INTEGER_CONSTANT, int(number_string), self.line, self.column
            )

    def _tokenize_identifier(self) -> Token:
        """
        Parse an identifier or reserved keyword.

        Identifiers start with a letter or underscore and can contain letters,
        digits, and underscores. This method collects all valid identifier
        characters, checks if the result is a reserved keyword (case-insensitive),
        and returns either a keyword token or an ID token.

        Examples:
            "program" -> PROGRAM token (reserved keyword)
            "myVariable" -> ID token
            "_temp123" -> ID token

        Returns:
            Token with the appropriate type (keyword or ID) and the identifier string
        """
        identifier_string: str = ""

        # Collect all alphanumeric characters and underscores
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            identifier_string += self.current_char
            self._advance()

        # Check if this identifier is a reserved keyword - case-insensitive
        uppercase_identifier: str = identifier_string.upper()
        if uppercase_identifier in self.RESERVED_KEYWORDS:
            # Return the specific keyword token type
            return Token(
                self.RESERVED_KEYWORDS[uppercase_identifier],
                identifier_string,  # Preserve original case in token value
                self.line,
                self.column,
            )
        else:
            # Return regular identifier token
            return Token(TokenType.ID, identifier_string, self.line, self.column)

    def next_token(self) -> Token:
        """
        Get the next token from the input stream.

        This is the main public method of the lexical analyzer. It skips whitespace
        and comments, identifies the type of the next token, calls the appropriate
        tokenization method, and returns a Token object with type, value, and
        position information.

        The method handles various token types in order of complexity:
        - EOF (end of file)
        - Numbers (integers and floats)
        - Identifiers and keywords
        - Multi-character operators (:=)
        - Single-character operators and punctuation

        Returns:
            Token object representing the next lexical unit

        Raises:
            LexicalAnalyzerError: For invalid characters or malformed tokens
        """
        # Skip any leading whitespace
        self._skip_whitespace()

        # Skip comments - which might be followed by more whitespace
        while self.current_char == "{":
            self._skip_comment()
            self._skip_whitespace()

        # Handle end of file
        if self.current_char is None:
            return Token(TokenType.EOF, None, self.line, self.column)

        # Handle numeric literals starting with a digit
        if self.current_char.isdigit():
            return self._tokenize_number()

        # Handle numeric literals starting with a decimal point (e.g., .5)
        if self.current_char == ".":
            next_character: Optional[str] = self._peek()
            if next_character is not None and next_character.isdigit():
                return self._tokenize_number()
            # If . is not followed by a digit, fall through to single-char handling

        # Handle identifiers and reserved keywords
        if self.current_char.isalpha() or self.current_char == "_":
            return self._tokenize_identifier()

        # Handle multi-character assignment operator ":="
        if self.current_char == ":" and self._peek(1) == "=":
            self._advance()  # Consume ':'
            self._advance()  # Consume '='
            return Token(TokenType.ASSIGN, ":=", self.line, self.column)

        # Handle single-character operators and punctuation
        if self.current_char in self.SINGLE_CHARACTER_TOKEN_TYPES:
            token_type: TokenType = self.SINGLE_CHARACTER_TOKEN_TYPES[self.current_char]
            character: str = self.current_char
            self._advance()
            return Token(token_type, character, self.line, self.column)

        # If we reach here, we encountered an invalid character
        raise LexicalError(
            ErrorCode.INVALID_CHARACTER,
            f"Invalid character: '{self.current_char}'",
            self.position,
            self.line,
            self.column,
        )
