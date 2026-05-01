# Basic Compiler

A simple compiler for a custom programming language built in Python.

## Project Structure

```
basic-compiler/
├── src/
│   ├── __init__.py
│   ├── ast_nodes.py          # AST node definitions
│   ├── compiler.py           # Main compiler interface
│   ├── error_handler.py      # Error reporting
│   ├── lexer.py              # Lexical analyzer (Milestone 1)
│   ├── parser.py             # Syntax analyzer (Milestone 2)
│   ├── semantic_analyzer.py  # Semantic analyzer (Milestone 3)
│   └── symbol_table.py       # Symbol table implementation
├── gui/
│   ├── tabs/                 # Individual GUI tabs
│   ├── widgets/              # Reusable GUI widgets
│   ├── syntax_highlighter.py # Code editor highlighting
│   ├── main_window.py        # Main GUI window assembly
│   └── __init__.py
├── tests/
│   ├── test_compiler.py      # Unit tests
│   └── test_programs/
│       ├── valid/            # Valid test programs
│       └── invalid/          # Invalid programs for error testing
├── examples/
│   ├── calculator.src
│   └── conditional_logic.src
├── docs/
│   ├── grammar.md
│   └── language_spec.md
├── requirements.txt
├── main.py                   # Main entry point (launches GUI)
└── README.md
```

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Interactive GUI

To launch the compiler's interactive visualization tool:

```bash
python main.py
```

The GUI provides:
- **Lexer Tab**: View token stream with source code highlighting
- **Parser Tab**: Interactive parse tree (AST) visualization
- **Semantic Analyzer Tab**: Symbol table and type checking results
- **Pipeline Tab**: Complete compilation pipeline visualization
- **Example Templates**: Pre-loaded examples from the PDF and test cases

## Language Features

- **Data Types**: `int`, `string`
- **Arithmetic**: `+`, `-`, `*`, `/`
- **Comparison**: `>`, `<`, `=`
- **Control Flow**: `if-then-else`
- **Variable Declarations**: `int x;`, `string name;`

## Example Code

```python
int a;
int b;
int result;

a = 10;
b = 5;

if a > b then {
    result = a - b;
} else {
    result = b - a;
}
```

## Running Tests

```bash
python tests/test_compiler.py
```

## Milestones

1. **Lexical Analysis (Lexer)** - Converts source code into tokens
2. **Syntax Analysis (Parser)** - Builds Abstract Syntax Tree (AST)
3. **Semantic Analysis** - Type checking and scope resolution

## Requirements

- Python 3.12+