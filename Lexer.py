# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

import sys
import types

from Error import ErrorIDs, ErrorType, error, error_exit
from Token import Token, TokenType


def _exit(error_info, code=1):
    error_exit(error_info)
    sys.exit(code)


class Lexer:
    KEYWORDS = {
        "true": TokenType.BOOLEAN,
        "false": TokenType.BOOLEAN,
        "print": TokenType.KEYWORD,
        "let": TokenType.KEYWORD,
        "const": TokenType.KEYWORD,
        "if": TokenType.KEYWORD,
        "else": TokenType.KEYWORD,
        "while": TokenType.KEYWORD,
        "break": TokenType.KEYWORD,
        "continue": TokenType.KEYWORD,
        "input": TokenType.KEYWORD,
        "func": TokenType.KEYWORD,
        "return": TokenType.KEYWORD,
        "for": TokenType.KEYWORD,
        "in": TokenType.KEYWORD,
        "struct": TokenType.KEYWORD,
        "implement": TokenType.KEYWORD,
        "int": TokenType.DATA_TYPE,
        "float": TokenType.DATA_TYPE,
        "string": TokenType.DATA_TYPE,
        "bool": TokenType.DATA_TYPE,
        "array": TokenType.DATA_TYPE,
    }
    DOUBLE_CHAR_COMBINATIONS = {
        "==": TokenType.EQUALS,
        "!=": TokenType.NOTEQUALS,
        "<=": TokenType.LESSTHANOREQUAL,
        ">=": TokenType.GREATERTHANOREQUAL,
        "&&": TokenType.AND,
        "||": TokenType.OR,
        "++": TokenType.INCREMENT,
        "--": TokenType.DECREMENT,
        "+=": lambda: TokenType.COMPOUNDASSIGNMENT,
        "-=": lambda: TokenType.COMPOUNDASSIGNMENT,
        "*=": lambda: TokenType.COMPOUNDASSIGNMENT,
        "/=": lambda: TokenType.COMPOUNDASSIGNMENT,
        "%=": lambda: TokenType.COMPOUNDASSIGNMENT,
        "\\=": lambda: TokenType.COMPOUNDASSIGNMENT,
    }
    CHAR_TO_TOKEN_TABLE = {
        ".": TokenType.PERIOD,
        ",": TokenType.COMMA,
        ":": TokenType.COLON,
        ";": TokenType.SEMICOLON,
        "(": TokenType.LEFTPAREN,
        ")": TokenType.RIGHTPAREN,
        "[": TokenType.LEFTBRACKET,
        "]": TokenType.RIGHTBRACKET,
        "{": TokenType.LEFTBRACE,
        "}": TokenType.RIGHTBRACE,
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "/": TokenType.SLASH,
        "\\": TokenType.BACKSLASH,
        "%": TokenType.MOD,
        "!": TokenType.NOT,
        "=": TokenType.ASSIGN,
        "<": TokenType.LESSTHAN,
        ">": TokenType.GREATERTHAN,
    }

    def __init__(self, source, filename="<stdin>", error_info_module=None):
        self.source = source
        self.filename = filename
        self.errinfomod = error_info_module
        self.pos = -1
        self.cc = None
        self.line = 1
        self.col = 0
        self.tokens = []
        self.errored = False
        self.adv()

    def __repr__(self):
        return f"Lexer(filename={self.filename})"

    def adv(self, amt=1):
        self.pos += amt
        self.col += 1
        self.cc = None if self.pos >= len(self.source) else self.source[self.pos]
        if self.cc == "\n":
            self.line += 1
            self.col = 0

    def peek(self, amt=1):
        return (
            None
            if (self.pos + amt >= len(self.source) or self.pos + amt < 0)
            else self.source[self.pos + amt]
        )

    def make_token(self, typ, value=None, line=None, col=None, colEnd=None):
        self.tokens.append(Token(typ, value, line, col, colEnd))

    def tokenize(self):
        comment = 0
        while self.cc is not None:
            if comment > 0:
                if comment == 1 and self.cc == "\n":
                    comment = 0
                elif comment == 2 and self.cc == "/" and self.peek(-1) == "*":
                    comment = 0
                self.adv()
                continue
            if self.cc in " \n\r":
                self.adv()
                continue
            if self.cc.isalpha() or self.cc == "_":
                col = self.col
                out = self.cc
                while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
                    out += self.peek()
                    self.adv()
                typ = TokenType.IDENTIFIER
                if out in self.KEYWORDS:
                    typ = self.KEYWORDS[out]
                    if typ == TokenType.BOOLEAN:
                        out = True if out == "true" else False
                self.make_token(
                    typ,
                    out,
                    line=self.line,
                    col=col,
                    colEnd=self.col + 1,
                )
            elif self.cc.isdigit():
                col = self.col
                out = self.cc
                while self.peek() and (self.peek().isdigit() or self.peek() == "."):
                    out += self.peek()
                    self.adv()
                typ = TokenType.INTEGER
                if "." in out:
                    typ = TokenType.FLOAT
                    if out.count(".") > 1:
                        error(
                            self.errinfomod,
                            ErrorType.MalformedFloat,
                            ErrorIDs.MalformedFloat,
                            f"{self.line}:{col}-{self.col + 1}",
                            out,
                        )
                        self.errored = True
                        self.adv()
                        continue
                    out = float(out)
                else:
                    out = int(out)
                self.make_token(
                    typ,
                    out,
                    line=self.line,
                    col=col,
                    colEnd=self.col + 1,
                )
            elif self.cc == '"':
                col = self.col
                out = ""
                errored = False
                while self.peek() and self.peek() != '"':
                    if self.peek() == "\n":
                        error(
                            self.errinfomod,
                            ErrorType.MalformedString,
                            ErrorIDs.MalformedString,
                            f"{self.line}:{self.col - 1}-{self.col + 1}",
                            '"' + out,
                        )
                        errored = True
                        self.errored = True
                    if self.peek() == "\\":
                        self.adv()
                        if self.peek() == "n":
                            out += "\n"
                        elif self.peek() == "t":
                            out += "\t"
                        elif self.peek() == "r":
                            out += "\r"
                        elif self.peek() == "b":
                            out += "\b"
                        elif self.peek() == "a":
                            out += "\a"
                        elif self.peek() == "f":
                            out += "\f"
                        elif self.peek() == "v":
                            out += "\v"
                        elif self.peek() == '"':
                            out += '"'
                        elif self.peek() == "\\":
                            out += "\\"
                        elif self.peek() == "0":
                            out += "\0"
                        elif (
                            self.peek().isdigit()
                            and self.peek(2)
                            and self.peek(2).isdigit()
                        ):
                            digits = ""
                            for _ in range(3):
                                digits += self.peek()
                                self.adv()
                            self.adv(-1)
                            out += chr(int(digits, 8))
                        elif self.peek() == "x":
                            self.adv()
                            digits = ""
                            for _ in range(2):
                                digits += self.peek()
                                self.adv()
                            self.adv(-1)
                            out += chr(int(digits, 16))
                        elif self.peek() == "u":
                            self.adv()
                            digits = ""
                            for _ in range(4):
                                digits += self.peek()
                                self.adv()
                            self.adv(-1)
                            out += chr(int(digits, 16))
                        elif self.peek() == "U":
                            self.adv()
                            digits = ""
                            for _ in range(8):
                                digits += self.peek()
                                self.adv()
                            self.adv(-1)
                            out += chr(int(digits, 16))
                        else:
                            out += f"\\{self.peek()}"
                    else:
                        out += self.peek()
                    self.adv()
                self.adv()
                if errored:
                    self.adv()
                    continue
                self.make_token(
                    TokenType.STRING,
                    out,
                    line=self.line,
                    col=col,
                    colEnd=self.col + 1,
                )
            elif self.cc == "/" and self.peek() == "/":
                comment = 1
                self.adv()
            elif self.cc == "/" and self.peek() == "*":
                comment = 2
                self.adv()
            elif (
                self.peek() is not None
                and self.cc + self.peek() in self.DOUBLE_CHAR_COMBINATIONS
            ):
                if isinstance(
                    self.DOUBLE_CHAR_COMBINATIONS[self.cc + self.peek()],
                    types.FunctionType,
                ):
                    self.make_token(
                        self.DOUBLE_CHAR_COMBINATIONS[self.cc + self.peek()](),
                        self.cc + self.peek(),
                        line=self.line,
                        col=self.col,
                        colEnd=self.col + 2,
                    )
                else:
                    self.make_token(
                        self.DOUBLE_CHAR_COMBINATIONS[self.cc + self.peek()],
                        line=self.line,
                        col=self.col,
                        colEnd=self.col + 2,
                    )
                self.adv()
            elif self.cc in self.CHAR_TO_TOKEN_TABLE:
                self.make_token(
                    self.CHAR_TO_TOKEN_TABLE[self.cc],
                    line=self.line,
                    col=self.col,
                    colEnd=self.col + 1,
                )
            else:
                error(
                    self.errinfomod,
                    ErrorType.UnexpectedCharacter,
                    ErrorIDs.UnexpectedCharacter,
                    f"{self.line}:{self.col}-{self.col + 1}",
                    self.cc,
                )
                self.errored = True
            self.adv()
        if self.errored:
            _exit(self.errinfomod, 1)
        return self.tokens
