# Copyright (C) 2026 BasaltDev
# SPDX-License-Identifier: GPL-3.0-only

from coloring import Back, Fore, Style

# dedicated module for explanation table


class EXPLANATIONS:
    E0001 = f"""E0001 is the {Fore.RED}Malformed String{Fore.RESET} error code.
The Malformed String error usually occurs when you have a string literal that
doesn't end with a double-quote or has a newline character (NOT "\\n") in it, for \
example:
    {Back.BLACK}{Fore.RED}"Hello,{Style.RESET_ALL}
    {Back.BLACK}{Fore.RED}World!"{Style.RESET_ALL}
or:
    {Back.BLACK}{Fore.RED}"Hello World! {Fore.LIGHTGREEN_EX}// doesn't end with a quote\
{Style.RESET_ALL}
To fix this error you can usually just remove the newlines or add the quote, for \
example:
    {Back.BLACK}{Fore.RED}"Hello,{Back.RESET} {Fore.GREEN}-> {Back.BLACK}\
"Hello, World!"{Style.RESET_ALL}
    {Back.BLACK}{Fore.RED}World!"{Style.RESET_ALL}
or:
    {Back.BLACK}{Fore.RED}"Hello, World!{Back.RESET} {Fore.GREEN}-> {Back.BLACK}\
"Hello, World!"{Style.RESET_ALL}"""
    E0002 = f"""E0002 is the {Fore.RED}Malformed Float{Fore.RESET} error code.
The Malformed Float error usually occurs when you have a floating point literal
that has more than 1 decimal point, e.g.:
    {Back.BLACK}1.5{Fore.RED}.0{Style.RESET_ALL}
To fix this error you can usually just remove all the extra decimal points, \
for example:
    {Back.BLACK}1.5{Fore.RED}.0{Back.RESET} {Fore.LIGHTGREEN_EX}->{Fore.RESET} \
{Back.BLACK}1.50{Back.RESET}"""
    E0003 = f"""E0003 is the {Fore.RED}Token Expected{Fore.RESET} error code.
The Token Expected error usually occurs when you're missing an important token at
the end of a line, for example, a semicolon:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(1 + 5){Fore.LIGHTGREEN_EX} // missing \
semicolon{Style.RESET_ALL}
Usually you can just fix this by adding said token, for example:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(1 + 5){Fore.LIGHTGREEN_EX}{Back.RESET} \
-> {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(1 + 5){Fore.RED};{Style.RESET_ALL}"""
    E0004 = f"""E0004 is the {Fore.RED}Unexpected Character{Fore.RESET} error code.
The Unexpected Character error occurs when you type a character not recognized
by the lexer, for example:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(1 + 5){Fore.LIGHTRED_EX}?\
{Style.RESET_ALL}
The easiest way to fix this is to just remove said character or replace it, for example:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(1 + 5){Fore.LIGHTRED_EX}?\
{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}-> {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}\
(1 + 5){Fore.LIGHTGREEN_EX};{Style.RESET_ALL}"""
    E0005 = f"""E0005 is the {Fore.RED}Unexpected Token{Fore.RESET} error code.
The Unexpected Token error occurs when a token is not expected by the parser,
for example:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(1 + 5){Fore.LIGHTRED_EX}%\
{Style.RESET_ALL}
Here, there's an unexpected "MOD" token (modulo operator).
The easiest way to fix this is to just remove said token or replace it, for example:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(1 + 5){Fore.LIGHTRED_EX}%\
{Style.RESET_ALL} -> {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(1 + 5)\
{Fore.LIGHTGREEN_EX};{Style.RESET_ALL}"""
    E0006 = f"""E0006 is the {Fore.RED}Undefined Symbol{Fore.RESET} error code.
The Undefined Symbol error usually occurs when you try to use an instance variable, \
function or
another symbol type, that doesn't exist. For example:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}({Fore.RED}a{Fore.RESET});\
{Fore.LIGHTGREEN_EX}// we never defined `a` as a variable{Fore.RESET}{Back.RESET}
The easiest way to fix it is to just define said symbol, for example:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}({Fore.RED}a{Fore.RESET});{Back.RESET}\
{Fore.GREEN} -> {Back.BLACK}{Fore.YELLOW}let {Fore.RESET}a = 10;{Back.RESET}
                 {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}({Fore.GREEN}a{Fore.RESET});{Back.RESET}"""
    E0007 = f"""E0007 is the {Fore.RED}Zero Division{Fore.RESET} error code.
The Zero Division error is self-explanatory; it occurs when you try to divide something\
 by 0.
For example:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}({Fore.LIGHTRED_EX}1 / 0{Fore.RESET});\
{Back.RESET}
The fix is straightforward. If the value is not determined by user input, you can \
change the value. Otherwise,
figure something out."""
    E0008 = f"""E0008 is the {Fore.RED}Type Mismatch{Fore.RESET} error group.
There are multiple error codes that fall under this group:
- {Fore.YELLOW}E0008A{Fore.RESET}: Operator Type Mismatch
- {Fore.YELLOW}E0008B{Fore.RESET}: Assignment Type Mismatch
- {Fore.YELLOW}E0008C{Fore.RESET}: Conditional Type Mismatch
To fix these, ensure the data types align correctly based on the specific error \
code above."""
    E0008A = f"""E0008A is the {Fore.RED}Operator Type Mismatch{Fore.RESET} error code.
Specifically, this error occurs when you try to use an operator with an unsupported \
type, for example,
trying to add a string and an int:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}({Fore.RED}"A" + 10{Fore.RESET});\
{Fore.GREEN} // adding a string and an int{Style.RESET_ALL}
The fix can be one of three things:
- type-casting the mismatching value: {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(\
{Fore.LIGHTGREEN_EX}"A" + <{Fore.YELLOW}string{Fore.LIGHTGREEN_EX}>10{Fore.RESET});\
{Back.RESET}
- changing the type of the mismatching value: {Back.BLACK}{Fore.YELLOW}print\
{Fore.RESET}({Fore.LIGHTGREEN_EX}"A" + "10"{Fore.RESET});{Back.RESET}
- removing the operation altogether.
For more information on E0008, run {Back.BLACK}{Fore.YELLOW}dust{Fore.RESET} --explain \
E0008{Style.RESET_ALL}"""
    E0008B = f"""E0008B is the {Fore.RED}Assignment Type Mismatch{Fore.RESET} error \
code.
Specifically, this error occurs when you try to assign a value to a variable of a \
different type.
Said variable will 100% have a type annotation since this language is Gradually Typed \
(meaning
variables are dynamic until you add a type annotation).
For example:
    {Back.BLACK}{Fore.YELLOW}let{Fore.RESET} a: int = {Fore.RED}"10"{Fore.RESET};\
{Fore.GREEN} // setting a string as the value of an int variable{Style.RESET_ALL}
The fix can be one of three things:
- type-casting the value to the correct type: {Back.BLACK}{Fore.YELLOW}let{Fore.RESET} \
a: int = {Fore.GREEN}<int>"10"{Fore.RESET};{Back.RESET}
- changing the type of the mismatching value: {Back.BLACK}{Fore.YELLOW}let\
{Fore.RESET} a: int = {Fore.LIGHTGREEN_EX}10{Fore.RESET};{Back.RESET}
- changing the variable type: {Back.BLACK}{Fore.YELLOW}let {Fore.RESET}a: \
{Fore.LIGHTGREEN_EX}string{Fore.RESET} = "10";{Back.RESET}
For more information on E0008, run {Back.BLACK}{Fore.YELLOW}dust{Fore.RESET} --explain \
E0008{Style.RESET_ALL}"""
    E0008C = f"""E0008C is the {Fore.RED}Conditional Type Mismatch{Fore.RESET} error \
code.
Specifically, this error occurs when you try to use a non-boolean value as the \
condition for a
conditional statement such as if or while.
This is because Dust doesn't support truthiness, it's either true or false, nothing in-\
between.
Here's an example of some broken code:
    {Back.BLACK}{Fore.YELLOW}if{Fore.RED} 1 + 2 {Fore.RESET}{{ {Fore.LIGHTGREEN_EX}/* \
do something */ {Fore.RESET}}}{Style.RESET_ALL}
The fix is usually:
- adding a comparison: {Back.BLACK}{Fore.YELLOW}if{Fore.LIGHTGREEN_EX} (1 + 2) == 3 \
{Fore.RESET}{{ {Fore.LIGHTGREEN_EX}/* do something */ {Fore.RESET}}}{Style.RESET_ALL}
- passing an explicit boolean value: {Back.BLACK}{Fore.YELLOW}if{Fore.LIGHTGREEN_EX} \
true {Fore.RESET} {{ {Fore.LIGHTGREEN_EX}/* do something */{Fore.RESET} }}\
{Style.RESET_ALL}
For more information on E0008, run {Back.BLACK}{Fore.YELLOW}dust{Fore.RESET} --explain \
E0008{Style.RESET_ALL}"""
    E0009 = f"""E0009 is the {Fore.RED}Const Reassignment{Fore.RESET} error code.
It's self-explanatory; the Const Reassignment error occurs when you try to reassign
the value of a CONST variable. For example:
    {Back.BLACK}{Fore.YELLOW}const{Fore.RESET} a = 10;{Back.RESET}
    {Back.BLACK}{Fore.RED}a = 20;{Style.RESET_ALL}
To fix it, you can:
- replace the CONST keyword in the variable definition: {Back.BLACK}{Fore.GREEN}let\
{Fore.RESET} a = 10;{Style.RESET_ALL}
- remove the reassignment."""
    E0010 = f"""E0010 is the {Fore.RED}Keyword Outside of Context{Fore.RESET} error \
code.
It occurs when you use a keyword that is only meant to be used in a specific statement \
type,
for example, if you use the {Back.BLACK}{Fore.YELLOW}break{Fore.RESET};{Back.RESET} or \
{Back.BLACK}{Fore.YELLOW}continue{Fore.RESET};{Back.RESET} statement outside of a loop:
    {Back.BLACK}{Fore.YELLOW}while{Fore.RESET} x < 10 {{{Back.RESET}
    {Back.BLACK}    {Style.DIM}...{Style.RESET_ALL}
    {Back.BLACK}}}{Back.RESET}
    {Back.BLACK}{Fore.YELLOW}break{Fore.RESET}; {Fore.GREEN}// using break outside of \
a loop{Style.RESET_ALL}
There are two fixes:
- removing the statement:
    {Back.BLACK}{Fore.YELLOW}while{Fore.RESET} x < 10 {{{Back.RESET}
    {Back.BLACK}    {Style.DIM}...{Style.RESET_ALL}
    {Back.BLACK}}}{Back.RESET}
- moving the statement into the right context:
    {Back.BLACK}{Fore.YELLOW}while{Fore.RESET} x < 10 {{{Back.RESET}
    {Back.BLACK}    {Style.DIM}...{Style.RESET_ALL}
    {Back.BLACK}    {Fore.GREEN}break;{Style.RESET_ALL}
    {Back.BLACK}    {Style.DIM}...{Style.RESET_ALL}
    {Back.BLACK}}}{Back.RESET}"""
    E0011 = f"""E0011 is the {Fore.RED}Type Cast Error{Fore.RESET} code.
The Type Cast Error occurs when you attempt to cast a value to another type
but the value cannot be cast to said type.
For example, when you do something like this:
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}(<{Fore.YELLOW}int{Fore.RESET}>{Fore.RED}\
"a"{Fore.RESET}); {Fore.GREEN}// attempting to turn "a" into an int, yeah...\
{Style.RESET_ALL}
There are two fixes:
    - validating/sanitizing the data before casting.
    - providing a valid literal or a compatible expression: {Back.BLACK}{Fore.YELLOW}\
print{Fore.RESET}(<{Fore.YELLOW}int{Fore.RESET}>{Fore.GREEN}"123"{Fore.RESET});{Back.RESET}"""
    E0012 = f"""E0012 is the {Fore.RED}Keyboard Interrupt{Fore.RESET} error code.
This needs no explanation; this error occurs when the user interrupts the program,
usually by pressing Ctrl+C."""
    E0013 = f"""E0013 is the {Fore.RED}Not a Function{Fore.RESET} error code.
The Not a Function error occurs when you try to call something that isn't a function,
for example:
    {Back.BLACK}{Fore.YELLOW}let{Fore.RESET} a = 10;{Back.RESET}
    {Back.BLACK}{Fore.RED}a();{Fore.GREEN} // trying to call an int variable\
{Style.RESET_ALL}
There are two fixes:
    - defining the callee as a function
    - removing the function call."""
    E0014 = f"""E0014 is the {Fore.RED}Argument Count Mismatch{Fore.RESET} error code.
The Argument Count Mismatch error occurs when you pass the incorrect amount of s\
arguments to a function. For example:
    {Back.BLACK}{Fore.YELLOW}func{Fore.RESET} sum(x, y) {{{Back.RESET}
    {Back.BLACK}    {Fore.YELLOW}return{Fore.RESET} x + y;{Back.RESET}
    {Back.BLACK}}}{Back.RESET}
    {Back.BLACK}{Fore.YELLOW}print{Fore.RESET}({Fore.RED}sum(10, 20, 30){Fore.RESET}); \
{Fore.GREEN}// calling sum() with 3 arguments instead of 2{Style.RESET_ALL}
There are two fixes:
    - changing the function signature
    - removing the extra arguments"""
    E0015 = f"""E0015 is the {Fore.RED}Already Defined Symbol{Fore.RESET} error code.
The Already Defined Symbol error occurs when you try to define a symbol
(using let or func) that already exists, for example:
    {Back.BLACK}{Fore.YELLOW}let{Fore.RESET} a = 10;{Back.RESET}
    {Back.BLACK}{Style.DIM}...{Style.RESET_ALL}
    {Back.BLACK}{Fore.YELLOW}let{Fore.RESET} a = 20;{Fore.GREEN} // \
assigning to a after already assigning it{Style.RESET_ALL}
There are two fixes:
    - removing the original definition
    - changing the second definition to a reassignment."""
    E0016 = f"""E0016 is the {Fore.RED}Not a Type{Fore.RESET} error code.
The Not a Type error occurs when you try to put something that is not a valid
data type as an annotation for a let statement or a function parameter, for example:
    {Back.BLACK}{Fore.YELLOW}let{Fore.RESET} a: {Fore.RED}HIIII{Fore.RESET} = 10; \
{Fore.GREEN}// `HIIII` is not a type{Style.RESET_ALL}
There are two fixes:
    - change the type
    - remove the annotation."""
    E0017 = f"""E0017 is the {Fore.RED}Recursion Depth Error{Fore.RESET} code.
It occurs when you exceed 1000 stack frames. There is no specific explanation
or fix for it."""
