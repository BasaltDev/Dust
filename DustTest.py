# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

import subprocess
import sys
from enum import Enum, auto

from coloring import Fore


class TokenType(Enum):
    IDENTIFIER = auto()
    KEYWORD = auto()
    STRING = auto()
    NUMBER = auto()

    LEFTBRACE = auto()
    RIGHTBRACE = auto()

    LEFTBRACKET = auto()
    RIGHTBRACKET = auto()

    EQ = auto()
    NEQ = auto()

    ASSIGN = auto()

    COMMA = auto()


class Token:
    def __init__(self, typ, value, line=None):
        self.type = typ
        self.value = value
        self.line = line

    def __eq__(self, value):
        if not isinstance(value, (Token, TokenType)):
            return False
        if isinstance(value, TokenType):
            return value == self.type
        return value.type == self.type and value.value == self.value

    def __repr__(self):
        return f"Token(type={self.type}, value={repr(self.value)}, line={self.line})"


class DustTestLexer:
    KEYWORDS = {
        "test": TokenType.KEYWORD,
        "group": TokenType.KEYWORD,
        "run": TokenType.KEYWORD,
        "run_test": TokenType.KEYWORD,
        "run_group": TokenType.KEYWORD,
        "expect": TokenType.KEYWORD,
        "otherwise": TokenType.KEYWORD,
        "contains": TokenType.KEYWORD,
        "log": TokenType.KEYWORD,
    }

    def __init__(self, src, filename):
        self.src = src
        self.filename = filename
        self.line = 1
        self.pos = -1
        self.cc = None
        self.tokens = []
        self.adv()

    def adv(self, amt=1):
        self.pos += amt
        self.cc = None if self.pos >= len(self.src) else self.src[self.pos]
        if self.cc == "\n":
            self.line += 1

    def peek(self, amt=1):
        return None if self.pos + amt >= len(self.src) else self.src[self.pos + amt]

    def make_token(self, typ, value=None, line=None):
        self.tokens.append(Token(typ, value, line))

    def error(self):
        print(f"An error occured at line {self.line}")
        sys.exit(1)

    def lex(self):
        while self.cc is not None:
            if self.cc in " \n\t\r":
                self.adv()
                continue
            if self.cc.isalpha() or self.cc == "_":
                out = self.cc
                ln = self.line
                while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
                    out += self.peek()
                    self.adv()
                typ = TokenType.IDENTIFIER
                if out in self.KEYWORDS:
                    typ = self.KEYWORDS[out]
                self.make_token(typ, out, ln)
            elif self.cc.isdigit():
                out = self.cc
                ln = self.line
                while self.peek() and (self.peek().isdigit() or self.peek() == "."):
                    out += self.peek()
                    self.adv()
                self.make_token(
                    TokenType.NUMBER, float(out) if "." in out else int(out), ln
                )
            elif self.cc == "-" and self.peek().isdigit():
                self.adv()
            elif self.cc == '"':
                out = ""
                while self.peek() and self.peek() != '"':
                    if self.peek() == "\n":
                        self.error()
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
                self.make_token(
                    TokenType.STRING,
                    out,
                    self.line,
                )
            elif self.cc == "/" and self.peek() == "/":
                self.adv(2)
                while self.cc and self.cc != "\n":
                    self.adv()
            elif self.cc == "/" and self.peek() == "*":
                self.adv(2)
                while self.cc and (self.peek(-1) + self.cc != "*/"):
                    self.adv()
            elif self.cc == "{":
                self.make_token(TokenType.LEFTBRACE, line=self.line)
            elif self.cc == "}":
                self.make_token(TokenType.RIGHTBRACE, line=self.line)
            elif self.cc == "[":
                self.make_token(TokenType.LEFTBRACKET, line=self.line)
            elif self.cc == "]":
                self.make_token(TokenType.RIGHTBRACKET, line=self.line)
            elif self.cc == ",":
                self.make_token(TokenType.COMMA, line=self.line)
            elif self.peek() == "=" and self.cc in "!=":
                self.make_token(
                    TokenType.EQ if self.cc == "=" else TokenType.NEQ, line=self.line
                )
                self.adv()
            elif self.cc == "=":
                self.make_token(TokenType.ASSIGN, line=self.line)
            self.adv()
        return self.tokens


class Literal:
    def __init__(self, typ, value):
        self.typ = typ
        self.value = value

    def __eq__(self, value):
        if not isinstance(value, Literal):
            return False
        return value.typ == self.typ and value.value == self.value

    def __repr__(self):
        return f"Literal(typ={self.typ}, value={repr(self.value)})"


