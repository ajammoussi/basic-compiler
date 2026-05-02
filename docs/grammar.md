# Basic Compiler - Language Grammar

## Language Definition

The language supports:
- Variable declarations (`int` and `string` types)
- Variable assignments
- Arithmetic expressions (+, -, *, /)
- Comparison operators (>, <, =)
- If-then-else control flow
- While loops

## Grammar Rules

```
<program>       ::= <statement_list>
<statement_list>::= <statement> | <statement> <statement_list>
<statement>     ::= <declaration> | <assignment> | <if_statement> | <while_statement>
<declaration>   ::= <type> <identifier> ;
<type>          ::= 'int' | 'string'
<assignment>    ::= <identifier> = <expression> ;
<if_statement>  ::= 'if' <expression> 'then' '{' <statement_list> '}'
                  | 'if' <expression> 'then' '{' <statement_list> '}' 'else' '{' <statement_list> '}'
<while_statement>::= 'while' <expression> '{' <statement_list> '}'
<expression>    ::= <comparison>
<comparison>    ::= <addition> (('>' | '<' | '=') <addition>)*
<addition>      ::= <multiplication> (('+' | '-') <multiplication>)*
<multiplication>::= <unary> (('*' | '/') <unary>)*
<unary>         ::= '-' <unary> | <primary>
<primary>       ::= <identifier> | <number> | <string_literal> | '(' <expression> ')'
```

## Example Programs

### Simple Assignment
```
int x;
x = 5 + 2;
```

### Conditional
```
if x > 3 then {
    y = 1;
} else {
    y = 2;
}
```

### Arithmetic
```
int result;
result = a * (b + c) - d / 2;
```

### While Loop
```
int x;
x = 10;
while x > 0 {
    x = x - 1;
}
```