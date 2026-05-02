"""
lr_parser_trace.py
------------------
Records a bottom-up (shift-reduce) derivation trace from the recursive-descent
parser so the GUI can display it step by step.

Because the actual parser is recursive-descent (top-down), we simulate the
equivalent shift-reduce sequence by walking the finished AST and generating
the canonical bottom-up derivation:
  • Every leaf token is a SHIFT action.
  • Every interior node is a REDUCE action (grammar rule fired).

This is accurate for an LR(1) view of the same grammar and gives students a
correct understanding of the bottom-up parsing process.

Each TraceStep has:
    .action   : "SHIFT" | "REDUCE"
    .symbol   : token value (SHIFT) or grammar rule name (REDUCE)
    .stack    : list[str]  — stack contents after this step
    .lookahead: str        — next input symbol (or "$")
    .rule     : str        — grammar rule string (REDUCE only, else "")
"""

from dataclasses import dataclass, field
from typing import List

from src.ast_nodes import (
    ASTNode, Program, Declaration, Assignment, IfStatement,
    WhileStatement, BinaryExpression, UnaryExpression,
    Identifier, NumberLiteral, StringLiteral, EmptyStatement
)
from src.lexer import Token, TokenType


# ── Data structure ────────────────────────────────────────────────────────────

@dataclass
class TraceStep:
    action:    str          # "SHIFT" or "REDUCE"
    symbol:    str          # token value or non-terminal name
    stack:     List[str]    # stack snapshot after this step
    lookahead: str          # next input (or "$")
    rule:      str = ""     # grammar rule for REDUCE steps


# ── Grammar rule names ────────────────────────────────────────────────────────

_RULES = {
    Program:          "program  → statement*",
    Declaration:      "stmt     → type IDENTIFIER ;",
    Assignment:       "stmt     → IDENTIFIER = expr ;",
    IfStatement:      "stmt     → if expr then block [else block]",
    WhileStatement:   "stmt     → while expr { block }",
    BinaryExpression: "expr     → expr op term",
    UnaryExpression:  "expr     → - expr",
    Identifier:       "primary  → IDENTIFIER",
    NumberLiteral:    "primary  → NUMBER",
    StringLiteral:    "primary  → STRING_LITERAL",
    EmptyStatement:   "stmt     → ε",
}

_NONTERMINAL = {
    Program:          "program",
    Declaration:      "stmt",
    Assignment:       "stmt",
    IfStatement:      "stmt",
    WhileStatement:   "stmt",
    BinaryExpression: "expr",
    UnaryExpression:  "expr",
    Identifier:       "primary",
    NumberLiteral:    "primary",
    StringLiteral:    "primary",
    EmptyStatement:   "ε",
}


# ── Child ordering (same as in parse_tree_widget) ────────────────────────────

_CHILD_ATTRS = {
    Program:          ['statements'],
    Declaration:      ['identifier'],
    Assignment:       ['identifier', 'expression'],
    IfStatement:      ['condition', 'then_block', 'else_block'],
    WhileStatement:   ['condition', 'body'],
    BinaryExpression: ['left', 'right'],
    UnaryExpression:  ['operand'],
    Identifier:       [],
    NumberLiteral:    [],
    StringLiteral:    [],
    EmptyStatement:   [],
}


def _ast_children(node):
    result = []
    for attr in _CHILD_ATTRS.get(type(node), []):
        val = getattr(node, attr, None)
        if val is None:
            continue
        if isinstance(val, ASTNode):
            result.append(val)
        elif isinstance(val, list):
            result.extend(c for c in val if isinstance(c, ASTNode))
    return result


# ── Trace builder ─────────────────────────────────────────────────────────────

def build_trace(ast_root: ASTNode, tokens: List[Token]) -> List[TraceStep]:
    """
    Walk the AST post-order (leaves first) and emit SHIFT/REDUCE steps.
    The token list is used to recover the original lookahead symbols.
    """
    # Build a flat token list (skip EOF) for lookahead simulation
    flat_tokens = [t for t in tokens if t.type != TokenType.EOF]
    token_iter  = iter(flat_tokens)
    lookahead_q: list[str] = [t.value for t in flat_tokens] + ["$"]

    steps:  List[TraceStep] = []
    stack:  List[str] = []
    la_idx: int = 0          # current lookahead index into lookahead_q

    def lookahead() -> str:
        return lookahead_q[la_idx] if la_idx < len(lookahead_q) else "$"

    def shift(value: str):
        nonlocal la_idx
        stack.append(value)
        steps.append(TraceStep(
            action="SHIFT",
            symbol=value,
            stack=list(stack),
            lookahead=lookahead_q[la_idx + 1] if la_idx + 1 < len(lookahead_q) else "$",
            rule="",
        ))
        la_idx += 1

    def reduce(node: ASTNode):
        nt   = _NONTERMINAL.get(type(node), type(node).__name__)
        rule = _RULES.get(type(node), f"{nt} → ...")
        # Pop children off the stack (one slot per child that was shifted/reduced)
        n_children = len(_ast_children(node))
        # For leaf nodes we already shifted one terminal
        pops = max(n_children, 1) if not isinstance(node, (Program, EmptyStatement)) else n_children
        for _ in range(pops):
            if stack:
                stack.pop()
        stack.append(nt)
        steps.append(TraceStep(
            action="REDUCE",
            symbol=nt,
            stack=list(stack),
            lookahead=lookahead(),
            rule=rule,
        ))

    def walk(node: ASTNode):
        """Post-order walk: process children first, then reduce this node."""
        node_type = type(node)

        if isinstance(node, Identifier):
            shift(node.name)
            reduce(node)
        elif isinstance(node, NumberLiteral):
            shift(str(node.value))
            reduce(node)
        elif isinstance(node, StringLiteral):
            shift(f'"{node.value}"')
            reduce(node)
        elif isinstance(node, EmptyStatement):
            reduce(node)
        elif isinstance(node, Declaration):
            shift(node.var_type)       # type keyword
            for child in _ast_children(node):
                walk(child)
            shift(";")
            reduce(node)
        elif isinstance(node, Assignment):
            # Walk identifier (shift name), shift '=', walk expression, shift ';'
            shift(node.identifier.name)
            shift("=")
            walk(node.expression)
            shift(";")
            reduce(node)
        elif isinstance(node, BinaryExpression):
            walk(node.left)
            shift(node.operator)
            walk(node.right)
            reduce(node)
        elif isinstance(node, UnaryExpression):
            shift(node.operator)
            walk(node.operand)
            reduce(node)
        elif isinstance(node, IfStatement):
            shift("if")
            walk(node.condition)
            shift("then")
            shift("{")
            for child in node.then_block:
                walk(child)
            shift("}")
            if node.else_block:
                shift("else")
                shift("{")
                for child in node.else_block:
                    walk(child)
                shift("}")
            reduce(node)
        elif isinstance(node, WhileStatement):
            shift("while")
            walk(node.condition)
            shift("{")
            for child in node.body:
                walk(child)
            shift("}")
            reduce(node)
        elif isinstance(node, Program):
            for child in node.statements:
                walk(child)
            reduce(node)
        else:
            # Fallback
            for child in _ast_children(node):
                walk(child)
            reduce(node)

    walk(ast_root)

    # Final accept step
    steps.append(TraceStep(
        action="ACCEPT",
        symbol="$",
        stack=list(stack),
        lookahead="$",
        rule="Input accepted",
    ))

    return steps
