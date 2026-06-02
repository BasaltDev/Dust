# Dust
### A unique interpreted programming language
<small>By BasaltDev</small>
---

### Table of Contents
- [About](#about)
- [Features](#features)
- [Syntax](#syntax)
- [How to Run](#how-to-run)
- [License](#license)
- [DISCLAIMERS](#disclaimers)

---

<a name="about"></a>
## About
Dust is an old-school, curly-braces, semicolons, gradually typed programming language built in Python.

<small>Don't judge, just 'cause it's interpreted doesn't mean it's terrible.</small>

The original version of Dust was written in only 7 days and most of the code behind it is original. Pretty cool, right?

<a name="features"></a>
## Features
* **Gradual Typing:** Dust offers you a choice between static and dynamic types using a Gradual Typing system.
* **Modern Syntax:** C-style feel with a touch of modern programming languages.
* **High-Quality Errors and Explanations:** Dust has a high-quality error system that shows where an error happened, exactly the lines and columns where it happened, help on how to fix it and commands to explain the errors in detail.
* **Tooling:** Dust comes with a fair bit of tooling, including a syntax highlighting extension for Visual Studio Code, a work-in-progress LSP (Language Server Protocol) and a built-in testing "framework" (more of a DSL).

<a name ="syntax"></a>
## Syntax
Dust has a slightly unique syntax, but it's very similar to languages like Rust.

### Basic Operations
Dust has most of the arithmetic and logical operators required to function as a normal language, excluding bitwise operators:
|Operator|Explanation|
|---|---|
| `+`, `-`, `*`, `/`, `%` | Essential arithmetic operators |
| `\` | The integer-division operator. Unlike some languages where you would do a // b or int(a / b), we use the backslash as our idiv.
| `==`, `!=` | Essential equality operators | 
| `<`, `>`, `<=`, `>=` | Essential comparison operators |
| `!`, `&&`, `\|\|` | Essential logical operators: NOT, AND and OR |

It also has the standard compound/in-place operators:

| In-Place Operator | Explanation |
|---|---|
| `+=`, `-=`, `*=`, `/=`, `%=`, `\=` | Essential compound arithmetic operators |
| `++`, `--` | Incrementation and decrementation. Fair warning: these do NOT work in expressions. They are standalone statements. |

### Variables
Variables are a key feature in every programming language, you can define them like this:
```Rust
let a = 10;
```
Variables are mutable by default; if you want it to be immutable, define it as a const:
```Rust
const a = 10;
```
Dust also supports a gradual typing system, meaning that if you annotate your variable definition with one of the standard data types (`int`, `float`, `bool`, `string` and more to come soon), the interpreter will enforce the type of the variable stays the same:
```Rust
let a: int = 10;
a = 10.5; // Error[E0008B]: Attempted to assign to a variable of type `int` with a value of type `float`
```
You could technically add a type annotation to a const definition, but what's the point? A constant variable's value never changes.

### Print Statements
Print statements look as you would expect and work as you'd expect:
```Python
print("Hello, World!", ...);
```
Unlike languages like C, you don't need a format string. You can just put whatever arguments you want into the print statement and you can put as many arguments as you want.

### Gathering User Input
Dust has a built-in `input()` keyword. You can use it in expressions or like this:
```Rust
let name = input("Hello, what's your name");
print(name);
input("");
```

It returns the value that the user inputted into your program. One thing to note is that the input() function MUST be supplied a prompt, otherwise it will break.

### If Statements

If statements (and conditions in general) are also a key part of any language. You can write them like this:
```Rust
if condition1 {
    // do something
} else if condition2 {
    // do something else
} else {
    // do some final thing
}
```
A few things to note:
* The condition doesn't need to be enclosed in parentheses
* The condition MUST evaluate to a boolean value, as Dust doesn't have truthiness.
* Each statement's body MUST have a block statement (`{ /*...*/ }`) or it won't work.
* You can write as many else-if branches as you want, or none if you don't need to! The same goes with the else branch, except you can only have 1 else branch (logically)

Essentially, for beginners, the pattern goes like this:
```
find if statement -> check truth of condition
    -> if true, execute main if branch
    -> otherwise, execute else branch
        -> if else branch is else-if, repeat the process
```

### While Statements/Loops
Currently, `while` is the only loop in Dust. It works similarly to the if statement:
```Rust
while condition {
    // do something
}
```
The rules are similar:
* No truthiness, the condition must evaluate into a boolean value
* The body MUST be a block-statement (`{ /*...*/ }`)

For beginners, the pattern is like this:
```
find while statement -> check truth of condition
    -> if true, execute the loop's body until the condition is false
    -> otherwise, don't execute
```
You can also add break or continue keywords. Here's an example program:
```Rust
let i = 0;
while i < 10 {
    if i == 5 {
        continue;
    } else if i == 8 {
        break;
    }
    print(i);
}
```
The break keyword exits the loop entirely when it runs and the continue keyword stops the current loop iteration and moves to the next one.

### Type Casting
Before we continue with the rest of this, there's a slight detour we need to make that demonstrates convenience: **Type Casting.**
You can type cast something like this:
```Rust
let a = <int>input("prompt");
```

If it fails to convert the value to the proper type however, it's going to throw an error. This encourages value sanitation/validation.

### Functions
Functions are one of the holy grails of reusable code in Dust.
You define a function using `func`, and you call it by typing its name with parentheses in front. For example:
```swift
func sum(x, y) {
    return x + y;
}

print(sum(10, 20));
```
If you try to call something that isn't a function, for example, a variable, it will throw an error. User-defined functions can return a value using the `return` keyword.

### Arrays
Arrays are basically lists of items. Unlike other languages, you cannot type-annotate an array variable with something like array\[type] (for now). Defining an array looks something like this:
```rust
let arr: array = [10, 20, 30,...];
```
To access an element of an array, you do this:
```rust
arr[index]
```
You can reassign the value at a certain index too, for example:
```rust
arr[index] = 1;
```
There are a few other operations you can perform on them as well, listed in the Arrays section of Standard Library Functions (below).

### Standard Library Functions

<a name="stdlib-funcs-arrays"></a>
#### Arrays:
### ⚠️ WARNING: array functions do NOT perform in-place mutation.
* `push`: Adds an element to an array.<br>
    `push` takes 2 arguments: arr (the array) and value (the value you want to push).<br>
    For example:
    ```rust
    let arr = [10, 20, 30];
    arr = push(arr, 40);
    ```
    It's a little similar to Go, however Go has `append`.
* `remove`: Removes an element at a certain index from an array.<br>
`remove` takes two arguments: arr (the array to remove from) and index (the index of the item to remove).<br>For example:
    ```rust
    let arr = [10, 20, 30];
    arr = remove(arr, 2);
    ```
    Remember, Dust (and most programming languages) have zero-based indexing.
* `insert`: Inserts an element at a certain index in an array.<br>
`insert` takes 3 arguments: arr (the array), index (the index where you want to insert the value) and value (the value you want to insert).<br>
For example:
    ```rust
    let arr = [10, 20, 30];
    arr = insert(arr, 2, 25);
    ```
    Remember zero-indexing.
* `contains`: Checks if an array contains a certain value.<br>
` contains` takes 1 argument, and that is arr (the array to check). It returns a `bool` value.<br>
For example:
    ```rust
    let arr = [10, 20, 30];
    print(contains(arr, 25));
    ```
* `pop`: Gets the last element of an array, stores it and removes it.<br>
`pop` takes 1 argument, and that is arr (the array to pop from). `pop` is the only function of these that performs an in-place mutation.<br>
For example:
    ```rust
    let arr = [10, 20, 30];
    print(pop(arr));
    ```

#### Other Functions
* `range`: Creates a lazy iterator (basically a list that doesn't load until you actually iterate over it).<br>
`range` takes 2 arguments: start (the start of the range) and end (the end of the range).<br>
For example:
    ```rust
    let a = range(10, 15);
    print(a[3]); // will print `14` because 14 is the 4th item in the iterator
    ```
    `range` is NOT inclusive.

<br>

### For Loops
For loops are an easy way to iterate over a list or an iterator. You use them like this:
```rust
for i in iterator {
    // do something
}
```
In each iteration, `i` contains the current value in the iteration. `i` is a constant variable which cannot be modified.

<a name="how-to-run"></a>
## How to Run
### **Step 1:** Make sure you have Python installed.
If you don't have python installed, you can get it from [python.org](https://www.python.org/).
### **Step 2:** Clone the GitHub repository.
```Bash
git clone https://github.com/BasaltDev/Dust
cd dust
```
### **Step 3:** Run Dust
You can run dust using the following command:
```Powershell
python dust.py
```
You can figure out the rest from there.

<a name="license"></a>
## License
Licensed under the [GNU GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.html). The license can be found in [LICENSE](license).

In short, you can use, modify and share this code however you want. However, if you distribute your own version of it, you must keep it open-source and release your changes under the same GPLv3 license.

<a name="disclaimers"></a>
## DISCLAIMERS
* **Work in Progress:** Dust is still under development and not fully stable, expect breaking changes.
* **Not Production-Ready:** Please do not use this language for anything mission-critical. It's an experimental project built for educational purposes and personal interest.
* **Performance:** Due to this language being interpreted (tree-walk) and written in Python, it may not meet too many modern performance standards.