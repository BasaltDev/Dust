# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only


class Literal:
    def __init__(self, typ, value, line=None, lineEnd=None, col=None, colEnd=None):
        self.type = typ
        self.value = value
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "Literal"

    def __repr__(self):
        return f"Literal(type={self.type}, value={repr(self.value)})"


class BinOp:
    def __init__(self, lhs, rhs, op, line=None, lineEnd=None, col=None, colEnd=None):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "BinOp"

    def __repr__(self):
        return f"BinOp(lhs={self.lhs}, rhs={self.rhs}, op='{self.op}')"


class UnaryOp:
    def __init__(self, rhs, op, line=None, lineEnd=None, col=None, colEnd=None):
        self.rhs = rhs
        self.op = op
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "UnaryOp"

    def __repr__(self):
        return f"UnaryOp(rhs={self.rhs}, op='{self.op}')"


class PrintStatement:
    def __init__(self, values, line=None, lineEnd=None, col=None, colEnd=None):
        self.values = values
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "PrintStatement"

    def __repr__(self):
        return f"PrintStatement({self.values})"


class LetStatement:
    def __init__(
        self,
        name,
        value,
        typ="dynamic",
        const=False,
        line=None,
        lineEnd=None,
        col=None,
        colEnd=None,
    ):
        self.name = name
        self.value = value
        self.type = typ
        self.const = const
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "LetStatement"

    def __repr__(self):
        return f"LetStatement(name={self.name}, value={self.value}, type={self.type})"


class VariableReassignment:
    def __init__(self, name, value, line=None, lineEnd=None, col=None, colEnd=None):
        self.name = name
        self.value = value
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "VariableReassignment"

    def __repr__(self):
        return f"VariableReassignment(name={self.name}, value={self.value})"


class IfStatement:
    def __init__(
        self,
        condition,
        true_body,
        false_body,
        line=None,
        lineEnd=None,
        col=None,
        colEnd=None,
    ):
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "IfStatement"

    def __repr__(self):
        return f"IfStatement(condition={self.condition}, \
true={self.true_body}, false={self.false_body})"


class WhileStatement:
    def __init__(
        self,
        condition,
        body,
        line=None,
        lineEnd=None,
        col=None,
        colEnd=None,
    ):
        self.condition = condition
        self.body = body
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "WhileStatement"

    def __repr__(self):
        return f"WhileStatement(condition={self.condition}, body={self.body})"


class BreakStatement:
    def __init__(self, line=None, lineEnd=None, col=None, colEnd=None):
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "BreakStatement"

    def __repr__(self):
        return self.node_type()


class ContinueStatement:
    def __init__(self, line=None, lineEnd=None, col=None, colEnd=None):
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "ContinueStatement"

    def __repr__(self):
        return self.node_type()


class InputStatement:
    def __init__(self, prompt, line=None, lineEnd=None, col=None, colEnd=None):
        self.prompt = prompt
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "InputStatement"

    def __repr__(self):
        return f"InputStatement(prompt={self.prompts})"


class FunctionStatement:
    def __init__(
        self,
        name,
        params,
        body,
        return_type=None,
        line=None,
        lineEnd=None,
        col=None,
        colEnd=None,
    ):
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "FunctionStatement"

    def __repr__(self):
        return f"FunctionStatement(name={self.name}, params={self.params},\
body={self.body}, return_type={self.return_type})"


class FunctionCall:
    def __init__(self, name, args, line=None, lineEnd=None, col=None, colEnd=None):
        self.name = name
        self.args = args
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "FunctionCall"

    def __repr__(self):
        return f"FunctionCall(name={self.name}, args={self.args})"


class ReturnStatement:
    def __init__(self, value, line=None, lineEnd=None, col=None, colEnd=None):
        self.value = value
        self.line = line
        self.lineEnd = lineEnd
        self.col = col
        self.colEnd = colEnd

    def node_type(self):
        return "ReturnStatement"

    def __repr__(self):
        return f"ReturnStatement(value={self.value})"
