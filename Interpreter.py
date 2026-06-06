# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

import sys

from AST import (
    BinOp,
    DotAccess,
    ForStatement,
    FunctionCall,
    FunctionStatement,
    GetItem,
    IfStatement,
    LetStatement,
    Literal,
    ReturnStatement,
    StructInit,
    UnaryOp,
    VariableReassignment,
)
from Error import ErrorIDs, ErrorInfo, ErrorType, error, error_exit


class BreakInterrupt(Exception): ...


class ContinueInterrupt(Exception): ...


def _exit(error_info, code=1):
    error_exit(error_info)
    sys.exit(code)


sys.setrecursionlimit(25000)


def _error(
    error_info: ErrorInfo,
    error_type,
    error_id: ErrorIDs,
    position_info: str,
    *args,
    **kwargs,
):
    error(error_info, error_type, error_id, position_info, *args, **kwargs)
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
        if (
            (not self.inferred)
            and python_to_dust_type_map.get(type(value)) != self.type
            and self.type in ("int", "float", "bool", "string", "array")
        ):
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


class WrapperFunction:
    def __init__(
        self,
        wraps_to,
        return_type=None,
        errinfomod=None,
    ):
        self.wraps_to = wraps_to
        self.return_type = return_type
        self.errinfomod = errinfomod

    def __repr__(self):
        return f"WrapperFunction(wraps_to={repr(self.wraps_to)})"


class WrapperFunctionWraps:
    @staticmethod
    def length(obj):
        return len(obj)

    @staticmethod
    def ranges(start, stop):
        return range(start, stop)

    @staticmethod
    def contains(arr, value):
        return value in arr


class Struct:
    def __init__(
        self,
        name,
        fields,
        node=None,
        errinfomod=None,
    ):
        self.name = name
        self.fields = fields
        self.methods = {}
        self.node = node
        self.errinfomod = errinfomod

    def __repr__(self):
        return f"Struct(name={self.name}, fields={self.fields}, methods={self.methods})"


class InitializedStruct:
    def __init__(
        self,
        name,
        fields,
        node=None,
        errinfomod=None,
    ):
        self.name = name
        self.fields = fields
        self.node = node
        self.errinfomod = errinfomod

    def __repr__(self):
        fields = ", ".join(
            f"{field}: {
                f'"{repr(value)[1:-1]}"' if repr(value).startswith("'") else repr(value)
            }"
            for field, value in self.fields.items()
        )
        return f"{self.name} {{ {fields} }}"


python_to_dust_type_map = {
    str: "string",
    int: "int",
    float: "float",
    bool: "bool",
    list: "array",
    range: "array",
    InitializedStruct: "struct",
}


