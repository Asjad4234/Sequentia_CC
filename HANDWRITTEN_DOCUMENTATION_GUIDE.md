# Sequentia Compiler - Handwritten Documentation Guide

This document outlines all the handwritten components required for the Sequentia compiler project, organized by compiler phases.

---

## Table of Contents
1. [Language Specification](#1-language-specification)
2. [Lexical Analysis](#2-lexical-analysis)
3. [Syntax Analysis](#3-syntax-analysis)
4. [Semantic Analysis](#4-semantic-analysis)
5. [Intermediate Code Generation](#5-intermediate-code-generation)
6. [Code Optimization](#6-code-optimization)
7. [Example Programs](#7-example-programs)
8. [Complete Compilation Example](#8-complete-compilation-example)

---

## 1. Language Specification

### 1.1 Data Types
Document the following data types:

```
Data Types in Sequentia:
┌─────────────┬────────────────────────────────┐
│ Type        │ Description                     │
├─────────────┼────────────────────────────────┤
│ int         │ Integer values (e.g., 5, 42)   │
│ array       │ Sequence of integers            │
└─────────────┴────────────────────────────────┘
```

**To Document:**
- Type hierarchy diagram
- Type compatibility rules
- Implicit type conversions (broadcast operations)

### 1.2 Language Features

**Variables:**
```
Syntax: identifier = expression
Example: x = 5
         arr = pattern fibonacci 10
```

**Operators:**
```
Arithmetic: +, -, *, /
Comparison: ==, !=, <, >, <=, >=
```

**Control Structures:**
```
If-Else: if condition { ... } else { ... }
For Loop: for variable in array { ... }
```

**Functions (Patterns):**
```
pattern fibonacci N
pattern factorial N
pattern square N
pattern cube N
pattern triangular N
pattern arithmetic START, STEP, N
pattern geometric START, RATIO, N
```

---

## 2. Lexical Analysis

### 2.1 Lexical Rules (Token Specification)

**Document these token categories:**

#### **Keywords:**
```
KEYWORDS = {
    pattern, print, if, else, for, in,
    fibonacci, factorial, square, cube,
    triangular, arithmetic, geometric
}
```

#### **Identifiers:**
```
Regex: [a-zA-Z_][a-zA-Z0-9_]*
Examples: x, count, fib_array, myVar123
```

#### **Numbers:**
```
Regex: [0-9]+
Examples: 0, 42, 1000
```

#### **Operators:**
```
Single: +, -, *, /, =, <, >
Double: ==, !=, <=, >=
```

#### **Delimiters:**
```
{, }, [, ], (, ), :, ,
```

#### **Comments:**
```
# single line comment (ignored by lexer)
```

### 2.2 Transition DFA

**Draw DFAs for:**

#### DFA 1: Identifier Recognition
```
State Diagram:
    [a-zA-Z_]        [a-zA-Z0-9_]
(S0) ────────→ (S1) ←──────────┐
                 │              │
                 └──────────────┘
               (accepting state)

S0: Start state
S1: Identifier recognized (accepting)

Transitions:
- S0 → S1 on [a-zA-Z_]
- S1 → S1 on [a-zA-Z0-9_]
- S1 is accepting state
```

#### DFA 2: Number Recognition
```
State Diagram:
         [0-9]        [0-9]
(S0) ────────→ (S1) ←──────┐
                 │         │
                 └─────────┘
            (accepting state)

Transitions:
- S0 → S1 on [0-9]
- S1 → S1 on [0-9]
- S1 is accepting state
```

#### DFA 3: Operator Recognition (== vs =)
```
State Diagram:
         =           =
(S0) ────────→ (S1) ────────→ (S2)
           (accept: =)     (accept: ==)

Transitions:
- S0 → S1 on '='
- S1 → S2 on '=' (if next char is '=')
- S1 is accepting for ASSIGN token
- S2 is accepting for EQ token
```

#### DFA 4: Comment Recognition
```
State Diagram:
         #           [^\n]
(S0) ────────→ (S1) ←──────┐
                 │         │
                 └─────────┘
                 \n ↓
                  (S2)
            (accept: ignore)
```

### 2.3 Lexical Analysis Table

**Create a table showing tokenization:**

```
Source Code: x = pattern fibonacci 5

┌──────────────┬──────────┬─────────────┐
│ Lexeme       │ Token    │ Attribute   │
├──────────────┼──────────┼─────────────┤
│ x            │ ID       │ "x"         │
│ =            │ ASSIGN   │ -           │
│ pattern      │ PATTERN  │ -           │
│ fibonacci    │ FIB_KW   │ -           │
│ 5            │ NUMBER   │ 5           │
└──────────────┴──────────┴─────────────┘
```

---

## 3. Syntax Analysis

### 3.1 Context-Free Grammar (BNF)

**Write the complete BNF grammar:**

```bnf
<program>       ::= <statement-list>

<statement-list> ::= <statement> | <statement> <statement-list>

<statement>     ::= <assignment>
                  | <print-stmt>
                  | <if-stmt>
                  | <for-stmt>

<assignment>    ::= ID '=' <expression>

<print-stmt>    ::= 'print' <expression>

<if-stmt>       ::= 'if' <expression> '{' <statement-list> '}'
                  | 'if' <expression> '{' <statement-list> '}' 'else' '{' <statement-list> '}'

<for-stmt>      ::= 'for' ID 'in' <expression> '{' <statement-list> '}'

<expression>    ::= <comparison>

<comparison>    ::= <additive> | <additive> <comp-op> <additive>

<comp-op>       ::= '==' | '!=' | '<' | '>' | '<=' | '>='

<additive>      ::= <multiplicative>
                  | <additive> '+' <multiplicative>
                  | <additive> '-' <multiplicative>

<multiplicative> ::= <primary>
                   | <multiplicative> '*' <primary>
                   | <multiplicative> '/' <primary>

<primary>       ::= NUMBER
                  | ID
                  | ID '[' <expression> ']'
                  | ID '[' <slice> ']'
                  | 'pattern' <pattern-type> <arg-list>
                  | '(' <expression> ')'

<slice>         ::= <expression> ':' <expression>
                  | ':' <expression>
                  | <expression> ':'

<pattern-type>  ::= 'fibonacci' | 'factorial' | 'square' | 'cube' 
                  | 'triangular' | 'arithmetic' | 'geometric'

<arg-list>      ::= <expression> | <expression> ',' <arg-list>
```

### 3.2 Extended BNF (EBNF)

**Write the same grammar in EBNF notation:**

```ebnf
program       = statement+ ;

statement     = assignment
              | print-stmt
              | if-stmt
              | for-stmt ;

assignment    = ID '=' expression ;

print-stmt    = 'print' expression ;

if-stmt       = 'if' expression '{' statement+ '}' 
                ['else' '{' statement+ '}'] ;

for-stmt      = 'for' ID 'in' expression '{' statement+ '}' ;

expression    = comparison ;

comparison    = additive [comp-op additive] ;

comp-op       = '==' | '!=' | '<' | '>' | '<=' | '>=' ;

additive      = multiplicative {('+' | '-') multiplicative} ;

multiplicative = primary {('*' | '/') primary} ;

primary       = NUMBER
              | ID
              | ID '[' expression ']'
              | ID '[' [expression] ':' [expression] ']'
              | 'pattern' pattern-type arg-list
              | '(' expression ')' ;

pattern-type  = 'fibonacci' | 'factorial' | 'square' | 'cube' 
              | 'triangular' | 'arithmetic' | 'geometric' ;

arg-list      = expression {',' expression} ;
```

### 3.3 Top-Down Parsing (LL(1))

#### 3.3.1 FIRST and FOLLOW Sets

**Calculate and document:**

```
FIRST Sets:
───────────────────────────────────────────────────
FIRST(program)       = {ID, print, if, for}
FIRST(statement)     = {ID, print, if, for}
FIRST(assignment)    = {ID}
FIRST(print-stmt)    = {print}
FIRST(if-stmt)       = {if}
FIRST(for-stmt)      = {for}
FIRST(expression)    = {NUMBER, ID, pattern, (}
FIRST(comparison)    = {NUMBER, ID, pattern, (}
FIRST(additive)      = {NUMBER, ID, pattern, (}
FIRST(multiplicative)= {NUMBER, ID, pattern, (}
FIRST(primary)       = {NUMBER, ID, pattern, (}

FOLLOW Sets:
───────────────────────────────────────────────────
FOLLOW(program)      = {$}
FOLLOW(statement)    = {ID, print, if, for, }, $}
FOLLOW(expression)   = {), ], ',', {, NEWLINE}
FOLLOW(additive)     = {==, !=, <, >, <=, >=, ), ], ',', {, NEWLINE}
FOLLOW(multiplicative)= {+, -, ==, !=, <, >, <=, >=, ), ], ',', {, NEWLINE}
FOLLOW(primary)      = {*, /, +, -, ==, !=, <, >, <=, >=, ), ], ',', {, NEWLINE}
```

#### 3.3.2 LL(1) Parsing Table

**Create the parsing table:**

```
LL(1) Parsing Table:
═══════════════════════════════════════════════════════════════════
Non-terminal │ ID      │ NUMBER  │ pattern │ print │ if    │ for   │
─────────────┼─────────┼─────────┼─────────┼───────┼───────┼───────┤
program      │ S→S+    │         │         │ S→S+  │ S→S+  │ S→S+  │
statement    │ A       │         │         │ P     │ I     │ F     │
assignment   │ ID=E    │         │         │       │       │       │
expression   │ E→C     │ E→C     │ E→C     │       │       │       │
primary      │ ID...   │ NUM     │ pattern │       │       │       │
═══════════════════════════════════════════════════════════════════

Legend:
S = statement, A = assignment, P = print-stmt, 
I = if-stmt, F = for-stmt, E = expression, C = comparison
```

#### 3.3.3 LL(1) Parse Tree Example

**Draw parse tree for: `x = 5 + 3`**

```
                    program
                       │
                   statement
                       │
                  assignment
                 /     |     \
               ID      =    expression
              (x)            │
                        comparison
                            │
                        additive
                      /    |    \
                 additive  +  multiplicative
                    │              │
              multiplicative    primary
                    │              │
                 primary        NUMBER
                    │             (3)
                 NUMBER
                   (5)
```

### 3.4 Bottom-Up Parsing

#### 3.4.1 LR(0) Items and Automaton

**Write LR(0) items for a simplified grammar:**

```
Simplified Grammar:
E → E + T
E → T
T → T * F
T → F
F → ( E )
F → id

LR(0) Items:
────────────────────────────
I0: E' → •E
    E → •E + T
    E → •T
    T → •T * F
    T → •F
    F → •( E )
    F → •id

I1: E' → E•
    E → E• + T

I2: E → T•
    T → T• * F

I3: T → F•

I4: F → ( •E )
    E → •E + T
    E → •T
    ...

I5: F → id•

I6: E → E + •T
    T → •T * F
    T → •F
    ...

I7: T → T * •F
    F → •( E )
    F → •id

I8: F → ( E• )
    E → E• + T

I9: F → ( E )•

I10: E → E + T•
     T → T• * F

I11: T → T * F•
```

**Draw LR(0) Automaton:**

```
    E         T         F        (        id
I0 ──→ I1  I0 ──→ I2  I0 ──→ I3  I0 ──→ I4  I0 ──→ I5
       │          │          │
       +          *          
       ↓          ↓          
      I6         I7         

(Continue for all states...)
```

#### 3.4.2 SLR(1) Parsing Table

**Create SLR(1) parsing table:**

```
SLR(1) Parsing Table:
════════════════════════════════════════════════════════════
State │ id  │  +  │  *  │  (  │  )  │  $  │  E  │  T  │  F  │
──────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
  0   │ s5  │     │     │ s4  │     │     │  1  │  2  │  3  │
  1   │     │ s6  │     │     │     │ acc │     │     │     │
  2   │     │ r2  │ s7  │     │ r2  │ r2  │     │     │     │
  3   │     │ r4  │ r4  │     │ r4  │ r4  │     │     │     │
  4   │ s5  │     │     │ s4  │     │     │  8  │  2  │  3  │
  5   │     │ r6  │ r6  │     │ r6  │ r6  │     │     │     │
  6   │ s5  │     │     │ s4  │     │     │     │ 10  │  3  │
  7   │ s5  │     │     │ s4  │     │     │     │     │ 11  │
  8   │     │ s6  │     │     │ s9  │     │     │     │     │
  9   │     │ r5  │ r5  │     │ r5  │ r5  │     │     │     │
 10   │     │ r1  │ s7  │     │ r1  │ r1  │     │     │     │
 11   │     │ r3  │ r3  │     │ r3  │ r3  │     │     │     │
════════════════════════════════════════════════════════════

s = shift, r = reduce, acc = accept
```

#### 3.4.3 CLR(1) Items

**Document CLR(1) items with lookaheads:**

```
CLR(1) Items (with lookaheads):
─────────────────────────────────────
I0: [E' → •E, $]
    [E → •E + T, +/$]
    [E → •T, +/$]
    [T → •T * F, +/*/$ ]
    [T → •F, +/*/$ ]
    [F → •( E ), +/*/$ ]
    [F → •id, +/*/$ ]

I1: [E' → E•, $]
    [E → E• + T, +/$]

I2: [E → T•, +/$]
    [T → T• * F, +/*/$ ]

(Continue for all states with lookaheads...)
```

#### 3.4.4 LALR(1) Construction

**Show LALR(1) state merging:**

```
LALR(1) State Merging:
──────────────────────────────────────
Merge CLR(1) states with same core:

CLR States → LALR States
I0 → I0 (no merge)
I1 → I1 (no merge)
I2, I2' → I2 (merged - same core, different lookaheads)
I3, I3' → I3 (merged)
...

LALR(1) has fewer states than CLR(1) 
but more powerful than SLR(1)
```

#### 3.4.5 Parse Example with Bottom-Up

**Show shift-reduce parsing for: `id + id * id`**

```
Bottom-Up Parse (SLR):
════════════════════════════════════════════════════════════
Stack              │ Input           │ Action
───────────────────┼─────────────────┼─────────────────────
0                  │ id + id * id $  │ shift 5
0 id 5             │ + id * id $     │ reduce F → id
0 F 3              │ + id * id $     │ reduce T → F
0 T 2              │ + id * id $     │ reduce E → T
0 E 1              │ + id * id $     │ shift 6
0 E 1 + 6          │ id * id $       │ shift 5
0 E 1 + 6 id 5     │ * id $          │ reduce F → id
0 E 1 + 6 F 3      │ * id $          │ reduce T → F
0 E 1 + 6 T 10     │ * id $          │ shift 7
0 E 1 + 6 T 10 * 7 │ id $            │ shift 5
...                │ ...             │ ...
0 E 1              │ $               │ accept
════════════════════════════════════════════════════════════
```

---

## 4. Semantic Analysis

### 4.1 Type System and Rules

**Document type checking rules:**

```
Type System Rules:
═══════════════════════════════════════════════════════════

1. Variable Declaration:
   ─────────────────────────────────────────
   x : int ⊢ x = 5 : int
   
   arr : array ⊢ arr = pattern fibonacci 10 : array

2. Arithmetic Operations:
   ─────────────────────────────────────────
   e1 : int    e2 : int
   ────────────────────────
   e1 + e2 : int
   
   e1 : array    e2 : array
   ──────────────────────────── (element-wise)
   e1 + e2 : array
   
   e1 : array    e2 : int
   ──────────────────────────── (broadcast)
   e1 * e2 : array
   
   e1 : int    e2 : array
   ──────────────────────────── (broadcast)
   e1 + e2 : array

3. Comparison Operations:
   ─────────────────────────────────────────
   e1 : int    e2 : int
   ────────────────────────
   e1 == e2 : int (boolean result)

4. Array Access:
   ─────────────────────────────────────────
   arr : array    i : int
   ──────────────────────────
   arr[i] : int

5. Slicing:
   ─────────────────────────────────────────
   arr : array    start : int    end : int
   ──────────────────────────────────────────
   arr[start:end] : array

6. Pattern Functions:
   ─────────────────────────────────────────
   n : int
   ──────────────────────────
   pattern fibonacci n : array

7. Control Flow:
   ─────────────────────────────────────────
   condition : int    stmt1 : void
   ──────────────────────────────────────
   if condition { stmt1 } : void
   
   arr : array    body : void
   ──────────────────────────────────────
   for x in arr { body } : void
```

### 4.2 Symbol Table Structure

**Design symbol table entries:**

```
Symbol Table Entry Structure:
═══════════════════════════════════════════════════════════
┌──────────┬──────┬────────┬────────┬────────────────────┐
│ Name     │ Type │ Scope  │ Offset │ Additional Info    │
├──────────┼──────┼────────┼────────┼────────────────────┤
│ x        │ int  │ global │ 0      │ -                  │
│ fib      │ array│ global │ 4      │ length: dynamic    │
│ count    │ int  │ local  │ 8      │ function: main     │
│ val      │ int  │ local  │ 12     │ loop iterator      │
└──────────┴──────┴────────┴────────┴────────────────────┘
```

### 4.3 Symbol Table Example

**Show symbol table for a complete program:**

```
Program:
────────
n = 5
fib = pattern fibonacci n
for val in fib {
    if val > 3 {
        print val
    }
}

Symbol Table After Semantic Analysis:
═══════════════════════════════════════════════════════════
Scope: GLOBAL
┌──────────┬──────┬─────────┬──────────────────────────┐
│ Name     │ Type │ Line    │ Additional Info           │
├──────────┼──────┼─────────┼──────────────────────────┤
│ n        │ int  │ 1       │ assigned value: 5         │
│ fib      │ array│ 2       │ pattern: fibonacci        │
│          │      │         │ length: depends on n      │
└──────────┴──────┴─────────┴──────────────────────────┘

Scope: FOR_LOOP (lines 3-7)
┌──────────┬──────┬─────────┬──────────────────────────┐
│ Name     │ Type │ Line    │ Additional Info           │
├──────────┼──────┼─────────┼──────────────────────────┤
│ val      │ int  │ 3       │ iterator variable         │
│          │      │         │ source: fib               │
└──────────┴──────┴─────────┴──────────────────────────┘

Scope: IF_BLOCK (lines 4-6)
┌──────────┬──────┬─────────┬──────────────────────────┐
│ Name     │ Type │ Line    │ Additional Info           │
├──────────┼──────┼─────────┼──────────────────────────┤
│ (none)   │ -    │ -       │ uses parent scope vars    │
└──────────┴──────┴─────────┴──────────────────────────┘
```

### 4.4 Semantic Error Examples

**Document common semantic errors:**

```
Semantic Errors to Detect:
═══════════════════════════════════════════════════════════

1. Undefined Variable:
   ─────────────────────────────────────────
   Source: print x
   Error: Variable 'x' is not defined
   Line: 1

2. Type Mismatch:
   ─────────────────────────────────────────
   Source: arr = pattern fibonacci 5
           y = arr + "string"
   Error: Cannot perform '+' between array and string
   Line: 2

3. Invalid Array Index:
   ─────────────────────────────────────────
   Source: arr = pattern square 5
           x = arr[arr]
   Error: Array index must be of type int, not array
   Line: 2

4. Invalid Loop Source:
   ─────────────────────────────────────────
   Source: x = 5
           for i in x { ... }
   Error: For loop source must be an array, not int
   Line: 2

5. Wrong Number of Arguments:
   ─────────────────────────────────────────
   Source: arr = pattern fibonacci 5, 10
   Error: fibonacci pattern expects 1 argument, got 2
   Line: 1
```

---

## 5. Intermediate Code Generation

### 5.1 Three-Address Code (TAC)

**Generate TAC for expressions:**

#### Example 1: Simple Arithmetic
```
Source: x = 5 + 3 * 2

Three-Address Code:
───────────────────────────────
t1 = 3 * 2
t2 = 5 + t1
x = t2
───────────────────────────────
```

#### Example 2: Array Operations
```
Source: fib = pattern fibonacci 5
        doubled = fib * 2

Three-Address Code:
───────────────────────────────
t1 = call fibonacci, 5
fib = t1
t2 = _pat_mul(fib, 2)
doubled = t2
───────────────────────────────
```

#### Example 3: Conditional
```
Source: if x > 5 {
            print x
        } else {
            print 0
        }

Three-Address Code:
───────────────────────────────
    t1 = x > 5
    ifFalse t1 goto L1
    print x
    goto L2
L1: print 0
L2: (continue)
───────────────────────────────
```

#### Example 4: For Loop
```
Source: for val in fib {
            print val
        }

Three-Address Code:
───────────────────────────────
    t1 = len(fib)
    i = 0
L1: if i >= t1 goto L2
    val = fib[i]
    print val
    i = i + 1
    goto L1
L2: (continue)
───────────────────────────────
```

### 5.2 Quadruples

**Generate quadruples representation:**

```
Expression: x = (a + b) * (c - d)

Quadruples:
═══════════════════════════════════════════════════════════
Index │ Operator │ Arg1 │ Arg2 │ Result │
──────┼──────────┼──────┼──────┼────────┤
 0    │    +     │  a   │  b   │   t1   │
 1    │    -     │  c   │  d   │   t2   │
 2    │    *     │  t1  │  t2  │   t3   │
 3    │    =     │  t3  │      │   x    │
═══════════════════════════════════════════════════════════
```

### 5.3 Triples

**Generate triples representation:**

```
Expression: x = (a + b) * (c - d)

Triples:
═══════════════════════════════════════════════════
Index │ Operator │ Arg1 │ Arg2 │
──────┼──────────┼──────┼──────┤
 0    │    +     │  a   │  b   │
 1    │    -     │  c   │  d   │
 2    │    *     │ (0)  │ (1)  │
 3    │    =     │  x   │ (2)  │
═══════════════════════════════════════════════════

Note: (0), (1), (2) refer to result of operation at that index
```

### 5.4 Indirect Triples

**Generate indirect triples:**

```
Expression: x = (a + b) * (c - d)

Statement List:
──────────────
(0) | (1) | (2) | (3)

Triples:
═══════════════════════════════════════════════════
Index │ Operator │ Arg1 │ Arg2 │
──────┼──────────┼──────┼──────┤
 0    │    +     │  a   │  b   │
 1    │    -     │  c   │  d   │
 2    │    *     │ (0)  │ (1)  │
 3    │    =     │  x   │ (2)  │
═══════════════════════════════════════════════════
```

---

## 6. Code Optimization

### 6.1 Constant Folding

**Show optimization examples:**

```
Before Optimization:
────────────────────────────────
x = 2 + 3
y = x * 4
z = 10 / 2

TAC:
t1 = 2 + 3
x = t1
t2 = x * 4
y = t2
t3 = 10 / 2
z = t3

After Constant Folding:
────────────────────────────────
x = 5
y = x * 4
z = 5

TAC:
x = 5
t2 = x * 4
y = t2
z = 5
```

### 6.2 Constant Propagation

```
Before:
────────────────────────────────
x = 5
y = x + 3
z = x * 2

After Constant Propagation:
────────────────────────────────
x = 5
y = 5 + 3
z = 5 * 2

After Constant Folding:
────────────────────────────────
x = 5
y = 8
z = 10
```

### 6.3 Dead Code Elimination

```
Before:
────────────────────────────────
x = 5
y = x + 3      # y is never used
z = x * 2
print z

After Dead Code Elimination:
────────────────────────────────
x = 5
z = x * 2
print z

Analysis: Variable 'y' is assigned but never read
```

### 6.4 Common Subexpression Elimination

```
Before:
────────────────────────────────
t1 = a + b
x = t1 * c
t2 = a + b      # same as t1
y = t2 * d

After CSE:
────────────────────────────────
t1 = a + b
x = t1 * c
y = t1 * d      # reuse t1

Savings: One addition operation eliminated
```

### 6.5 Loop Optimization

**Loop Invariant Code Motion:**

```
Before:
────────────────────────────────
for i in range(10) {
    x = a + b      # invariant
    arr[i] = x * i
}

After:
────────────────────────────────
x = a + b          # moved outside loop
for i in range(10) {
    arr[i] = x * i
}

Benefit: Calculation performed once instead of 10 times
```

### 6.6 Strength Reduction

```
Before:
────────────────────────────────
for i in range(10) {
    x = i * 4
}

After Strength Reduction:
────────────────────────────────
x = 0
for i in range(10) {
    x = x + 4      # addition instead of multiplication
}

Benefit: Addition is faster than multiplication
```

---

## 7. Example Programs

### 7.1 Example Program 1: Fibonacci Processing

**Complete compilation example:**

```
Source Code:
════════════════════════════════════════════════════════════
# Generate and process Fibonacci sequence
n = 10
fib = pattern fibonacci n
doubled = fib * 2
print doubled
════════════════════════════════════════════════════════════
```

**Lexical Analysis:**
```
Tokens:
┌───────────┬──────────┬──────────┐
│ Lexeme    │ Token    │ Line     │
├───────────┼──────────┼──────────┤
│ n         │ ID       │ 2        │
│ =         │ ASSIGN   │ 2        │
│ 10        │ NUMBER   │ 2        │
│ fib       │ ID       │ 3        │
│ =         │ ASSIGN   │ 3        │
│ pattern   │ PATTERN  │ 3        │
│ fibonacci │ FIB_KW   │ 3        │
│ n         │ ID       │ 3        │
│ doubled   │ ID       │ 4        │
│ =         │ ASSIGN   │ 4        │
│ fib       │ ID       │ 4        │
│ *         │ STAR     │ 4        │
│ 2         │ NUMBER   │ 4        │
│ print     │ PRINT    │ 5        │
│ doubled   │ ID       │ 5        │
└───────────┴──────────┴──────────┘
```

**Syntax Analysis (Parse Tree):**
```
Draw the complete parse tree showing:
- program node
- statement nodes for each line
- expression trees
```

**Semantic Analysis (Symbol Table):**
```
═══════════════════════════════════════════════════════════
│ Name    │ Type  │ Line │ Info                          │
├─────────┼───────┼──────┼───────────────────────────────┤
│ n       │ int   │ 2    │ value: 10                     │
│ fib     │ array │ 3    │ pattern: fibonacci, size: 10  │
│ doubled │ array │ 4    │ from vector operation         │
═══════════════════════════════════════════════════════════
```

**Intermediate Code (TAC):**
```
───────────────────────────────
n = 10
t1 = call fibonacci, n
fib = t1
t2 = _pat_mul(fib, 2)
doubled = t2
print doubled
───────────────────────────────
```

**Optimized Code:**
```
───────────────────────────────
n = 10
fib = call fibonacci, 10
doubled = _pat_mul(fib, 2)
print doubled
───────────────────────────────
```

**Generated Python Code:**
```python
n = 10
def _gen_fib():
    a, b = 0, 1
    arr = []
    for _ in range(n):
        arr.append(a)
        a, b = b, a+b
    return arr
fib = _gen_fib()
doubled = _pat_mul(fib, 2)
print(doubled if isinstance(doubled, int) else ' '.join(str(x) for x in doubled))
```

### 7.2 Example Program 2: Conditional Loop

**Complete compilation example:**

```
Source Code:
════════════════════════════════════════════════════════════
# Filter values using loop and conditional
nums = pattern square 10
for val in nums {
    if val > 25 {
        print val
    }
}
════════════════════════════════════════════════════════════
```

**Lexical Analysis:**
```
Tokens:
┌───────────┬──────────┬──────────┐
│ Lexeme    │ Token    │ Line     │
├───────────┼──────────┼──────────┤
│ nums      │ ID       │ 2        │
│ =         │ ASSIGN   │ 2        │
│ pattern   │ PATTERN  │ 2        │
│ square    │ SQUARE   │ 2        │
│ 10        │ NUMBER   │ 2        │
│ for       │ FOR      │ 3        │
│ val       │ ID       │ 3        │
│ in        │ IN       │ 3        │
│ nums      │ ID       │ 3        │
│ {         │ LBRACE   │ 3        │
│ if        │ IF       │ 4        │
│ val       │ ID       │ 4        │
│ >         │ GT       │ 4        │
│ 25        │ NUMBER   │ 4        │
│ {         │ LBRACE   │ 4        │
│ print     │ PRINT    │ 5        │
│ val       │ ID       │ 5        │
│ }         │ RBRACE   │ 6        │
│ }         │ RBRACE   │ 7        │
└───────────┴──────────┴──────────┘
```

**Syntax Analysis (Parse Tree):**
```
                    program
                       │
                  statement-list
                    /      \
              statement   statement
                 │           │
            assignment    for-stmt
           /    |    \      /  |  \  \
        ID     =    expr   for ID in expr block
      (nums)          │         (val) (nums)  │
                   pattern                  if-stmt
                    /  \                    /  |  \
                square  10               if expr block
                                           /  |  \
                                        val  >  25
```

**Semantic Analysis (Symbol Table):**
```
═══════════════════════════════════════════════════════════
Scope: GLOBAL
│ Name    │ Type  │ Line │ Info                          │
├─────────┼───────┼──────┼───────────────────────────────┤
│ nums    │ array │ 2    │ pattern: square, size: 10     │
═══════════════════════════════════════════════════════════

Scope: FOR_LOOP
│ Name    │ Type  │ Line │ Info                          │
├─────────┼───────┼──────┼───────────────────────────────┤
│ val     │ int   │ 3    │ iterator, source: nums        │
═══════════════════════════════════════════════════════════
```

**Intermediate Code (TAC):**
```
───────────────────────────────
nums = call square, 10
t1 = len(nums)
i = 0
L1: if i >= t1 goto L3
    val = nums[i]
    t2 = val > 25
    ifFalse t2 goto L2
    print val
L2: i = i + 1
    goto L1
L3: (end)
───────────────────────────────
```

**Optimized Code:**
```
Same as above (no optimization opportunities)
```

**Generated Python Code:**
```python
nums = [(i+1)**2 for i in range(10)]
for val in nums:
    if (val > 25):
        print(val if isinstance(val, int) else ' '.join(str(x) for x in val))
```

---

## 8. Complete Compilation Example

### 8.1 Complex Program

```
Source Code:
════════════════════════════════════════════════════════════
# Complex program with multiple features
n = 5
fib = pattern fibonacci n
squares = pattern square n
combined = fib + squares
middle = combined[1:4]

for val in middle {
    doubled = val * 2
    if doubled > 10 {
        print doubled
    } else {
        print val
    }
}
════════════════════════════════════════════════════════════
```

### Document the following for this program:

1. **Complete Token Stream**
2. **Full Parse Tree** (can be large - show key sections)
3. **Symbol Table at Each Scope**
4. **Complete TAC**
5. **Optimization Steps**
6. **Final Generated Code**

---

## 9. Error Handling Documentation

### 9.1 Lexical Errors

```
Example Errors:
════════════════════════════════════════════════════════════
Error 1: Invalid character
Source: x = 5 @ 3
        ─────^
Error: Unknown character '@' at line 1, column 7

Error 2: Invalid identifier
Source: 123abc = 5
        ^─────
Error: Identifier cannot start with digit at line 1, column 1
════════════════════════════════════════════════════════════
```

### 9.2 Syntax Errors

```
Example Errors:
════════════════════════════════════════════════════════════
Error 1: Missing delimiter
Source: if x > 5
           print x
Error: Expected '{' after condition at line 1, column 9

Error 2: Mismatched braces
Source: for i in arr {
            print i
Error: Expected '}' at line 2, column 20

Error 3: Invalid expression
Source: x = + 5
           ^
Error: Unexpected '+' at line 1, column 5
════════════════════════════════════════════════════════════
```

### 9.3 Semantic Errors

```
Example Errors:
════════════════════════════════════════════════════════════
Error 1: Type mismatch
Source: x = 5
        y = x + pattern fibonacci 3
                ^──────────────────
Error: Cannot add int and array at line 2, column 9

Error 2: Undefined variable
Source: print undefined_var
              ^────────────
Error: Variable 'undefined_var' not defined at line 1

Error 3: Invalid array access
Source: x = 5
        y = x[0]
            ^───
Error: Cannot index non-array type int at line 2
════════════════════════════════════════════════════════════
```

---

## 10. Checklist Summary

### Handwritten Documentation Checklist:

- [ ] **BNF Grammar** - Complete formal grammar
- [ ] **EBNF Grammar** - Extended notation
- [ ] **Lexical Rules** - Token specifications with regex
- [ ] **DFA Diagrams** - For identifiers, numbers, operators, comments
- [ ] **FIRST & FOLLOW Sets** - For LL(1) parsing
- [ ] **LL(1) Parsing Table** - Complete table
- [ ] **LL(1) Parse Trees** - 2-3 examples
- [ ] **LR(0) Items** - Complete item sets
- [ ] **LR(0) Automaton** - State diagram
- [ ] **SLR(1) Parsing Table** - Complete table
- [ ] **CLR(1) Items** - With lookaheads
- [ ] **LALR(1) Construction** - State merging
- [ ] **Bottom-Up Parse Examples** - Shift-reduce traces
- [ ] **Type System Rules** - Formal typing rules
- [ ] **Symbol Table Structure** - Entry format
- [ ] **Symbol Table Examples** - For 2+ programs
- [ ] **Semantic Error Examples** - Common errors
- [ ] **TAC Examples** - For various constructs
- [ ] **Quadruples** - Alternative representation
- [ ] **Triples** - Alternative representation
- [ ] **Optimization Examples** - All techniques
- [ ] **Complete Program 1** - Full compilation trace
- [ ] **Complete Program 2** - Full compilation trace
- [ ] **Derivation Trees** - For key expressions
- [ ] **Error Handling Examples** - All phases

---

## Notes for Handwritten Work

### Drawing Tips:
1. **Use ruled paper** for tables and structured diagrams
2. **Use graph paper** for DFAs and parse trees
3. **Leave margins** for annotations
4. **Use different colors** for different phases
5. **Number all pages** and create an index

### Presentation Structure:
1. **Title page** with compiler name and features
2. **Table of contents**
3. **One section per compiler phase**
4. **Clear headings** and subheadings
5. **Examples after each concept**
6. **Summary page** at the end

### Important Formulas to Include:
- FIRST/FOLLOW set calculations
- Closure operations for LR items
- Type inference rules
- Optimization transformation rules

---

**End of Handwritten Documentation Guide**

This document serves as a comprehensive guide for creating handwritten compiler documentation for the Sequentia language. Follow each section systematically to create complete, professional documentation for your compiler project.
