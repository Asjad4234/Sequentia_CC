# Sequentia - The Language of Mathematical Flow

A powerful domain-specific language for generating, manipulating, and analyzing mathematical sequence patterns with support for vector arithmetic, control flow, and slicing operations.

## Table of Contents
- [Installation & Usage](#installation--usage)
- [Language Features](#language-features)
- [Quick Examples](#quick-examples)
- [Language Syntax](#language-syntax)
- [Pattern Types](#pattern-types)
- [Advanced Examples](#advanced-examples)
- [Technical Implementation](#technical-implementation)
- [Test Files](#test-files)
- [Language Rules](#language-rules)
- [Contributing](#contributing)

## Installation & Usage

### Running Sequentia Programs

**From a file:**
```bash
python sequentia_compiler.py program.seq
```

**Interactive REPL:**
```bash
python sequentia_compiler.py
>>> x = pattern fibonacci 5
>>> print x
>>> 
```
Press Enter on an empty line to execute the code block.

## Language Features

Sequentia includes powerful features for mathematical computing:

✨ **Pattern Generation**: Create mathematical sequences (Fibonacci, factorial, arithmetic, geometric, etc.)  
🧮 **Vector Arithmetic**: Perform element-wise operations on arrays with automatic scalar broadcasting  
✂️ **Slicing**: Extract sub-sequences using Python-style slicing syntax  
🔀 **Control Flow**: If/else conditionals and for loops  
🎯 **Dynamic Typing**: Variables can hold integers or arrays  
💬 **Comments**: Full support for `#` line comments

## Quick Examples

### Vector Arithmetic
```
fib = pattern fibonacci 6
doubled = fib * 2          # Scalar broadcast: [0, 2, 2, 4, 6, 10]
sum = fib + doubled        # Element-wise: [0, 3, 3, 6, 9, 15]
```

### Slicing
```
x = pattern fibonacci 10
middle = x[2:5]           # Extract elements 2, 3, 4
first_five = x[:5]        # Extract first 5 elements
```

### Control Flow
```
for val in pattern square 10 {
    if val > 25 {
        print val
    }
}
```

## Language Syntax

### 1. Variable Assignment

#### Scalar Assignment
```
n = 5
count = 10
```

#### Pattern Assignment
```
variable = pattern PATTERN_TYPE arguments
```

Arguments can be:
- **Numbers**: `pattern fibonacci 5`
- **Variables**: `pattern square n`
- **Array elements**: `pattern cube x[3]`

#### Vector Arithmetic Assignment
```
fib = pattern fibonacci 6
doubled = fib * 2          # [0, 2, 2, 4, 6, 10]
sum = fib + doubled        # [0, 3, 3, 6, 9, 15]
```

#### Slicing Assignment
```
x = pattern fibonacci 10
middle = x[2:5]           # Extract elements 2, 3, 4
first_five = x[:5]        # First 5 elements
last_five = x[5:]         # From index 5 to end
```

### 2. Arithmetic Operations

#### Scalar Arithmetic
```
a = 5
b = 3
sum = a + b               # 8
diff = a - b              # 2
prod = a * b              # 15
quot = a / b              # 1 (integer division)
```

#### Vector Arithmetic (Element-wise)
```
fib = pattern fibonacci 5     # [0, 1, 1, 2, 3]
squares = pattern square 5    # [1, 4, 9, 16, 25]

sum = fib + squares           # [1, 5, 10, 18, 28]
diff = squares - fib          # [1, 3, 8, 14, 22]
prod = fib * squares          # [0, 4, 9, 32, 75]
```

#### Scalar Broadcasting
```
x = pattern fibonacci 6       # [0, 1, 1, 2, 3, 5]
doubled = x * 2               # [0, 2, 2, 4, 6, 10]
shifted = x + 10              # [10, 11, 11, 12, 13, 15]
halved = x / 2                # [0, 0, 0, 1, 1, 2] (integer division)
```

### 3. Comparison Operations

```
x = 5
y = 3
result = x > y                # true (1)
result = x == y               # false (0)
result = x <= 10              # true (1)
```

**Supported operators:** `==`, `!=`, `<`, `>`, `<=`, `>=`

### 4. Control Flow

#### If/Else Statements
```
x = 5
if x > 3 {
    print x
}

if x > 10 {
    print "High"
} else {
    print "Low"
}
```

**Nested conditions:**
```
score = 85
if score >= 90 {
    print "A"
} else {
    if score >= 80 {
        print "B"
    } else {
        print "C"
    }
}
```

#### For Loops
```
fib = pattern fibonacci 8
for num in fib {
    print num
}
```

**Loop with conditions:**
```
squares = pattern square 10
for val in squares {
    if val > 25 {
        print val
    }
}
```

**Nested loops:**
```
x = pattern fibonacci 5
y = pattern square 3
for a in x {
    for b in y {
        print a + b
    }
}
```

### 5. Slicing

```
x = pattern fibonacci 10      # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# Basic slicing
middle = x[2:5]               # [1, 2, 3]
first_half = x[:5]            # [0, 1, 1, 2, 3]
second_half = x[5:]           # [5, 8, 13, 21, 34]

# Use slices in operations
doubled = x[2:7] * 2          # Double middle section
```

### 6. Print Statement

**Print scalar:**
```
n = 5
print n                       # Output: 5
```

**Print array:**
```
fib = pattern fibonacci 5
print fib                     # Output: 0 1 1 2 3
```

**Print expressions:**
```
x = pattern fibonacci 5
print x * 2                   # Print vector arithmetic result
print x[1:4]                  # Print slice
```

### 7. Comments
```
# This is a comment
x = pattern fibonacci 5       # Generate Fibonacci sequence
```

## Pattern Types

### Fibonacci
Generates Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, ...

**Syntax:** `pattern fibonacci N`

```
fib = pattern fibonacci 8
print fib
# Output: 0 1 1 2 3 5 8 13
```

---

### Factorial
Generates factorials: 1!, 2!, 3!, 4!, ...

**Syntax:** `pattern factorial N`

```
fact = pattern factorial 5
print fact
# Output: 1 2 6 24 120
```

---

### Square
Generates perfect squares: 1², 2², 3², 4², ...

**Syntax:** `pattern square N`

```
squares = pattern square 6
print squares
# Output: 1 4 9 16 25 36
```

---

### Cube
Generates perfect cubes: 1³, 2³, 3³, 4³, ...

**Syntax:** `pattern cube N`

```
cubes = pattern cube 5
print cubes
# Output: 1 8 27 64 125
```

---

### Triangular
Generates triangular numbers: 1, 3, 6, 10, 15, ...

**Formula:** T(n) = n(n+1)/2

**Syntax:** `pattern triangular N`

```
tri = pattern triangular 7
print tri
# Output: 1 3 6 10 15 21 28
```

---

### Arithmetic
Generates arithmetic sequence with constant difference.

**Syntax:** `pattern arithmetic START, STEP, N`

**Formula:** a(i) = START + STEP × i

```
odds = pattern arithmetic 1, 2, 8
print odds
# Output: 1 3 5 7 9 11 13 15
```

---

### Geometric
Generates geometric sequence with constant ratio.

**Syntax:** `pattern geometric START, RATIO, N`

**Formula:** a(i) = START × RATIO^i

```
powers = pattern geometric 1, 2, 10
print powers
# Output: 1 2 4 8 16 32 64 128 256 512
```

## Advanced Examples

### Example 1: Vector Processing Pipeline
```
# Generate data
fib = pattern fibonacci 10

# Process with vector arithmetic
doubled = fib * 2
shifted = doubled + 5

# Extract and analyze
middle = shifted[2:7]

# Conditional processing
for val in middle {
    if val > 10 {
        print val
    }
}
```

**Output:**
```
12
14
```

### Example 2: Nested Loops with Arithmetic
```
# Generate sequences
x = pattern fibonacci 5
y = pattern square 4

# Nested iteration
for a in x {
    for b in y {
        sum = a + b
        if sum > 10 {
            print sum
        }
    }
}
```

### Example 3: Slicing and Broadcasting
```
# Create sequence
nums = pattern arithmetic 0, 5, 10

# Extract chunks
first_half = nums[:5]
second_half = nums[5:]

# Scale differently
scaled1 = first_half * 2
scaled2 = second_half * 3

print scaled1
print scaled2
```

**Output:**
```
0 10 20 30 40
75 90 105 120 135
```

### Example 4: Complex Data Processing
```
# Generate multiple sequences
fib = pattern fibonacci 6
squares = pattern square 6
cubes = pattern cube 6

# Combine with arithmetic
combined = fib + squares * 2 - cubes / 3
print combined

# Process result
result = combined[1:5] * 10
print result
```

## Technical Implementation

### Compiler Architecture

Sequentia uses a 4-phase compiler:

1. **Lexer**: Tokenizes source code
   - Keywords: `pattern`, `print`, `if`, `else`, `for`, `in`
   - Operators: `+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`, `<=`, `>=`
   - Delimiters: `{`, `}`, `[`, `]`, `(`, `)`, `:`, `,`
   - Comments: `#` to end of line

2. **Parser**: Builds Abstract Syntax Tree (AST)
   - Expression precedence: comparison → additive → multiplicative → primary
   - AST nodes: `Program`, `Assign`, `Print`, `IfStmt`, `ForStmt`, `BinOp`, `SliceExpr`, `PatternExpr`
   - Support for nested structures

3. **Semantic Analyzer**: Validates types and constraints
   - Type system: `int` (scalars) and `array` (sequences)
   - Type inference for operations
   - Variable definition checking
   - Operation compatibility validation

4. **Code Generator**: Produces executable Python code
   - Injects runtime helper functions
   - Generates efficient list comprehensions
   - Handles scalar broadcasting automatically
   - Proper indentation for nested blocks

### Runtime Helper Functions

The compiler automatically injects helper functions for vector arithmetic:

```python
def _pat_add(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return [x + y for x, y in zip(a, b)]
    elif isinstance(a, list):
        return [x + b for x in a]
    elif isinstance(b, list):
        return [a + x for x in b]
    else:
        return a + b
```

Similar implementations for:
- `_pat_sub(a, b)`: Subtraction with broadcasting
- `_pat_mul(a, b)`: Multiplication with broadcasting
- `_pat_div(a, b)`: Integer division with broadcasting
- `_fib_inline(n)`: Generate Fibonacci inline
- `_fact_inline(n)`: Generate factorial inline

### Type System

**Types:**
- **int**: Single integer values, comparison results
- **array**: Sequences of integers

**Type Inference:**
- `int op int` → `int`
- `array op array` → `array` (element-wise)
- `array op int` → `array` (broadcast)
- `int op array` → `array` (broadcast)
- Comparisons always return `int`

**Operator Precedence (highest to lowest):**
1. Array access/slicing: `[]`, `[:]`
2. Multiplication/Division: `*`, `/`
3. Addition/Subtraction: `+`, `-`
4. Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`

### Key Design Decisions

1. **Runtime helpers instead of compile-time type checking**
   - Simpler implementation
   - Handles dynamic types naturally
   - Offloads complexity to Python runtime

2. **Curly braces for blocks**
   - Avoids whitespace/indentation parsing complexity
   - Familiar syntax for many programmers

3. **Direct Python slicing**
   - 1:1 mapping to Python syntax
   - No need to reinvent the wheel
   - Familiar to Python developers

4. **Inline pattern support**
   - Allows `for i in pattern fib 5` without intermediate variable
   - More expressive code

## Test Files

The repository includes comprehensive test files:

1. **test_vector_arithmetic.seq** - Vector operations and broadcasting
2. **test_slicing.seq** - Array slicing operations
3. **test_conditionals.seq** - If/else statements
4. **test_for_loops.seq** - For loop iterations
5. **test_comparisons.seq** - All comparison operators
6. **test_comprehensive.seq** - Combined features
7. **test_edge_cases.seq** - Edge cases and inline patterns
8. **demo_all_features.seq** - Simple demonstration

Run any test with:
```bash
python sequentia_compiler.py test_filename.seq
```

## Language Rules & Constraints

1. ✓ **Variable names** must start with a letter or underscore, followed by letters, digits, or underscores
2. ✓ **Scalar variables** hold single integer values
3. ✓ **Array variables** hold sequences generated by patterns or operations
4. ✓ **Vector arithmetic** supports: `+`, `-`, `*`, `/` (integer division)
5. ✓ **Comparison operators**: `==`, `!=`, `<`, `>`, `<=`, `>=`
6. ✓ **Control flow** uses curly braces `{ }` for blocks
7. ✓ **Slicing syntax**: `array[start:end]` (start inclusive, end exclusive)
8. ✓ **Scalar broadcasting** automatically applies scalars to all array elements
9. ✓ **Comments** start with `#` and extend to end of line
10. ✓ **Statements** are separated by newlines; blocks use `{ }`

## Error Handling

The compiler provides clear errors for:

- **Lexical errors**: Unknown characters
- **Syntax errors**: Invalid statement structure, mismatched braces
- **Semantic errors**:
  - Undefined variables
  - Type mismatches (e.g., using array as index)
  - Wrong number of pattern arguments
  - Invalid operation types
- **Runtime errors**: Out-of-bounds array access

## Backward Compatibility

All existing Sequentia programs continue to work. New features are additive only.

## Performance Considerations

- Runtime helpers add small overhead per operation
- List comprehensions used where possible for efficiency
- Inline patterns may be less efficient than pre-computed arrays
- Generated Python code is readable and debuggable

## Future Enhancements

Possible extensions:
- Boolean type and logical operators (`and`, `or`, `not`)
- While loops
- Functions/procedures
- More mathematical operations (modulo, exponentiation, floor, ceiling)
- String support
- File I/O operations
- List methods (append, sort, reverse)
- Dictionary/map types

## Contributing

Contributions welcome! Areas for improvement:
- Additional pattern types
- Optimization of generated code
- Better error messages with line numbers
- IDE support (syntax highlighting, LSP)
- More comprehensive test suite
- Performance benchmarks

## License

MIT License - Feel free to use and modify.

## Repository

**GitHub**: Sequentia_CC  
**Owner**: Asjad4234  
**Branch**: main

---

*Built with ❤️ for mathematical sequence exploration*