class Env:
    def __init__(self, errinfomod, parent=None):
        self.errinfomod = errinfomod
        self.parent: Env = parent
        wrapper_functions = {}
        self.symbols = (
            {}
            if parent
            else {
                "RECURSION_LIMIT": Variable(1000, typ="int", const=True),
                **wrapper_functions,
            }
        )
        if not parent:
            stmt = FunctionStatement(
                "push",
                {"arr": "array", "value": "dynamic"},
                [
                    ReturnStatement(
                        BinOp(
                            Literal("Ident", "arr"),
                            Literal("Array", [Literal("Ident", "value")]),
                            "+",
                        )
                    )
                ],
            )
            self.define("push", Function(stmt.params, stmt.body, stmt))
            self.define(
                "len",
                WrapperFunction(WrapperFunctionWraps.length, "int", self.errinfomod),
            )
            self.define(
                "range",
                WrapperFunction(WrapperFunctionWraps.ranges, "array", self.errinfomod),
            )
            self.define(
                "contains",
                WrapperFunction(WrapperFunctionWraps.contains, "bool", self.errinfomod),
            )
            stmt = FunctionStatement(
                "remove",
                {"arr": "array", "value": "int"},
                [
                    LetStatement("new_arr", Literal("Array", [])),
                    LetStatement("index", Literal("Int", 0)),
                    ForStatement(
                        "item",
                        Literal("Ident", "arr"),
                        [
                            IfStatement(
                                BinOp(
                                    Literal("Ident", "index"),
                                    Literal("Ident", "value"),
                                    "!=",
                                ),
                                [
                                    VariableReassignment(
                                        "new_arr",
                                        FunctionCall(
                                            "push",
                                            [
                                                Literal("Ident", "new_arr"),
                                                Literal("Ident", "item"),
                                            ],
                                        ),
                                    ),
                                ],
                                [],
                            ),
                            VariableReassignment(
                                "index",
                                BinOp(
                                    Literal("Ident", "index"), Literal("Int", 1), "+"
                                ),
                            ),
                        ],
                    ),
                    ReturnStatement(
                        Literal("Ident", "new_arr"),
                    ),
                ],
            )
            self.define("remove", Function(stmt.params, stmt.body, stmt))
            stmt = FunctionStatement(
                "insert",
                {"arr": "array", "value": "int", "val": "dynamic"},
                [
                    LetStatement("new_arr", Literal("Array", [])),
                    LetStatement("index", Literal("Int", 0)),
                    ForStatement(
                        "item",
                        Literal("Ident", "arr"),
                        [
                            IfStatement(
                                BinOp(
                                    Literal("Ident", "index"),
                                    Literal("Ident", "value"),
                                    "!=",
                                ),
                                [
                                    VariableReassignment(
                                        "new_arr",
                                        FunctionCall(
                                            "push",
                                            [
                                                Literal("Ident", "new_arr"),
                                                Literal("Ident", "item"),
                                            ],
                                        ),
                                    ),
                                ],
                                [
                                    VariableReassignment(
                                        "new_arr",
                                        FunctionCall(
                                            "push",
                                            [
                                                Literal("Ident", "new_arr"),
                                                Literal("Ident", "val"),
                                            ],
                                        ),
                                    ),
                                    VariableReassignment(
                                        "new_arr",
                                        FunctionCall(
                                            "push",
                                            [
                                                Literal("Ident", "new_arr"),
                                                Literal("Ident", "item"),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                            VariableReassignment(
                                "index",
                                BinOp(
                                    Literal("Ident", "index"), Literal("Int", 1), "+"
                                ),
                            ),
                        ],
                    ),
                    ReturnStatement(
                        Literal("Ident", "new_arr"),
                    ),
                ],
            )
            self.define("insert", Function(stmt.params, stmt.body, stmt))

    def define(self, name, value, redefining=False):
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
            if not hasattr(self.symbols[name], "value"):
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
        self.FUNCTION_HANDLERS = {"pop": self.handle_pop_statement}
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
            return self.env.lookup(value.value, auto_resolve=True, node=value)
        else:
            return value.value

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

    def handle_expression(
        self, expr: BinOp | UnaryOp | Literal | StructInit | DotAccess
    ):
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
        elif expr.node_type() == "GetItem":
            arr = self.env.lookup(expr.name, auto_resolve=True, node=expr)
            index = self.handle_expression(expr.index)
            if index > len(arr):
                _error(
                    self.errinfomod,
                    ErrorType.IndexErr,
                    ErrorIDs.IndexErr,
                    f"{expr.line}-{expr.lineEnd}:{expr.col}-{expr.colEnd}",
                    index,
                )
            return arr[index]
        elif expr.node_type() == "DotAccess":
            if isinstance(expr.lhs, DotAccess):
                data = self.handle_expression(expr.lhs)
            else:
                data = self.env.lookup(expr.lhs)
            return data.fields[expr.rhs]
        elif expr.node_type() == "StructInit":
            initialized_struct = InitializedStruct(
                expr.name,
                {
                    field: self.handle_expression(value)
                    for field, value in expr.fields.items()
                },
                expr,
                self.errinfomod,
            )
            return initialized_struct
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

    def handle_print_statement(self, node, return_repr=False):
        values = []
        for i in node.values:
            val = self.handle_expression(i)
            if isinstance(val, bool):
                val = "true" if (val and isinstance(val, bool)) else "false"
            elif isinstance(val, list):
                for i, v in enumerate(val):
                    if repr(v).startswith("'"):
                        val[i] = f'"{v}"'
                val = f"[{', '.join(str(v) for v in val)}]"
            values.append(str(val))
        if return_repr:
            return " ".join(values)
        print(" ".join(values))

    def handle_let_statement(self, node):
        value = self.handle_expression(node.value)
        if isinstance(value, (Function, WrapperFunction)):
            self.env.define(
                node.name,
                value,
            )
            return
        self.env.define(
            node.name,
            Variable(
                value,
                typ=node.type,
                const=node.const,
                node=node,
                errinfomod=self.errinfomod,
            ),
        )

    def get_dotaccess_first(self, node: DotAccess):
        if not isinstance(node, DotAccess):
            return node
        elif not isinstance(node.lhs, DotAccess):
            return node.lhs
        return self.get_dotaccess_first(node.lhs)

    def handle_reassignment(self, node):
        if isinstance(node.name, GetItem):
            arr = self.env.lookup(node.name.name, node=node)
            index = self.handle_expression(node.name.index)
            arr[index] = self.handle_expression(node.value)
            self.env.define(node.name.name, Variable(arr), redefining=True)
        elif isinstance(node.name, DotAccess):
            field = node.name.rhs
            name = self.get_dotaccess_first(node.name)
            data = self.env.lookup(name)
            data.fields[field] = self.handle_expression(node.value)
        else:
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

    def handle_function_statement(self, node, no_define=False):
        if no_define:
            return Function(
                node.params, node.body, node, node.return_type, self.errinfomod
            )
        self.env.define(
            node.name,
            Function(node.params, node.body, node, node.return_type, self.errinfomod),
        )

    def handle_function_call(self, node: FunctionCall):
        if node.name in self.FUNCTION_HANDLERS:
            return self.FUNCTION_HANDLERS[node.name](node)
        if isinstance(node.name, DotAccess):
            struct = self.env.lookup(self.get_dotaccess_first(node.name), node)
            structdata = self.env.lookup(struct.name)
            node.args.insert(0, struct)
            func = structdata.methods[node.name.rhs]
        else:
            func = self.env.lookup(node.name, node=node, auto_resolve=False)
        if isinstance(func, WrapperFunction):
            arguments = [self.handle_expression(value) for value in node.args]
            return func.wraps_to(*arguments)
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
            if i == 0 and v == "self":
                resolved = node.args[i]
            else:
                resolved = self.handle_expression(node.args[i])
            arguments[v] = resolved
        env = Env(self.errinfomod, self.env)
        for idx, (i, v) in enumerate(arguments.items()):
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
        result = Interpreter(
            func.body, self.filename, self.errinfomod, env=env
        ).interpret()
        if result is not None:
            return result

    def handle_for_statement(self, node: ForStatement):
        rng = self.handle_expression(node.range)
        for i in rng:
            scope = Env(self.errinfomod, self.env)
            scope.define(node.iterator, i)
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

    def handle_pop_statement(self, node: FunctionCall):
        # never thought i'd be making a separate
        # method for a function that should be
        # defined in Env() if it wasn't for my
        # decision to make func params immutable
        arr = self.handle_expression(node.args[0])
        val = arr.pop()
        if isinstance(node.args[0], Literal) and node.args[0].type == "Ident":
            self.env.define(node.args[0].value, arr, redefining=True)
        return val

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
                self.handle_function_call(node)
                stack_frame -= 1
            case "ReturnStatement":
                return self.handle_expression(node.value)
            case "ForStatement":
                res = self.handle_for_statement(node)
                if res is not None:
                    return res
            case "StructStatement":
                self.env.define(
                    node.name,
                    Struct(
                        node.name,
                        node.fields,
                        node,
                        self.errinfomod,
                    ),
                )
            case "Implementation":
                struct: Struct = self.env.lookup(node.struct)
                for method in self.cn.methods:
                    func = self.handle_function_statement(method, no_define=True)
                    struct.methods[method.name] = func

    def interpret(self):
        if stack_frame >= self.env.lookup("RECURSION_LIMIT"):
            _error(
                self.errinfomod,
                ErrorType.RecursionDepthError,
                ErrorIDs.RecursionDepthError,
                f"{self.cn.line}-{self.cn.lineEnd}:{self.cn.col}-{self.cn.colEnd}",
                self.env.lookup("RECURSION_LIMIT"),
            )
        while self.cn is not None:
            res = self.parse_node(self.cn)
            if res is not None:
                return res
            self.adv()
