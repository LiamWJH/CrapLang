# CrapLang

CrapLang is a minimalist scripting language implemented in Python, built without parser generators like PLY or Lark—just pure determination. Its syntax is designed to be simple and intuitive for basic scripting tasks.

---

## Table of Contents

1. [Syntax Overview](#syntax-overview)
2. [Statements](#statements)
   - [print](#print)
   - [let](#let)
   - [input](#input)
   - [comment](#comment)
   - [if / end](#if--end)
   - [while / end](#while--end)
   - [fnc / end](#fnc--end)
   - [output](#output)
   - [push / pop](#push--pop)
   - [have / slice](#have--slice)
   - [readfile / writefile / appendfile](#readfile--writefile--appendfile)
   - [rickroll](#rickroll)

---

## Syntax Overview

CrapLang programs consist of lines of tokens separated by whitespace. Blocks (for `if`, `while`, `fnc`) are closed by `end`. String literals use double quotes. Arithmetic and comparison use infix operators.

---

## Statements

### `print`

Outputs the evaluated expression to stdout.

```crap
print "Hello, world"
print 1234
print 1 + 1
print variableName
```

### `let`

Declares or reassigns a variable.

```crap
let stringVar = "Hi"
let numVar    = 144
let sumVar    = 1 + 2
let listVar   = [1,2,3,4]
let otherVar  = numVar + 2
```

### `input`

Prompts the user and stores their input.

```crap
input drink "What drink would you want?"
input sum   1 + 1
```

### `comment:`

A single-line comment. Everything after `comment:` is ignored.

```crap
comment: This is just a note
```

### `if` / `end`

Conditional execution.

```crap
if x < 10
    print "x is less than 10"
end
```

### `while` / `end`

Loop while the condition is true.

```crap
while i < 5
    print i
    let i = i + 1
end
```

### `fnc` / `end`

Defines a function.  Call with `call` prefix.

```crap
fnc sayhi name
    print "Hi, "
    print name
    print "!"
end

call sayhi "Alice"
```

### `output`

Assigns a value from inside a function back to an outer variable.

```crap
let result = 0

fnc compute
    let temp = 42
    output result temp
end

call compute
print result   # prints 42
```

### `push` / `pop`

Manipulate lists.

```crap
let arr = [1,2,3]
push arr 4      # arr is now [1,2,3,4]
pop arr 1       # removes element at index 1 (value 2)
```

### `have` / `slice`

Import the string library to slice strings.

```crap
have string
let s = "abcdef"
slice s 1 4    # s becomes "bcd"
print s
```

### `readfile` / `writefile` / `appendfile`

Import file I/O support with `have fileio`.

```crap
have fileio
let content = ""

readfile  "notes.txt" content
print content

writefile "notes.txt" "Hello!"
readfile  "notes.txt" content
print content  # Hello!

appendfile "notes.txt" " Goodbye!"
readfile  "notes.txt" content
print content  # Hello! Goodbye!
```

### `rickroll`

Yes

```crap
have rick
rickroll
```

---

*Enjoy scripting with CrapLang!*

