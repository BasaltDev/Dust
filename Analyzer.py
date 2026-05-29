# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

import sys

from AST import (
    BinOp,
    Literal,
    UnaryOp,
)
from Error import ErrorIDs, ErrorInfo, ErrorType, error, error_exit

python_to_dust_type_map = {str: "string", int: "int", float: "float", bool: "bool"}


def _exit(error_info, code=1):
    error_exit(error_info)
    sys.exit(code)


def _error(
    error_info: ErrorInfo, error_type, error_id: ErrorIDs, position_info: str, *args
):
    error(error_info, error_type, error_id, position_info, *args)


errored = False


class Env:
    def __init__(self, errinfomod, parent=None):
        self.symbols = {}
        self.errinfomod = errinfomod
        self.parent = parent

    def define(self, name, typ="var", const=False, **kwargs):
        dictionary = {"type": typ, "const": const}
        for k, v in kwargs.items():
            dictionary[k] = v
        self.symbols[name] = dictionary

    def lookup(self, name, node=None):
        global errored
        if name not in self.symbols:
            if self.parent:
                return self.parent.lookup(name, node)
            if node is None:
                print("An internal error within the Dust interpreter happened.")
                _exit(self.errinfomod, 1)
            _error(
                self.errinfomod,
                ErrorType.UndefinedSymbol,
                ErrorIDs.UndefinedSymbol,
                f"{node.line}-{node.lineEnd}:{node.col}-{node.colEnd}",
                name,
            )
            errored = True
            return None
        else:
            return self.symbols[name]

    def __repr__(self):
        return f"Env(symbols={self.symbols}, parent={self.parent})"


