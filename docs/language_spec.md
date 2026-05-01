# Basic Compiler - Language Specification

## Overview

A simple educational compiler for a custom programming language supporting basic arithmetic, variable assignments, and control structures.

## Supported Data Types

| Type | Description | Example |
|------|-------------|---------|
| `int` | Integer values | `int x; x = 42;` |
| `string` | String literals | `string name; name = "hello";` |

## Keywords

- `int` - Integer type declaration
- `string` - String type declaration
- `if` - Conditional statement
- `then` - If branch marker
- `else` - Else branch marker
- `while` - Loop statement

## Operators

### Arithmetic
- `+` - Addition
- `-` - Subtraction (also unary negation)
- `*` - Multiplication
- `/` - Division

### Comparison
- `>` - Greater than
- `<` - Less than
- `=` - Equals (comparison and assignment context)

### Delimiters
- `{` - Block start
- `}` - Block end
- `;` - Statement terminator
- `(` - Expression grouping
- `)` - Expression grouping

## Syntax Rules

1. Every statement ends with a semicolon `;`
2. Blocks are enclosed in curly braces `{ }`
3. Variable declarations must specify type before use
4. String literals are enclosed in double quotes

## Error Types

### Lexical Errors
- Invalid characters
- Unrecognized tokens

### Syntax Errors
- Unexpected tokens
- Missing required tokens
- Invalid expression structure

### Semantic Errors
- Undeclared variable usage
- Type mismatches in assignments
- Duplicate variable declarations in same scope

## Example Programs

See `examples/` directory for sample programs.