class Assignment:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Assignment(name={self.name}, value={repr(self.value)})"


class Run:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Run(value={self.value})"


class Comparison:
    def __init__(self, lhs, rhs, op):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def __repr__(self):
        return f"Comparison(lhs={self.lhs}, rhs={self.rhs}, op='{self.op}')"


class Expect:
    def __init__(self, cmp, otherwise=None):
        self.cmp = cmp
        self.otherwise = otherwise

    def __repr__(self):
        return f"Expect(cmp={self.cmp}, otherwise={self.otherwise})"


class Test:
    def __init__(self, name, ast):
        self.name = name
        self.ast = ast

    def __repr__(self):
        return f"Test(name={self.name}, ast={self.ast})"


class Group:
    def __init__(self, name, ast):
        self.name = name
        self.ast = ast

    def __repr__(self):
        return f"Test(name={self.name}, ast={self.ast})"


class RunTest:
    def __init__(self, test):
        self.test = test

    def __repr__(self):
        return f"RunTest(test={self.test})"


class RunGroup:
    def __init__(self, test):
        self.test = test

    def __repr__(self):
        return f"RunGroup(test={self.test})"


class Log:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Log(value={self.value})"


class DustTestParser:
    def __init__(self, src, filename, src_available=True):
        if src_available:
            self.tokens = DustTestLexer(src, filename).lex()
        else:
            self.tokens = src
        self.filename = filename
        self.ast = []
        self.pos = -1
        self.ct = None
        self.adv()

    def adv(self, amt=1):
        self.pos += amt
        self.ct = None if self.pos >= len(self.tokens) else self.tokens[self.pos]

    def peek(self, amt=1):
        return (
            None if self.pos + amt >= len(self.tokens) else self.tokens[self.pos + amt]
        )

    def parse_value(self):
        if self.ct == TokenType.IDENTIFIER:
            return Literal("ident", self.ct.value)
        elif self.ct == TokenType.LEFTBRACKET:
            values = []
            self.adv()
            while self.ct and self.ct != TokenType.RIGHTBRACKET:
                values.append(self.parse_value())
                if self.ct != TokenType.RIGHTBRACKET:
                    self.adv()
                if self.ct == TokenType.COMMA:
                    self.adv()
            value = Literal("array", values)
            return value
        else:
            return Literal(
                (
                    "number"
                    if isinstance(self.ct.value, (int, float))
                    else "array"
                    if isinstance(self.ct.value, list)
                    else "string"
                ),
                self.ct.value,
            )

    def parse_comparison(self):
        lhs = self.parse_value()
        self.adv()
        op = self.ct.value or self.ct.type.name.lower()
        self.adv()
        rhs = self.parse_value()
        return Comparison(lhs, rhs, op)

    def parse_statement(self):
        if self.ct == TokenType.KEYWORD:
            if self.ct.value == "run":
                self.adv()
                return Run(self.parse_value())
            elif self.ct.value == "expect":
                self.adv()
                cmp = self.parse_comparison()
                otherwise = None
                if self.peek() == Token(TokenType.KEYWORD, "otherwise"):
                    self.adv(2)
                    otherwise = self.parse_value()
                return Expect(cmp, otherwise)
            elif self.ct.value == "test":
                self.adv()
                name = self.parse_value()
                self.adv(2)
                block = 1
                tokens = []
                while self.ct:
                    if self.ct == TokenType.LEFTBRACE:
                        block += 1
                    if self.ct == TokenType.RIGHTBRACE:
                        block -= 1
                    if block == 0:
                        break
                    tokens.append(self.ct)
                    self.adv()
                ast = DustTestParser(tokens, self.filename, src_available=False).parse()
                return Test(name, ast)
            elif self.ct.value == "group":
                self.adv()
                name = self.parse_value()
                self.adv(2)
                block = 1
                tokens = []
                while self.ct:
                    if self.ct == TokenType.LEFTBRACE:
                        block += 1
                    if self.ct == TokenType.RIGHTBRACE:
                        block -= 1
                    if block == 0:
                        break
                    tokens.append(self.ct)
                    self.adv()
                ast = DustTestParser(tokens, self.filename, src_available=False).parse()
                tests = []
                buffer = []
                for i in ast:
                    if isinstance(i, Test):
                        tests.append(i)
                        buffer.append(RunTest(i.name))
                tests += buffer
                return Group(name, tests)
            elif self.ct.value == "run_test":
                self.adv()
                name = self.parse_value()
                return RunTest(name)
            elif self.ct.value == "run_group":
                self.adv()
                name = self.parse_value()
                return RunGroup(name)
            elif self.ct.value == "log":
                self.adv()
                return Log(self.parse_value())
        elif self.ct == TokenType.IDENTIFIER and self.peek() == TokenType.ASSIGN:
            name = self.ct.value
            self.adv(2)
            value = self.parse_value()
            return Assignment(name, value)

    def parse(self):
        while self.ct is not None:
            self.ast.append(self.parse_statement())
            self.adv()
        return self.ast


