# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

import sys

from AST import BinOp, FunctionStatement, Literal, UnaryOp
from Error import ErrorIDs, ErrorInfo, ErrorType, error, error_exit


class BreakInterrupt(Exception): ...


class ContinueInterrupt(Exception): ...


python_to_dust_type_map = {str: "string", int: "int", float: "float", bool: "bool"}


def _exit(error_info, code=1):
    error_exit(error_info)
    sys.exit(code)


sys.setrecursionlimit(25000)


def _error(
    error_info: ErrorInfo, error_type, error_id: ErrorIDs, position_info: str, *args
):
    error(error_info, error_type, error_id, position_info, *args)
    _exit(error_info, 1)

stack_frame = 0


class Variable:
    def __init__(
        self,
        value,
        typ="dynamic",
        node: BinOp = None,
        const=False,
        errinfomod=None,
    ):
        self.node = node
        self.type = typ if typ != "dynamic" else python_to_dust_type_map[type(value)]
        self.inferred = typ == "dynamic"
        self.value = value
        self.const = const
        if (not self.inferred) and python_to_dust_type_map[type(value)] != self.type:
            _error(
                errinfomod,
                ErrorType.AssignmentTypeMismatch,
                ErrorIDs.AssignmentTypeMismatch,
                f"{node.line}-{node.lineEnd}:{node.col}-{node.colEnd}",
                self.type,
                python_to_dust_type_map[type(value)],
            )

    def __repr__(self):
        return f"Variable(value={self.value}, type={self.type}, const={self.const})"


class Function:
    def __init__(
        self,
        params,
        body,
        node: FunctionStatement = None,
        return_type=None,
        errinfomod=None,
    ):
        self.params = params
        self.body = body
        self.node = node
        self.return_type = return_type
        self.errinfomod = errinfomod

    def __repr__(self):
        return f"Function(params={self.params}, body={self.body})"


class Env:
    def __init__(self, errinfomod, parent=None):
        self.symbols = {} if parent else {"RECURSION_LIMIT": Variable(1000, typ="int")}
        self.errinfomod = errinfomod
        self.parent: Env = parent

    def define(self, name, value, redefining=False):
        if redefining and name == "RECURSION_LIMIT":
            sys.setrecursionlimit(value.value * 25)
        if redefining:
            if self.parent and self.parent.lookup(
                name, auto_resolve=False, error_on_fail_lookup=False
            ):
                self.parent.define(name, value, redefining=True)
            else:
                self.symbols[name] = value
        elif not redefining and name not in self.symbols:
            self.symbols[name] = value
        elif (
            not redefining
            and name in self.symbols
            or (
                self.parent
                and self.parent.lookup(
                    name, auto_resolve=False, error_on_fail_lookup=False
                )
            )
        ):
            _error(
                self.errinfomod,
                ErrorType.AlreadyDefinedSymbol,
                ErrorIDs.AlreadyDefinedSymbol,
                f"{value.node.line}-{value.node.lineEnd}:{value.node.col}-{value.node.colEnd}",
                name,
            )

    def lookup(self, name, auto_resolve=True, error_on_fail_lookup=True, node=None):
        if name not in self.symbols:
            if self.parent:
                lookedup = self.parent.lookup(
                    name,
                    auto_resolve=auto_resolve,
                    error_on_fail_lookup=error_on_fail_lookup,
                    node=node,
                )
                if lookedup is not None:
                    if not auto_resolve or not hasattr(lookedup, "value"):
                        return lookedup
                    return lookedup.value
                elif error_on_fail_lookup:
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
            elif error_on_fail_lookup:
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
        else:
            if not auto_resolve:
                return self.symbols[name]
            return self.symbols[name].value

    def __repr__(self):
        return f"Env(symbols={self.symbols}, parent={self.parent})"


