# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

import sys

from AST import (
    BinOp,
    DotAccess,
    GetItem,
    Literal,
    StructInit,
    UnaryOp,
)
from Error import ErrorIDs, ErrorInfo, ErrorType, error, error_exit

python_to_dust_type_map = {
    str: "string",
    int: "int",
    float: "float",
    bool: "bool",
    list: "array",
}


def _exit(error_info, code=1):
    error_exit(error_info)
    sys.exit(code)


errored = False


def _error(
    error_info: ErrorInfo,
    error_type,
    error_id: ErrorIDs,
    position_info: str,
    *args,
    **kwargs,
):
    global errored
    errored = True
    error(error_info, error_type, error_id, position_info, *args, **kwargs)


class Env:
    def __init__(self, errinfomod, parent=None):
        self.symbols = (
            {}
            if parent
            else {
                "RECURSION_LIMIT": {"type": "var", "const": True},
                "push": {
                    "type": "function",
                    "const": True,
                    "params": {"arr": "array", "value": "dynamic"},
                },
                "len": {
                    "type": "function",
                    "const": True,
                    "params": {"value": "dynamic"},
                },
                "range": {
                    "type": "function",
                    "const": True,
                    "params": {"start": "dynamic", "end": "dynamic"},
                },
                "remove": {
                    "type": "function",
                    "const": True,
                    "params": {"arr": "array", "index": "int"},
                },
                "insert": {
                    "type": "function",
                    "const": True,
                    "params": {"arr": "array", "index": "int", "value": "dynamic"},
                },
                "pop": {"type": "function", "const": True, "params": {"arr": "array"}},
            }
        )
        self.errinfomod = errinfomod
        self.parent = parent

    def define(self, name, typ="var", const=False, ret_result=False, **kwargs):
        dictionary = {"type": typ, "const": const}
        for k, v in kwargs.items():
            dictionary[k] = v
        if ret_result:
            return dictionary
        self.symbols[name] = dictionary

    def lookup(self, name, node=None, fail=True):
        global errored
        if name not in self.symbols:
            if self.parent:
                return self.parent.lookup(name, node, fail=fail)
            if not fail:
                return
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
        if value.type == "Array":
            return [self.handle_expression(x) for x in value.value]
        elif value.type == "Ident":
            return self.env.lookup(value.value, node=value)
        else:
            return value.value

    def resolve_nested_dotaccess(self, da: DotAccess, leave_da_last=False):
        if not isinstance(da, DotAccess):
            return da
        elif not isinstance(da.lhs, DotAccess):
            if leave_da_last:
                return da
            return da.lhs
        return self.resolve_nested_dotaccess(da).lhs

    def resolve_nested_dotaccess_list(self, da: DotAccess):
        if not isinstance(da, DotAccess):
            return da
        elif not isinstance(da.lhs, DotAccess):
            return [da.lhs]
        return [self.resolve_nested_dotaccess_list(da).lhs]

    def handle_expression(
        self, expr: BinOp | UnaryOp | Literal | StructInit | DotAccess
    ):
        global errored
        if isinstance(expr, Literal):
            return self.resolve_literal(expr)
        elif isinstance(expr, UnaryOp):
            return self.handle_expression(expr.rhs)
        elif isinstance(expr, StructInit):
            data = self.env.lookup(expr.name)
            methodless = data["fields"]
            for i, v in methodless.copy().items():
                if isinstance(v, list) and v[0] == "method":
                    del methodless[i]
            if len(methodless) != len(expr.fields):
                _error(
                    self.errinfomod,
                    ErrorType.ArgumentCountMismatch,
                    ErrorIDs.ArgumentCountMismatch,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    expr.name,
                    len(methodless),
                    len(expr.fields),
                    typ="struct",
                )
            for field, value in expr.fields.items():
                if field not in data["fields"]:
                    _error(
                        self.errinfomod,
                        ErrorType.NotAStructField,
                        ErrorIDs.NotAStructField,
                        f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                        expr.name,
                        field,
                    )
                self.handle_expression(value)
            return data
        elif expr.node_type() == "DotAccess":
            lhs = expr.lhs
            if isinstance(expr.lhs, DotAccess):
                lhs = self.handle_expression(expr.lhs)
                data = lhs
                structdata = self.env.lookup(data.get("data_type"), expr)
            else:
                data = self.env.lookup(lhs, expr)
                structdata = self.env.lookup(data.get("data_type"), expr)
            rezzed = self.resolve_nested_dotaccess(expr.lhs, True)
            if (
                isinstance(rezzed, DotAccess)
                and rezzed.rhs not in data["fields"]
                and rezzed.rhs not in structdata["fields"]
            ):
                _error(
                    self.errinfomod,
                    ErrorType.NotAStructField,
                    ErrorIDs.NotAStructField,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    self.resolve_nested_dotaccess(expr.lhs),
                    expr.rhs,
                )
            return data
        elif expr.node_type() in [
            "InputStatement",
        ]:
            return "ok"
        elif expr.node_type() == "FunctionCall":
            self.analyze_function_call(expr)
            return "ok"
        if not isinstance(expr, (BinOp, UnaryOp, Literal, StructInit)):
            return
        erroredrn = False
        if isinstance(self.handle_expression(expr.lhs), list):
            if not isinstance(self.handle_expression(expr.rhs), list):
                _error(
                    self.errinfomod,
                    ErrorType.OperatorTypeMismatch,
                    ErrorIDs.OperatorTypeMismatch,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    expr.op,
                    python_to_dust_type_map[type(self.handle_expression(expr.lhs))],
                    python_to_dust_type_map[type(self.handle_expression(expr.rhs))],
                )
                erroredrn = True
        if expr.op in "\\/%":
            if isinstance(expr.rhs, Literal) and expr.rhs.value == 0:
                _error(
                    self.errinfomod,
                    ErrorType.ZeroDivision,
                    ErrorIDs.ZeroDivision,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    True,
                )
                erroredrn = True
        return not erroredrn

    def resolve_truthiness(self, node):
        global errored
        if (
            isinstance(node.condition, Literal)
            and not isinstance(node.condition.value, bool)
            and not node.condition.type == "Ident"
        ):
            _error(
                self.errinfomod,
                ErrorType.ConditionalTypeMismatch,
                ErrorIDs.ConditionalTypeMismatch,
                f"{node.condition.line}-{node.condition.lineEnd}:{node.condition.col}-{node.condition.colEnd}",
                python_to_dust_type_map[type(node.condition.value)],
            )
        return False

    def check_type_exists(self, typ, node):
        global errored
        if typ in ("dynamic", "int", "float", "bool", "string", "array"):
            return "exists"
        type_exists = self.env.lookup(typ, node, fail=False)
        type_is_struct = type_exists["type"] == "struct"
        if (
            typ not in ("int", "string", "float", "bool", "array")
            and not type_is_struct
        ):
            _error(
                self.errinfomod,
                ErrorType.UndefinedSymbol,
                ErrorIDs.UndefinedSymbol,
                f"{node.line}-{node.lineEnd}:{node.col}-{node.colEnd}",
                typ,
            )

    def analyze_function_statement(self, node, define=True):
        result = self.env.define(
            node.name, "function", params=node.params, ret_result=not define
        )
        env = Env(self.errinfomod, parent=self.env)
        for i, v in node.params.items():
            self.check_type_exists(v, node)
            env.define(i, "var", const=True, data_type=v, inferred=v == "dynamic")
        Analyzer(
            node.body,
            self.filename,
            self.errinfomod,
            function=True,
            env=env,
        ).analyze()
        if define:
            return self.env.lookup(node.name, node)
        else:
            return result

    def analyze_function_call(self, node):
        temp = node.name
        structing = False
        if isinstance(node.name, DotAccess):
            struct = self.env.lookup(self.resolve_nested_dotaccess(node.name))
            name_to_lookup = struct.get("data_type")
            structdata = self.env.lookup(name_to_lookup, node.name)
            if node.name.rhs not in structdata["methods"]:
                _error(
                    self.errinfomod,
                    ErrorType.NotAStructField,
                    ErrorIDs.NotAStructField,
                    f"{node.line}-{node.lineEnd}:{node.col}-{node.colEnd}",
                    self.resolve_nested_dotaccess(node.name),
                    node.name.rhs,
                )
                return
            func = structdata["methods"][node.name.rhs][2]
            temp = node.name
            node.name = ".".join(
                [*self.resolve_nested_dotaccess_list(node.name), node.name.rhs]
            )
            structing = True
        else:
            func = self.env.lookup(node.name, node)
        if not func:
            self.adv()
            return
        erroredrn = False
        if func["type"] != "function" and not self.function:
            _error(
                self.errinfomod,
                ErrorType.NotAFunction,
                ErrorIDs.NotAFunction,
                f"{node.line}-{node.lineEnd}:{node.col}-{node.colEnd}",
                node.name,
            )
            erroredrn = True
        if not erroredrn:
            if not self.function and (
                len(node.args)
                != (len(func["params"]) if not structing else len(func["params"]) - 1)
            ):
                _error(
                    self.errinfomod,
                    ErrorType.ArgumentCountMismatch,
                    ErrorIDs.ArgumentCountMismatch,
                    f"{node.line}-{node.lineEnd}:{node.col}-{node.colEnd}",
                    node.name,
                    len(func["params"]),
                    len(node.args),
                )
        for arg in node.args:
            arg = self.handle_expression(arg)
        node.name = temp

    def analyze(self):
        global errored
        while self.cn is not None:
            match self.cn.node_type():
                case "PrintStatement":
                    for i in self.cn.values:
                        self.handle_expression(i)
                case "LetStatement":
                    value = self.handle_expression(self.cn.value)
                    typ = self.cn.type
                    exists = self.check_type_exists(typ, self.cn)
                    if exists == "exists":
                        if isinstance(value, dict) and value["type"] in (
                            "struct",
                            "initstruct",
                        ):
                            if isinstance(self.cn.value, StructInit):
                                typ = self.cn.value.name
                            self.env.define(
                                self.cn.name,
                                "initstruct",
                                const=self.cn.const,
                                data_type=typ,
                                inferred=self.cn.type == "dynamic",
                                fields=self.cn.value.fields,
                            )
                            self.adv()
                            continue
                    self.env.define(
                        self.cn.name,
                        "var",
                        const=self.cn.const,
                        data_type=typ,
                        inferred=self.cn.type == "dynamic",
                    )
                case "VariableReassignment":
                    if isinstance(self.cn.name, (GetItem, DotAccess)):
                        self.adv()
                        continue
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
                    self.env.define(self.cn.name, "var")
                case "IfStatement":
                    self.resolve_truthiness(self.cn)
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
                    self.resolve_truthiness(self.cn)
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
                case "FunctionStatement":
                    self.analyze_function_statement(self.cn)
                case "FunctionCall":
                    self.analyze_function_call(self.cn)
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
                case "ForStatement":
                    self.handle_expression(self.cn.range)
                    env = Env(self.errinfomod, self.env)
                    env.define(
                        self.cn.iterator,
                        "var",
                        True,
                        data_type="dynamic",
                        inferred=False,
                    )
                    Analyzer(
                        self.cn.body,
                        self.filename,
                        self.errinfomod,
                        env,
                        loop=True,
                        function=self.function,
                    ).analyze()
                case "StructStatement":
                    self.env.define(
                        self.cn.name,
                        "struct",
                        True,
                        fields=self.cn.fields,
                        methods={}
                    )
                case "Implementation":
                    data = self.env.lookup(self.cn.struct, self.cn, fail=False)
                    if not data:
                        self.env.lookup(self.cn.struct, self.cn)
                    if not isinstance(data, dict):
                        exit(1)
                    if data.get("type") != "struct":
                        hlp = None
                        if data.get("type") == "initstruct":
                            hlp = f"""`{self.cn.struct}`'s parent struct is `{
                                data.get("data_type")
                            }`. Maybe you meant to write an implementation for the
{data.get("data_type")} struct?"""
                        _error(
                            self.errinfomod,
                            ErrorType.NotAStruct,
                            ErrorIDs.NotAStruct,
                            f"{self.cn.line}-{self.cn.lineEnd}:{self.cn.col}-{self.cn.colEnd}",
                            self.cn.struct,
                            hlp=hlp,
                        )
                        self.adv()
                        continue
                    for method in self.cn.methods:
                        method_dict = self.analyze_function_statement(
                            method, define=False
                        )
                        method_dict = {
                            method.name: [
                                "method",
                                method,
                                method_dict,
                            ]
                        }
                        data["methods"] |= method_dict
            self.adv()
        if errored:
            _exit(self.errinfomod, 1)
