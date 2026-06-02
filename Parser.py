# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

import sys

from AST import (
    BinOp,
    BreakStatement,
    ContinueStatement,
    ForStatement,
    FunctionCall,
    FunctionStatement,
    GetItem,
    IfStatement,
    InputStatement,
    LetStatement,
    Literal,
    PrintStatement,
    ReturnStatement,
    UnaryOp,
    VariableReassignment,
    WhileStatement,
)
from Error import ErrorIDs, ErrorType, error, error_exit
from Token import Token, TokenType


def _exit(error_info, code=1):
    error_exit(error_info)
    sys.exit(code)


class Parser:
    def __init__(self, tokens, filename="<stdin>", error_info_module=None):
        self.tokens = tokens
        self.filename = filename
        self.errinfomod = error_info_module
        self.pos = -1
        self.ct: Token = None
        self.ast = []
        self.errored = False
        self.KEYWORD_HANDLERS = {
            "print": self.parse_print_statement,
            "let": self.parse_let_statement,
            "const": lambda: self.parse_let_statement(True),
            "if": self.parse_if_statement,
            "while": self.parse_while_statement,
            "break": self.parse_break_statement,
            "continue": self.parse_continue_statement,
            "input": self.parse_input_statement,
            "func": self.parse_function,
            "return": self.parse_return_statement,
            "for": self.parse_for_statement,
        }
        self.EXPR_KEYWORDS = {"input": lambda: self.parse_input_statement(expr=True)}
        self.adv()

    def __repr__(self):
        return f"Parser(filename={self.filename})"

    def adv(self, amt=1):
        self.pos += amt
        self.ct = None if self.pos >= len(self.tokens) else self.tokens[self.pos]

    def peek(self, amt=1):
        return (
            None
            if (self.pos + amt >= len(self.tokens) or self.pos + amt < 0)
            else self.tokens[self.pos + amt]
        )

    def expect_token(self, token):
        if not self.ct or self.ct != token:
            pos_info = ""
            if not self.ct:
                self.adv(-1)
                pos_info = f"{self.ct.line}:{self.ct.colEnd}-{self.ct.colEnd + 1}"
                self.adv()
            else:
                pos_info = f"{self.ct.line}:{self.ct.col}-{self.ct.colEnd}"
            error(
                self.errinfomod,
                ErrorType.TokenExpected,
                ErrorIDs.TokenExpected,
                pos_info,
                token,
                self.ct,
            )
            self.errored = True
            if self.ct:
                self.adv(-1)
            return False
        return True

    def literalify(self, token: Token):
        typ = "???"
        value = token.value
        match token.type:
            case TokenType.IDENTIFIER:
                typ = "Ident"
            case TokenType.INTEGER:
                typ = "Int"
            case TokenType.FLOAT:
                typ = "Float"
            case TokenType.STRING:
                typ = "String"
            case TokenType.BOOLEAN:
                typ = "Bool"
            case TokenType.LEFTBRACKET:
                self.adv()
                typ = "Array"
                value = []
                while self.ct and self.ct != TokenType.RIGHTBRACKET:
                    value.append(
                        self.parse_expression(
                            ending=TokenType.RIGHTBRACKET, altEnding=TokenType.COMMA
                        )
                    )
                    if self.ct == TokenType.RIGHTBRACKET:
                        break
                    self.adv()
        return Literal(typ, value, token.line, token.line, token.col, token.colEnd)

    def parse_expression(self, ending=TokenType.SEMICOLON, altEnding=None):
        OPERATOR_MAP = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-",
            TokenType.STAR: "*",
            TokenType.SLASH: "/",
            TokenType.MOD: "%",
            TokenType.EQUALS: "==",
            TokenType.NOTEQUALS: "!=",
            TokenType.LESSTHAN: "<",
            TokenType.GREATERTHAN: ">",
            TokenType.LESSTHANOREQUAL: "<=",
            TokenType.GREATERTHANOREQUAL: ">=",
            TokenType.AND: "&&",
            TokenType.OR: "||",
            TokenType.NOT: "!",
        }
        operators = []
        operator_tokens = []
        operands = []
        last_item = None
        while self.ct is not None and self.ct not in (ending, altEnding):
            if self.ct == TokenType.LEFTPAREN:
                self.adv()
                value = self.parse_expression(ending=TokenType.RIGHTPAREN)
                value.col -= 1
                operands.append(value)
                last_item = value
            elif (
                self.ct == TokenType.KEYWORD
                and self.ct.value in self.EXPR_KEYWORDS
                and self.peek() == TokenType.LEFTPAREN
            ):
                value = self.EXPR_KEYWORDS[self.ct.value]()
                operands.append(value)
                last_item = value
            elif self.ct == TokenType.MINUS and (
                last_item
                in (
                    "+",
                    "-",
                    "*",
                    "/",
                    "%",
                    "==",
                    "!=",
                    "<",
                    ">",
                    "<=",
                    ">=",
                    "&&",
                    "||",
                    "!",
                )
                or last_item is None
            ):
                operators.append("--")
                operator_tokens.append(self.ct)
                last_item = "--"
            elif self.ct == TokenType.LESSTHAN and self.peek() == TokenType.DATA_TYPE:
                self.adv()
                operators.append(f"<{self.parse_data_type()}>")
                operator_tokens.append(self.peek(-1))
                self.adv()
            elif self.ct == TokenType.IDENTIFIER and self.peek() == TokenType.LEFTPAREN:
                value = self.parse_function_call(expr=True)
                operands.append(value)
                last_item = value
            elif (
                self.ct == TokenType.IDENTIFIER and self.peek() == TokenType.LEFTBRACKET
            ):
                name = self.ct.value
                self.adv(2)
                value = GetItem(
                    name, self.parse_expression(ending=TokenType.RIGHTBRACKET)
                )
                operands.append(value)
                last_item = value
            elif self.ct in (
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.STAR,
                TokenType.SLASH,
                TokenType.MOD,
                TokenType.EQUALS,
                TokenType.NOTEQUALS,
                TokenType.LESSTHAN,
                TokenType.GREATERTHAN,
                TokenType.LESSTHANOREQUAL,
                TokenType.GREATERTHANOREQUAL,
                TokenType.AND,
                TokenType.OR,
                TokenType.NOT,
            ):
                op = OPERATOR_MAP[self.ct.type]
                operators.append(op)
                operator_tokens.append(self.ct)
                last_item = op
            else:
                value = self.literalify(self.ct)
                operands.append(value)
                last_item = value
            self.adv()
        if self.ct not in (ending, altEnding):
            self.expect_token(altEnding if altEnding else ending)
            return
        while any(
            (i in ("--", "!") or (i.startswith("<") and i.endswith(">")))
            for i in operators
        ):
            for idx, op in enumerate(operators):
                if op in ("--", "!") or (op.startswith("<") and op.endswith(">")):
                    operand = operands[idx]
                    operands[idx] = UnaryOp(
                        operand,
                        (
                            "-"
                            if op == "--"
                            else "!"
                            if op == "!"
                            else f"type_cast {op[1:-1]}"
                        ),
                        operator_tokens[idx].line,
                        operand.lineEnd,
                        operator_tokens[idx].col,
                        operand.colEnd,
                    )
                    del operators[idx]
                    del operator_tokens[idx]
                    break
        while any(i in ("*", "/", "%") for i in operators):
            for idx, op in enumerate(operators):
                if op in ("*", "/", "%"):
                    op1 = operands[idx]
                    op2 = operands[idx + 1]
                    operands[idx] = BinOp(
                        op1, op2, op, op1.line, op2.lineEnd, op1.col, op2.colEnd
                    )
                    del operands[idx + 1]
                    del operators[idx]
                    del operator_tokens[idx]
                    break
        while any(i in ("+", "-") for i in operators):
            for idx, op in enumerate(operators):
                if op in ("+", "-"):
                    op1 = operands[idx]
                    op2 = operands[idx + 1]
                    operands[idx] = BinOp(
                        op1, op2, op, op1.line, op2.lineEnd, op1.col, op2.colEnd
                    )
                    del operands[idx + 1]
                    del operators[idx]
                    del operator_tokens[idx]
                    break
        while any(i in ("==", "!=") for i in operators):
            for idx, op in enumerate(operators):
                if op in ("==", "!="):
                    op1 = operands[idx]
                    op2 = operands[idx + 1]
                    operands[idx] = BinOp(
                        op1, op2, op, op1.line, op2.lineEnd, op1.col, op2.colEnd
                    )
                    del operands[idx + 1]
                    del operators[idx]
                    del operator_tokens[idx]
                    break
        while any(i in ("<", ">", "<=", ">=") for i in operators):
            for idx, op in enumerate(operators):
                if op in ("<", ">", "<=", ">="):
                    op1 = operands[idx]
                    op2 = operands[idx + 1]
                    operands[idx] = BinOp(
                        op1, op2, op, op1.line, op2.lineEnd, op1.col, op2.colEnd
                    )
                    del operands[idx + 1]
                    del operators[idx]
                    del operator_tokens[idx]
                    break
        while "&&" in operators:
            idx = 0
            for idx, op in enumerate(operators):
                if op == "&&":
                    op1 = operands[idx]
                    op2 = operands[idx + 1]
                    operands[idx] = BinOp(
                        op1, op2, op, op1.line, op2.lineEnd, op1.col, op2.colEnd
                    )
                    del operands[idx + 1]
                    del operators[idx]
                    del operator_tokens[idx]
                    break
        while "||" in operators:
            idx = 0
            for idx, op in enumerate(operators):
                if op == "||":
                    op1 = operands[idx]
                    op2 = operands[idx + 1]
                    operands[idx] = BinOp(
                        op1, op2, op, op1.line, op2.lineEnd, op1.col, op2.colEnd
                    )
                    del operands[idx + 1]
                    del operators[idx]
                    del operator_tokens[idx]
                    break
        return operands[0]

    def parse_print_statement(self):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        if not self.expect_token(TokenType.LEFTPAREN):
            return
        self.adv()
        in_parentheses = True
        values = []
        while self.ct and in_parentheses:
            values.append(
                self.parse_expression(
                    ending=TokenType.RIGHTPAREN, altEnding=TokenType.COMMA
                )
            )
            if self.ct == TokenType.RIGHTPAREN:
                in_parentheses = False
            self.adv()
        if not self.expect_token(TokenType.SEMICOLON):
            return
        colEnd = self.ct.colEnd
        lineEnd = self.ct.line
        return PrintStatement(values, line, lineEnd, col, colEnd)

    def parse_data_type(self):
        if self.ct == TokenType.DATA_TYPE:
            return self.ct.value
        error(
            self.errinfomod,
            ErrorType.NotAType,
            ErrorIDs.NotAType,
            f"{self.ct.line}:{self.ct.col}-{self.ct.colEnd}",
            self.ct.value,
        )
        self.errored = True

    def parse_let_statement(self, const=False):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        if not self.expect_token(TokenType.IDENTIFIER):
            return
        name = self.ct.value
        self.adv()
        typ = "dynamic"
        if self.ct and self.ct.type == TokenType.COLON:
            self.adv()
            typ = self.parse_data_type()
            self.adv()
        if not self.expect_token(TokenType.ASSIGN):
            return
        self.adv()
        value = self.parse_expression()
        if not self.expect_token(TokenType.SEMICOLON):
            return
        colEnd = self.ct.colEnd
        lineEnd = self.ct.line
        return LetStatement(
            name,
            value,
            line=line,
            lineEnd=lineEnd,
            col=col,
            colEnd=colEnd,
            typ=typ,
            const=const,
        )

    def parse_reassignment(self, name_token):
        line = self.ct.line
        col = self.ct.col
        self.adv(2)
        value = self.parse_expression()
        if not self.expect_token(TokenType.SEMICOLON):
            return
        colEnd = self.ct.colEnd
        lineEnd = self.ct.line
        return VariableReassignment(
            name_token if not isinstance(name_token, Token) else name_token.value,
            value,
            line,
            lineEnd,
            col,
            colEnd,
        )

    def parse_block_statement(self):
        self.adv()
        pos = self.pos
        block = 1
        while self.ct and block:
            if self.ct == TokenType.LEFTBRACE:
                block += 1
            elif self.ct == TokenType.RIGHTBRACE:
                block -= 1
            self.adv()
        self.adv(-1)
        if not self.expect_token(TokenType.RIGHTBRACE):
            return
        tokens = self.tokens[pos : self.pos]
        parser = Parser(tokens, self.filename, self.errinfomod)
        ast = parser.parse()
        return ast

    def parse_if_statement(self):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        condition = self.parse_expression(ending=TokenType.LEFTBRACE)
        true_body = self.parse_block_statement()
        false_body = []
        if self.peek() == Token(TokenType.KEYWORD, "else"):
            self.adv(2)
            if self.ct == Token(TokenType.KEYWORD, "if"):
                false_body = [self.parse_if_statement()]
            else:
                false_body = self.parse_block_statement()
                if not self.expect_token(TokenType.RIGHTBRACE):
                    return
        elif not self.expect_token(TokenType.RIGHTBRACE):
            return
        lineEnd = self.ct.line
        colEnd = self.ct.colEnd
        return IfStatement(condition, true_body, false_body, line, lineEnd, col, colEnd)

    def parse_while_statement(self):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        condition = self.parse_expression(ending=TokenType.LEFTBRACE)
        body = self.parse_block_statement()
        if not self.expect_token(TokenType.RIGHTBRACE):
            return
        lineEnd = self.ct.line
        colEnd = self.ct.colEnd
        return WhileStatement(condition, body, line, lineEnd, col, colEnd)

    def parse_compound_assignment(self, name_token, operator):
        line = self.ct.line
        col = self.ct.col
        self.adv(2)
        value = self.parse_expression()
        if not self.expect_token(TokenType.SEMICOLON):
            return
        colEnd = self.ct.colEnd
        lineEnd = self.ct.line
        expr = BinOp(
            name_token
            if not isinstance(name_token, Token)
            else self.literalify(name_token),
            value,
            operator[0],
            line,
            lineEnd,
            col,
            colEnd,
        )
        return VariableReassignment(
            name_token if not isinstance(name_token, Token) else name_token.value,
            expr,
            line,
            lineEnd,
            col,
            colEnd,
        )

    def parse_incrementation_decrementation(self, name_token, typ, expr=False):
        line = self.ct.line
        col = self.ct.col
        name = self.ct.value
        self.adv(2)
        if (not expr) and not self.expect_token(TokenType.SEMICOLON):
            return
        colEnd = self.ct.colEnd
        lineEnd = self.ct.line
        expr = BinOp(
            self.literalify(name_token),
            Literal("Int", 1),
            "+" if typ == TokenType.INCREMENT else "-",
            line,
            lineEnd,
            col,
            colEnd,
        )
        return VariableReassignment(name, expr, line, lineEnd, col, colEnd)

    def parse_break_statement(self):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        if not self.expect_token(TokenType.SEMICOLON):
            return
        lineEnd = self.ct.line
        colEnd = self.ct.colEnd
        return BreakStatement(line, lineEnd, col, colEnd)

    def parse_continue_statement(self):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        if not self.expect_token(TokenType.SEMICOLON):
            return
        lineEnd = self.ct.line
        colEnd = self.ct.colEnd
        return ContinueStatement(line, lineEnd, col, colEnd)

    def parse_input_statement(self, expr=False):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        if not self.expect_token(TokenType.LEFTPAREN):
            return
        self.adv()
        prompt = self.parse_expression(ending=TokenType.RIGHTPAREN)
        if not expr:
            self.adv()
            if not self.expect_token(TokenType.SEMICOLON):
                return
        lineEnd = self.ct.line
        colEnd = self.ct.colEnd
        return InputStatement(prompt, line, lineEnd, col, colEnd)

    def parse_function(self):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        if not self.expect_token(TokenType.IDENTIFIER):
            return
        name = self.ct.value
        self.adv()
        if not self.expect_token(TokenType.LEFTPAREN):
            return
        self.adv()
        params = {}
        while self.ct and self.ct != TokenType.RIGHTPAREN:
            param_name = self.ct.value
            param_type = "dynamic"
            self.adv()
            if self.ct == TokenType.COLON:
                self.adv()
                param_type = self.parse_data_type()
                self.adv()
            params[param_name] = param_type
            if self.ct == TokenType.RIGHTPAREN:
                break
            self.adv()
        self.adv()
        return_type = None
        if self.ct == TokenType.MINUS and self.peek() == TokenType.GREATERTHAN:
            self.adv()
            return_type = self.parse_data_type()
        if not self.expect_token(TokenType.LEFTBRACE):
            return
        body = self.parse_block_statement()
        lineEnd = self.ct.line
        colEnd = self.ct.colEnd
        return FunctionStatement(
            name, params, body, return_type, line, lineEnd, col, colEnd
        )

    def parse_function_call(self, expr=False):
        line = self.ct.line
        col = self.ct.col
        func_name = self.ct.value
        self.adv()
        if not self.expect_token(TokenType.LEFTPAREN):
            return
        self.adv()
        args = []
        while self.ct and self.ct != TokenType.RIGHTPAREN:
            args.append(
                self.parse_expression(
                    ending=TokenType.RIGHTPAREN, altEnding=TokenType.COMMA
                )
            )
            if self.ct == TokenType.RIGHTPAREN:
                break
            self.adv()
        if not self.expect_token(TokenType.RIGHTPAREN):
            return
        if not expr:
            self.adv()
            if not self.expect_token(TokenType.SEMICOLON):
                return
        lineEnd = self.ct.line
        colEnd = self.ct.colEnd
        return FunctionCall(
            name=func_name,
            args=args,
            line=line,
            lineEnd=lineEnd,
            col=col,
            colEnd=colEnd,
        )

    def parse_return_statement(self):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        value = self.parse_expression()
        lineEnd = self.ct.line
        colEnd = self.ct.colEnd
        return ReturnStatement(value, line, lineEnd, col, colEnd)

    def parse_for_statement(self):
        line = self.ct.line
        col = self.ct.col
        self.adv()
        if not self.expect_token(TokenType.IDENTIFIER):
            return
        iter_name = self.ct.value
        self.adv()
        if not self.expect_token(Token(TokenType.KEYWORD, "in")):
            return
        self.adv()
        rng = self.parse_expression(ending=TokenType.LEFTBRACE)
        body = self.parse_block_statement()
        lineEnd = self.ct.line
        colEnd = self.ct.colEnd
        return ForStatement(iter_name, rng, body, line, lineEnd, col, colEnd)

    def parse_get_item(self):
        line = self.ct.line
        col = self.ct.col
        name = self.ct.value
        self.adv(2)
        index = self.parse_expression(ending=TokenType.RIGHTBRACKET)
        if self.peek() == TokenType.ASSIGN:
            lineEnd = self.ct.line
            colEnd = self.ct.colEnd
            val = self.parse_reassignment(
                GetItem(name, index, line, lineEnd, col, colEnd)
            )
        elif self.peek() == TokenType.COMPOUNDASSIGNMENT:
            lineEnd = self.ct.line
            colEnd = self.ct.colEnd
            val = self.parse_compound_assignment(
                GetItem(name, index, line, lineEnd, col, colEnd), self.peek().value[0]
            )
        if not self.expect_token(TokenType.SEMICOLON):
            return
        val.line = line
        val.col = col
        return val

    def parse_statement(self):
        if self.ct == TokenType.KEYWORD:
            return self.KEYWORD_HANDLERS[self.ct.value]()
        elif self.ct == TokenType.IDENTIFIER and self.peek() == TokenType.ASSIGN:
            return self.parse_reassignment(self.ct)
        elif self.ct == TokenType.IDENTIFIER and self.peek() == TokenType.LEFTBRACKET:
            return self.parse_get_item()
        elif (
            self.ct == TokenType.IDENTIFIER
            and self.peek() == TokenType.COMPOUNDASSIGNMENT
        ):
            return self.parse_compound_assignment(self.ct, self.peek().value)
        elif self.ct == TokenType.IDENTIFIER and self.peek() == TokenType.LEFTPAREN:
            return self.parse_function_call()
        elif self.ct == TokenType.IDENTIFIER and self.peek() in (
            TokenType.INCREMENT,
            TokenType.DECREMENT,
        ):
            return self.parse_incrementation_decrementation(self.ct, self.peek().type)
        else:
            pos_info = f"{self.ct.line}:{self.ct.col}-{self.ct.colEnd}"
            error(
                self.errinfomod,
                ErrorType.UnexpectedToken,
                ErrorIDs.UnexpectedToken,
                pos_info,
                self.ct.type,
            )
            self.errored = True

    def parse(self):
        while self.ct is not None:
            self.ast.append(self.parse_statement())
            self.adv()
        if self.errored:
            _exit(self.errinfomod, 1)
        return self.ast
