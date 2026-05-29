# Copyright (C) 2026 BasaltDev
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.

import contextlib
import os
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

from Analyzer import Analyzer
from coloring import Fore
from Error import ErrorIDs, ErrorInfo, ErrorType, error
from Explanations import EXPLANATIONS
from Interpreter import Interpreter
from Lexer import Lexer
from Parser import Parser

LEXER_DEBUG = False
EXECUTE_PARSER = True
PARSER_DEBUG = False
INTERPRET = True

psr = ArgumentParser(description="The Dust programming language")
psr.add_argument("-r", "--run", help="runs a Dust program")
psr.add_argument(
    "--explain",
    type=lambda s: list(set(s.split(","))),
    help="explains something (e.g. '--explain E0001')",
)
psr.add_argument("-v", "--version", action="version", version="Dust v0.0.1")
psr.add_argument(
    "-c",
    "--check",
    action="store_true",
    help="runs a suite of tests to check if the Dust interpreter works.",
)
psr.add_argument(
    "--check-reduce-output",
    action="store_true",
    help="reduces the output of the Dust interpreter check (--check).",
)
psr.add_argument(
    "--time",
    action="store_true",
    help="times the full execution, from lexing to interpreting, of your Dust program",
)
args = psr.parse_args()


def interpret(file):
    with open(file, encoding="utf-8") as f:
        source = f.read()
    errinfo = ErrorInfo(file, source)
    lexer = Lexer(source, file, errinfo)
    tokens = lexer.tokenize()
    if LEXER_DEBUG:
        print("========== TOKEN ==========")
        print("\n".join(str(token) for token in tokens))
        print("===========================")
    if not EXECUTE_PARSER:
        sys.exit()
    parser = Parser(tokens, file, errinfo)
    ast = parser.parse()
    if PARSER_DEBUG:
        print("=========== AST ===========")
        print("\n".join(str(node) for node in ast))
        print("===========================")
    if not INTERPRET:
        sys.exit()
    analyzer = Analyzer(ast, file, errinfo)
    analyzer.analyze()
    start_time = time.perf_counter()
    try:
        interpreter = Interpreter(ast, file, errinfo)
        interpreter.interpret()
    except KeyboardInterrupt:
        if not interpreter.cn:
            interpreter.adv(-1)
        if interpreter.inputting:
            print()
        position = f"{interpreter.cn.line}-{interpreter.cn.lineEnd}:{
            interpreter.cn.col
        }-{interpreter.cn.colEnd}"
        error(
            errinfo,
            ErrorType.KeyboardInterruptError,
            ErrorIDs.KeyboardInterruptError,
            position,
            show_code=False,
        )
    end_time = time.perf_counter()
    if args.time:
        print(
            f"Executed in {(end_time - start_time) * 1000:.2f}ms (\
{(end_time - start_time):.2f}s)"
        )


if args.explain:
    args.explain.sort()
    import re

    ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
    cnt = 0
    found = False
    for val in args.explain:
        value = getattr(EXPLANATIONS, val.upper(), None)
        if not value:
            print(f"Could not find an explanation for `{val}`")
        else:
            found = True
            print(
                f"{'┎' if cnt < 1 else '┠'}{f'`{val}` EXPLANATION':─^123}{
                    '┒' if cnt < 1 else '┨'
                }"
            )
            for i in value.split("\n"):
                visible_len = len(ANSI_ESCAPE.sub("", i))
                padding = " " * (121 - visible_len)
                print(f"┃ {i}{padding} ┃")
            if cnt < len(args.explain) - 1:
                print(f"┃{' ' * 123}┃")
        cnt += 1
    if found:
        print(f"┖{'─' * 123}┚")
elif args.run:
    interpret(args.run)
elif args.check:
    silence_stdout = (
        contextlib.redirect_stdout(open(os.devnull, "w"))
        if args.check_reduce_output
        else contextlib.nullcontext()
    )
    directory = Path(__file__).resolve().parent / "tests"
    print("Checking Dust...")
    overall = True
    GREEN = Fore.GREEN
    RED = Fore.RED
    RES = Fore.RESET
    with silence_stdout:
        print("Running tests where success is required...")
        for fp in (directory / "success").glob("*ds"):
            status = True
            print(f"Running {fp.name}:")
            try:
                interpret(str(fp))
                print("Interpreter executed successfully")
            except SystemExit:
                print("Interpreter exited abnormally")
                status = False
                overall = False
            except Exception as e:
                print("Interpreter crashed abnormally")
                print(f"  > {e}")
                status = False
                overall = False
            print(
                f"Test status: {f'{GREEN}SUCCESS' if status else f'{RED}FAILURE'}{RES}"
            )
        print("Running tests where failure is required...")
        for fp in (directory / "failure").glob("*ds"):
            status = True
            print(f"Running {fp.name}:")
            try:
                interpret(str(fp))
                print("Interpreter executed successfully")
                status = False
                overall = False
            except SystemExit:
                print("Interpreter exited abnormally")
                status = True
            except Exception as e:
                print("Interpreter crashed abnormally")
                print(f"  > {e}")
                status = True
            print(
                f"Test status: {f'{GREEN}SUCCESS' if status else f'{RED}FAILURE'}{RES}"
            )
    print(
        "Overall status: Interpreter is "
        f"{f'{GREEN}FINE' if overall else f'{RED}NOT FINE'}{RES}."
    )
    if not overall:
        if args.check_reduce_output:
            print(
                "Your interpreter is malfunctioning."
                "Try updating to the latest Dust version."
            )
        else:
            print(
                "Your interpreter may be malfunctioning or you may have received a"
                "corrupted, old, or bad copy of Dust."
            )
            print("Try updating to the latest Dust version.")
else:
    psr.print_help()
