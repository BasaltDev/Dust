# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

import unicodedata

from coloring import Fore, Style
from Token import Token, TokenType


def char_width(char):
    amt = 1
    if unicodedata.east_asian_width(char) in ("F", "W"):
        amt = 2
    return amt


class ErrorInfo:
    def __init__(self, filename, source_code):
        self.filename = filename
        self.source_code = source_code
        self.source_lines = source_code.split("\n")
        self.error_table = []


class ErrorType:
    @staticmethod
    def MalformedString(malformed):
        return (f"Malformed string literal `{malformed}`",)

    @staticmethod
    def MalformedFloat(malformed):
        return (
            f"Malformed floating point literal `{malformed}`",
            f"The floating point literal `{malformed}` has too many decimal points/\
dots. Try turning it into:\n    `{Fore.RED}{malformed}{Fore.RESET}` -----> `\
{Fore.LIGHTGREEN_EX}{
                ''.join([malformed.split('.')[0] + '.', *malformed.split('.')[1:]])
            }{Fore.RESET}`",
        )

    @staticmethod
    def TokenExpected(token: Token, got):
        got_repr = ""
        if got is None:
            got_repr = "nothing"
        else:
            if isinstance(got, TokenType) or got.value is None:
                got_value = None
            else:
                got_value = "temp"
            if got_value is None:
                got_repr = f"token of type `{got.type.name}`"
            else:
                got_repr = f"token of type `{got.type.name}`, value `{got.value}`"
        token_repr = ""
        if isinstance(token, TokenType):
            token_value = None
        if token_value is None:
            token_repr = f"token of type `{token.name}`"
        else:
            token_repr = f"token of type `{token.type.name}`, value `{token.value}`"
        msg = f"Expected {token_repr}, got {got_repr}"
        _help = None
        if got_repr != "nothing":
            _help = "Try removing the unexpected token or replacing it with the\
expected token."
        else:
            _help = "Try adding the expected token."
        return (msg, _help) if _help else msg

    @staticmethod
    def UnexpectedCharacter(character):
        return (
            f"Unexpected character `{character}`",
            "Try removing the unexpected character or replacing it.",
        )

    @staticmethod
    def UnexpectedToken(token):
        token_repr = ""
        if isinstance(token, TokenType):
            token_value = None
        else:
            token_value = token.value
        if token_value is None:
            token_repr = f"token of type `{token.name}`"
        else:
            token_repr = f"token of type `{token.type.name}`, value `{token.value}`"
        return (
            f"Unexpected {token_repr}",
            "Try removing the unexpected token or replacing it.",
        )

    @staticmethod
    def UndefinedSymbol(symbol_name):
        return (f"Undefined symbol `{symbol_name}`", "Try defining the symbol.")

    @staticmethod
    def ZeroDivision(intentional=False):
        return (
            "Division by zero",
            (
                "You can't divide by zero."
                + (
                    f"\n{Style.DIM}(on a side note, if this was intentional, why would \
you divide with zero? what's gotten into you?){Style.RESET_ALL}"
                    if intentional
                    else ""
                )
            ),
        )

    @staticmethod
    def OperatorTypeMismatch(operator, type1, type2):
        return (
            f"Unsupported operator `{operator}` for values of type `{type1}` and \
`{type2}`",
            "Try casting one type to the other or removing the operation altogether.",
        )

    @staticmethod
    def AssignmentTypeMismatch(type1, type2):
        return (
            f"Attempted to assign to a variable of type `{type1}` with a value of \
`{type2}`",
            "Try casting one type to the other or using a different value.",
        )

    @staticmethod
    def ConditionalTypeMismatch(typ):
        return (
            f"Attempted to use value of type `{typ}` in conditional",
            "Dust doesn't have truthiness.",
        )

    @staticmethod
    def ConstReassignment(name):
        return (
            f"Reassignment to a constant variable `{name}`",
            f"Try making `{name}` a non-const variable or removing the reassignment.",
        )

    @staticmethod
    def KeywordOutsideOfContext(keyword, context):
        return (
            f"Using `{keyword}` keyword outside of a {context}",
            f"Try putting the `{keyword}` keyword in its right context ({context}) or \
removing the statement altogether.",
        )

    @staticmethod
    def TypeCastError(value, typ):
        return f"Could not cast value {
            f'`{value}`' if not isinstance(value, str) else f'"{value}"'
        } to type `{typ}`"

    @staticmethod
    def KeyboardInterruptError():
        return "A keyboard interrupt occurred"

    @staticmethod
    def NotAFunction(name):
        return (
            f"Attempted to call non-function object `{name}`",
            f"Try defining `{name}` as a function or removing the function call.",
        )

    @staticmethod
    def ArgumentCountMismatch(name, expected, got):
        return (
            f"Expected {expected} arguments for `{name}`, got {got}",
            "Try changing the number of arguments passed to the function or changing \
the function definition to expect a different number of arguments.",
        )

    @staticmethod
    def AlreadyDefinedSymbol(name):
        return (
            f"Symbol `{name}` is already defined in the current scope",
            f"Try renaming the new symbol or removing the new definition of `{name}`.",
        )


class ErrorIDs:
    MalformedString = "E0001"
    MalformedFloat = "E0002"
    TokenExpected = "E0003"
    UnexpectedCharacter = "E0004"
    UnexpectedToken = "E0005"
    UndefinedSymbol = "E0006"
    ZeroDivision = "E0007"
    OperatorTypeMismatch = "E0008A"
    AssignmentTypeMismatch = "E0008B"
    ConditionalTypeMismatch = "E0008C"
    ConstReassignment = "E0009"
    KeywordOutsideOfContext = "E0010"
    TypeCastError = "E0011"
    KeyboardInterruptError = "E0012"
    NotAFunction = "E0013"
    ArgumentCountMismatch = "E0014"
    AlreadyDefinedSymbol = "E0015"


def error(
    error_info: ErrorInfo,
    error_type,
    error_id: ErrorIDs,
    position_info: str,
    *args,
    show_code=True,
):
    errmsg = error_type(*args)
    plines = position_info.split(":")[0]
    if len(plines.split("-")) > 1 and int(plines.split("-")[0]) == int(
        plines.split("-")[1]
    ):
        plines = plines.split("-")[0]
    cols = position_info.split(":")[1]
    displaycols = cols
    if int(cols.split("-")[1]) - 1 == int(cols.split("-")[0]):
        displaycols = cols.split("-")[0]
    print(
        f"{Fore.GREEN}{error_info.filename}{Fore.RESET}:{Fore.YELLOW}{plines}\
{Fore.RESET}:{Fore.RED}{displaycols} {Fore.LIGHTRED_EX} Error[{error_id}]: {Fore.RESET}\
{errmsg[0] if isinstance(errmsg, tuple) else errmsg}"
    )
    if not show_code:
        error_info.error_table.append(error_id)
        return
    splitted = position_info.split(":")
    lines = splitted[0]
    if not lines.isdigit():
        lines = lines.split("-")
        line = int(lines[0])
        lineEnd = int(lines[1])
    else:
        line = int(lines)
        lineEnd = line
    cols = splitted[1].split("-")
    col = int(cols[0])
    colEnd = int(cols[1])
    ln = error_info.source_lines[line - 1]
    if line != lineEnd:
        for lin in range(line, lineEnd + 1):
            ln = error_info.source_lines[lin - 1]
            print(f"{Style.DIM}{Fore.BLACK}          |")
            print(f"{lin:>9} | {Style.RESET_ALL}{ln}{Fore.BLACK}{Style.DIM}")
            print("          | " + Style.RESET_ALL + Fore.RED, end="")
            for i in range(len(ln) + 1):
                if (
                    (i >= (col - 1) and lin == line)
                    or (i < (colEnd - 1) and lin == lineEnd)
                    or (lin not in (line, lineEnd) and i < len(ln))
                ):
                    print("^", end="")
                elif i < len(ln) and ln[i] == "\t":
                    print("\t", end="")
                elif i < len(ln) and char_width(ln[i]) > 1:
                    print(" " * char_width(ln[i]), end="")
                else:
                    print(" ", end="")
            print()
        print(f"{Style.DIM}{Fore.BLACK}          | {Style.NORMAL}{Fore.RED}")
    else:
        print(f"{Style.DIM}{Fore.BLACK}          |")
        print(f"{line:>9} | {Style.RESET_ALL}{ln}")
        print(f"{Style.DIM}{Fore.BLACK}          | {Style.NORMAL}{Fore.RED}", end="")
        for i in range(len(ln) + 1):
            if i >= (col - 1) and i < (colEnd - 1):
                print("^", end="")
            elif i < len(ln) and ln[i] == "\t":
                print("\t", end="")
            elif i < len(ln) and char_width(ln[i]) > 1:
                print(" " * char_width(ln[i]), end="")
            else:
                print(" ", end="")
    print(Style.RESET_ALL)
    if isinstance(errmsg, tuple) and len(errmsg) > 1:
        print(f"{Fore.LIGHTGREEN_EX}Help: {Fore.RESET}{errmsg[1]}")
    error_info.error_table.append(error_id)


def error_exit(errinfomod: ErrorInfo):
    if errinfomod.error_table:
        print(
            "If you need additional help to debug your program, you can use the "
            "--explain command!"
        )
        print(
            "To explain all the errors you've encountered, you might run a command like"
            " this:"
        )
        sorted_errors = list(set(errinfomod.error_table))
        sorted_errors.sort()
        print(
            f"{Fore.LIGHTYELLOW_EX}    dust{Fore.RESET} --explain {
                ','.join(sorted_errors)
            }"
        )
    print(f"{Fore.RED}Exiting due to failure...{Fore.RESET}")