env = {
    "variables": {"STDIN": []},
    "stdout": "",
    "exit": None,
    "error": "",
    "tests": {},
    "groups": {},
}
tests = [0, 0]


class DustTestInterpreter:
    def __init__(self, ast, test_name_prefix="", parent=False):
        self.ast = ast
        self.parent = parent
        self.pos = -1
        self.cn: Assignment | Run | Test | RunTest = None
        self.test_name_prefix = test_name_prefix
        self.adv()

    def adv(self):
        self.pos += 1
        self.cn = None if self.pos >= len(self.ast) else self.ast[self.pos]

    def resolve(self, value):
        if isinstance(value, Literal):
            if value.typ == "ident":
                if value.value in ("stdout", "exit", "error"):
                    return env[value.value]
                return env["variables"][value.value]
            elif value.typ == "array":
                return [self.resolve(val) for val in value.value]
            return value.value

    def resolve_comparison(self, comp: Comparison):
        lhs = self.resolve(comp.lhs)
        rhs = self.resolve(comp.rhs)
        if comp.op == "eq":
            if comp.lhs == Literal("ident", "stdout") and isinstance(rhs, list):
                rhs = "\n".join([str(val) for val in rhs])
            return lhs == rhs
        elif comp.op == "neq":
            return lhs != rhs
        elif comp.op == "contains":
            return rhs in lhs

    def interpret(self):
        while self.cn is not None:
            if isinstance(self.cn, Assignment):
                env["variables"][self.cn.name] = self.resolve(self.cn.value)
            elif isinstance(self.cn, Test):
                env["tests"][self.resolve(self.cn.name)] = self.cn.ast
            elif isinstance(self.cn, Group):
                env["groups"][self.resolve(self.cn.name)] = self.cn.ast
            elif isinstance(self.cn, Run):
                result: subprocess.CompletedProcess = subprocess.run(
                    ["python", "-S", "dust.py", "--run", self.resolve(self.cn.value)],
                    capture_output=True,
                    input="\n".join(str(val) for val in env["variables"]["STDIN"]),
                    text=True,
                    encoding="utf-8",
                )
                env["variables"]["STDIN"] = ""
                env["stdout"] = result.stdout.strip()
                env["exit"] = result.returncode
                if env["exit"] != 0:
                    last_index = result.stdout.rfind("Error[")
                    if not last_index:
                        self.adv()
                        continue
                    idx = last_index + 6
                    error_code = result.stdout[idx]
                    while result.stdout[idx] != "]":
                        idx += 1
                    error_code = result.stdout[last_index + 6 : idx]
                    env["error"] = error_code
                else:
                    env["error"] = -1
            elif isinstance(self.cn, Expect):
                truth = self.resolve_comparison(self.cn.cmp)
                if not truth:
                    return self.resolve(self.cn.otherwise) or "assertion failed"
            elif isinstance(self.cn, RunTest):
                name = self.resolve(self.cn.test)
                print(f"Running test `{name}`...")
                result = DustTestInterpreter(env["tests"][name]).interpret()
                if result is None:
                    print(
                        f"Test `{self.test_name_prefix}{name}` {Fore.GREEN}ran \
successfully{Fore.RESET}, no issues"
                    )
                    tests[0] += 1
                else:
                    print(
                        f"Test `{self.test_name_prefix}{name}` {Fore.RED}did not run \
successfully{Fore.RESET}: {result}"
                    )
                    tests[1] += 1
            elif isinstance(self.cn, RunGroup):
                name = self.resolve(self.cn.test)
                result = DustTestInterpreter(
                    env["groups"][name], test_name_prefix=name + "/"
                ).interpret()
                if result is None:
                    print(
                        f"Test group `{name}` {Fore.GREEN}ran successfully{Fore.RESET},\
 no issues"
                    )
                else:
                    print(
                        f"Test group `{name}` {Fore.RED}did not run successfully\
{Fore.RESET}:{result}"
                    )
            elif isinstance(self.cn, Log):
                print(self.resolve(self.cn.value))
            self.adv()