class Analyzer:
    def __init__(
        self,
        ast,
        filename="<stdin>",
        error_info_module=None,
        env=None,
        loop=False,
        function=False,
    ):
        self.ast = ast
        self.filename = filename
        self.errinfomod = error_info_module
        self.env = env if env is not None else Env(self.errinfomod)
        self.loop = loop
        self.function = function
        self.pos = -1
        self.cn = None
        self.adv()

    def adv(self, amt=1):
        self.pos += amt
        self.cn = None if self.pos >= len(self.ast) else self.ast[self.pos]

    def resolve_literal(self, value: Literal):
        return (
            value.value
            if value.type != "Ident"
            else self.env.lookup(value.value, node=value)
        )

    def handle_expression(self, expr: BinOp | UnaryOp | Literal):
        global errored
        if isinstance(expr, Literal):
            self.resolve_literal(expr)
            return
        elif isinstance(expr, UnaryOp):
            self.handle_expression(expr.rhs)
            return
        if not isinstance(expr, (BinOp, UnaryOp, Literal)):
            return
        if expr.op in "\\/%":
            if isinstance(expr.rhs, Literal) and expr.rhs.value == 0:
                _error(
                    self.errinfomod,
                    ErrorType.ZeroDivision,
                    ErrorIDs.ZeroDivision,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    True,
                )
                errored = True

    def resolve_truthiness(self, node):
        global errored
        if isinstance(self.cn.condition, Literal) and not isinstance(
            self.cn.condition.value, bool
        ):
            _error(
                self.errinfomod,
                ErrorType.ConditionalTypeMismatch,
                ErrorIDs.ConditionalTypeMismatch,
                f"{self.cn.condition.line}-{self.cn.condition.lineEnd}:{self.cn.condition.col}-{self.cn.condition.colEnd}",
                python_to_dust_type_map[type(self.cn.condition.value)],
            )
            errored = True
        return False

    def analyze(self):
        global errored
        while self.cn is not None:
            match self.cn.node_type():
                case "PrintStatement":
                    for i in self.cn.values:
                        self.handle_expression(i)
                case "LetStatement":
                    self.env.define(self.cn.name, "var", const=self.cn.const)
                case "VariableReassignment":
                    value = self.env.lookup(self.cn.name, self.cn)
                    if not isinstance(value, dict):
                        print("An internal error within the Dust interpreter happened.")
                        sys.exit(1)
                    const = value.get("const")
                    if const:
                        _error(
                            self.errinfomod,
                            ErrorType.ConstReassignment,
                            ErrorIDs.ConstReassignment,
                            f"{self.cn.line}-{self.cn.lineEnd}:{self.cn.col}-{self.cn.colEnd}",
                            self.cn.name,
                        )
                        errored = True
                    self.env.define(self.cn.name, "var")
                case "IfStatement":
                    self.resolve_truthiness(self.cn.condition)
                    Analyzer(
                        self.cn.true_body,
                        self.filename,
                        self.errinfomod,
                        env=Env(self.errinfomod, self.env),
                        loop=self.loop,
                        function=self.function,
                    ).analyze()
                    Analyzer(
                        self.cn.false_body,
                        self.filename,
                        self.errinfomod,
                        env=Env(self.errinfomod, self.env),
                        loop=self.loop,
                        function=self.function,
                    ).analyze()
                case "WhileStatement":
                    self.resolve_truthiness(self.cn.condition)
                    Analyzer(
                        self.cn.body,
                        self.filename,
                        self.errinfomod,
                        env=Env(self.errinfomod, self.env),
                        loop=True,
                        function=self.function,
                    ).analyze()
                case "BreakStatement":
                    if not self.loop:
                        _error(
                            self.errinfomod,
                            ErrorType.KeywordOutsideOfContext,
                            ErrorIDs.KeywordOutsideOfContext,
                            f"{self.cn.line}-{self.cn.lineEnd}:{self.cn.col}-{self.cn.colEnd}",
                            "break",
                            "loop",
                        )
                        errored = True
                case "ContinueStatement":
                    if not self.loop:
                        _error(
                            self.errinfomod,
                            ErrorType.KeywordOutsideOfContext,
                            ErrorIDs.KeywordOutsideOfContext,
                            f"{self.cn.line}-{self.cn.lineEnd}:{self.cn.col}-{self.cn.colEnd}",
                            "continue",
                            "loop",
                        )
                        errored = True
                case "FunctionStatement":
                    self.env.define(
                        self.cn.name,
                        "function",
                        params=self.cn.params,
                    )
                    env = Env(self.errinfomod, parent=self.env)
                    for i in self.cn.params:
                        env.define(i, "var", const=True)
                    Analyzer(
                        self.cn.body,
                        self.filename,
                        self.errinfomod,
                        function=True,
                        env=env,
                    ).analyze()
                case "FunctionCall":
                    func = self.env.lookup(self.cn.name, self.cn)
                    if func["type"] != "function":
                        _error(
                            self.errinfomod,
                            ErrorType.NotAFunction,
                            ErrorIDs.NotAFunction,
                            f"{self.cn.line}-{self.cn.lineEnd}:{self.cn.col}-{self.cn.colEnd}",
                            self.cn.name,
                        )
                        errored = True
                    if len(self.cn.args) != len(func["params"]):
                        _error(
                            self.errinfomod,
                            ErrorType.ArgumentCountMismatch,
                            ErrorIDs.ArgumentCountMismatch,
                            f"{self.cn.line}-{self.cn.lineEnd}:{self.cn.col}-{self.cn.colEnd}",
                            self.cn.name,
                            len(func["params"]),
                            len(self.cn.args),
                        )
                        errored = True
                    for arg in self.cn.args:
                        self.handle_expression(arg)
                case "ReturnStatement":
                    if not self.function:
                        _error(
                            self.errinfomod,
                            ErrorType.KeywordOutsideOfContext,
                            ErrorIDs.KeywordOutsideOfContext,
                            f"{self.cn.line}-{self.cn.lineEnd}:{self.cn.col}-{self.cn.colEnd}",
                            "return",
                            "function",
                        )
                        errored = True
            self.adv()
        if errored:
            _exit(self.errinfomod, 1)