class Interpreter:
    def __init__(
        self, ast, filename="<stdin>", error_info_module=None, env=None, loop=False
    ):
        self.ast = ast
        self.filename = filename
        self.inputting = False  # for keyboard interrupt debug
        self.errinfomod = error_info_module
        self.env = env if env is not None else Env(self.errinfomod)
        self.loop = loop
        self.EXPR_NODE_TYPES = {
            "InputStatement": self.handle_input_statement,
            "FunctionCall": self.handle_function_call,
        }
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
            else self.env.lookup(value.value, auto_resolve=True, node=value)
        )

    def resolve_truthiness(self, value, line=None, lineEnd=None, col=None, colEnd=None):
        if not isinstance(value, bool):
            _error(
                self.errinfomod,
                ErrorType.ConditionalTypeMismatch,
                ErrorIDs.ConditionalTypeMismatch,
                f"{line}-{lineEnd}:{col}-{colEnd}",
                python_to_dust_type_map[type(value)],
            )

    def handle_type_cast(self, value, cast_type, node=None):
        try:
            if cast_type == "int":
                return int(value)
            elif cast_type == "float":
                return float(value)
            elif cast_type == "string":
                return str(value)
            elif cast_type == "bool":
                return (
                    True
                    if value == "true" or (value and isinstance(value, bool))
                    else False
                )
        except ValueError:
            _error(
                self.errinfomod,
                ErrorType.TypeCastError,
                ErrorIDs.TypeCastError,
                f"{node.line}-{node.lineEnd}:{node.col}-{node.colEnd}",
                value,
                cast_type,
            )
        return value

    def handle_expression(self, expr: BinOp | UnaryOp | Literal):
        if expr.node_type() == "Literal":
            return self.resolve_literal(expr)
        elif expr.node_type() == "UnaryOp":
            rhs = self.handle_expression(expr.rhs)
            return (
                not rhs
                if expr.op == "!"
                else (
                    -rhs
                    if expr.op == "-"
                    else self.handle_type_cast(rhs, expr.op[10:], expr)
                )
            )
        elif expr.node_type() in self.EXPR_NODE_TYPES:
            return self.EXPR_NODE_TYPES[expr.node_type()](expr)
        lhs = self.handle_expression(expr.lhs)
        rhs = self.handle_expression(expr.rhs)
        if isinstance(lhs, str) or isinstance(rhs, str):
            if (
                isinstance(lhs, (int, float, bool))
                or isinstance(rhs, (int, float, bool))
            ) and expr.op in ("+", "-", "*", "/", "%", "<", ">", "<=", ">="):
                _error(
                    self.errinfomod,
                    ErrorType.OperatorTypeMismatch,
                    ErrorIDs.OperatorTypeMismatch,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    expr.op,
                    python_to_dust_type_map[type(lhs)],
                    python_to_dust_type_map[type(rhs)],
                )
        if expr.op == "+":
            return lhs + rhs
        elif expr.op == "-":
            return lhs - rhs
        elif expr.op == "*":
            return lhs * rhs
        elif expr.op == "/":
            if rhs == 0:
                _error(
                    self.errinfomod,
                    ErrorType.ZeroDivision,
                    ErrorIDs.ZeroDivision,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    False,
                )
                _exit(self.errinfomod, 1)
            return lhs / rhs
        elif expr.op == "\\":
            if rhs == 0:
                _error(
                    self.errinfomod,
                    ErrorType.ZeroDivision,
                    ErrorIDs.ZeroDivision,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    False,
                )
                _exit(self.errinfomod, 1)
            return lhs // rhs
        elif expr.op == "%":
            if rhs == 0:
                _error(
                    self.errinfomod,
                    ErrorType.ZeroDivision,
                    ErrorIDs.ZeroDivision,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    False,
                )
                _exit(self.errinfomod, 1)
            return lhs % rhs
        elif expr.op == "==":
            return lhs == rhs
        elif expr.op == "!=":
            return lhs != rhs
        elif expr.op == "<":
            return lhs < rhs
        elif expr.op == ">":
            return lhs > rhs
        elif expr.op == "<=":
            return lhs <= rhs
        elif expr.op == ">=":
            return lhs >= rhs
        elif expr.op == "&&":
            if not lhs:
                return False
            return lhs and rhs
        elif expr.op == "||":
            if lhs:
                return True
            return lhs or rhs

    def handle_print_statement(self, node):
        values = []
        for i in node.values:
            val = self.handle_expression(i)
            if isinstance(val, bool):
                val = "true" if (val and isinstance(val, bool)) else "false"
            values.append(str(val))
        print(" ".join(values))

    def handle_let_statement(self, node):
        self.env.define(
            node.name,
            Variable(
                self.handle_expression(node.value),
                typ=node.type,
                const=node.const,
                node=node,
                errinfomod=self.errinfomod,
            ),
        )

    def handle_reassignment(self, node):
        self.env.define(
            node.name,
            Variable(
                self.handle_expression(node.value),
                typ=self.env.lookup(
                    node.name, auto_resolve=False, node=node.value
                ).type,
                node=node,
                errinfomod=self.errinfomod,
            ),
            redefining=True,
        )

    def handle_if_statement(self, node):
        condition = self.handle_expression(node.condition)
        self.resolve_truthiness(
            condition,
            node.condition.line,
            node.condition.lineEnd,
            node.condition.col,
            node.condition.colEnd,
        )
        if condition:
            result = Interpreter(
                node.true_body,
                self.filename,
                self.errinfomod,
                env=Env(self.errinfomod, self.env),
            ).interpret()
        else:
            result = Interpreter(
                node.false_body,
                self.filename,
                self.errinfomod,
                env=Env(self.errinfomod, self.env),
            ).interpret()
        if result is not None:
            return result

    def handle_while_statement(self, node):
        condition = self.handle_expression(node.condition)
        self.resolve_truthiness(
            condition,
            node.condition.line,
            node.condition.lineEnd,
            node.condition.col,
            node.condition.colEnd,
        )
        while condition:
            scope = Env(self.errinfomod, self.env)
            interp = Interpreter(
                node.body,
                self.filename,
                self.errinfomod,
                env=scope,
                loop=True,
            )
            try:
                result = interp.interpret()
            except BreakInterrupt:
                break
            except ContinueInterrupt:
                continue
            if result is not None:
                return result
            condition = interp.handle_expression(node.condition)
            interp.resolve_truthiness(
                condition,
                node.condition.line,
                node.condition.lineEnd,
                node.condition.col,
                node.condition.colEnd,
            )

    def handle_input_statement(self, node):
        self.inputting = True
        prompt = self.handle_expression(node.prompt)
        value = input(prompt)
        self.inputting = False
        return value

    def handle_function_statement(self, node):
        self.env.define(
            node.name,
            Function(node.params, node.body, node, node.return_type, self.errinfomod),
        )

    def handle_function_call(self, node):
        func = self.env.lookup(node.name, node=node, auto_resolve=False)
        if not isinstance(func, Function):
            _error(
                self.errinfomod,
                ErrorType.NotAFunction,
                ErrorIDs.NotAFunction,
                f"{node.line}-{node.lineEnd}:{node.col}-{node.colEnd}",
                node.name,
            )
        arguments = {}
        for i, v in enumerate(func.params):
            resolved = self.handle_expression(node.args[i])
            arguments[v] = resolved
        env = Env(self.errinfomod, self.env)
        idx = 0
        for i, v in arguments.items():
            env.define(
                i,
                Variable(
                    value=v,
                    node=node.args[idx],
                    const=True,
                    typ=func.params[i],
                    errinfomod=self.errinfomod,
                ),
            )
            idx += 1
        result = Interpreter(
            func.body, self.filename, self.errinfomod, env=env
        ).interpret()
        if result is not None:
            return result

    def parse_node(self, node):
        global stack_frame
        match node.node_type():
            case "PrintStatement":
                self.handle_print_statement(node)
            case "LetStatement":
                self.handle_let_statement(node)
            case "VariableReassignment":
                self.handle_reassignment(node)
            case "IfStatement":
                res = self.handle_if_statement(node)
                if res is not None:
                    return res
            case "WhileStatement":
                res = self.handle_while_statement(node)
                if res is not None:
                    return res
            case "BreakStatement":
                raise BreakInterrupt()
            case "ContinueStatement":
                raise ContinueInterrupt()
            case "InputStatement":
                self.handle_input_statement(node)
            case "FunctionStatement":
                self.handle_function_statement(node)
            case "FunctionCall":
                stack_frame += 1
                res = self.handle_function_call(node)
                stack_frame -= 1
                if res is not None:
                    return res
            case "ReturnStatement":
                return self.handle_expression(node.value)

    def interpret(self):
        if stack_frame >= self.env.lookup("RECURSION_LIMIT"):
            _error(
                self.errinfomod,
                ErrorType.RecursionDepthError,
                ErrorIDs.RecursionDepthError,
                f"{self.cn.line}-{self.cn.lineEnd}:{self.cn.col}-{self.cn.colEnd}",
                self.env.lookup("RECURSION_LIMIT")
            )
        while self.cn is not None:
            res = self.parse_node(self.cn)
            if res is not None:
                return res
            self.adv()
