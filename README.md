# Sequentia - The Language of Mathematical Flow

A simple domain-specific language for generating and printing mathematical sequence patterns.

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

## Language Syntax

### 1. Variable Assignment

#### Scalar Assignment
Assign integer values to variables:
```
n = 5
count = 10
```

#### Array Element Assignment
Extract a single element from an array:
```
x = pattern square 5
y = x[2]                 # y = 9 (third element, 0-indexed)
```

#### Array Copy Assignment
Copy an entire array to a new variable:
```
x = pattern fibonacci 6
y = x                    # y is now a copy of x
```

#### Pattern Assignment
Generate arrays using pattern expressions:
```
variable = pattern PATTERN_TYPE arguments
```

Arguments can be:
- **Numbers**: `pattern fibonacci 5`
- **Variables**: `pattern square n`
- **Array elements**: `pattern cube x[3]`

### 2. Print Statement

**Print scalar (integer):**
```
n = 5
x = pattern fibonacci 10
y = x[n]
print y
```
Output: Single number

**Print entire array:**
```
print variable
```
Output: Space-separated values

**Print single element:**
```
print variable[index]
```
Index can be a number or variable.

### 3. Comments
Lines starting with `#` are comments:
```
# This is a comment
x = pattern fibonacci 5  # Generate Fibonacci sequence
```

## Pattern Types

### Fibonacci
Generates Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, ...

**Syntax:** `pattern fibonacci N`
- **N**: Number of terms to generate (N ≥ 1)

**Example:**
```
fib = pattern fibonacci 8
print fib
```
**Output:** `0 1 1 2 3 5 8 13`

---

### Factorial
Generates factorials: 1!, 2!, 3!, 4!, ...

**Syntax:** `pattern factorial N`
- **N**: Number of factorials (N ≥ 1)

**Example:**
```
fact = pattern factorial 5
print fact
```
**Output:** `1 2 6 24 120`

---

### Square
Generates perfect squares: 1², 2², 3², 4², ...

**Syntax:** `pattern square N`
- **N**: Number of squares (N ≥ 1)

**Example:**
```
squares = pattern square 6
print squares
```
**Output:** `1 4 9 16 25 36`

---

### Cube
Generates perfect cubes: 1³, 2³, 3³, 4³, ...

**Syntax:** `pattern cube N`
- **N**: Number of cubes (N ≥ 1)

**Example:**
```
cubes = pattern cube 5
print cubes
```
**Output:** `1 8 27 64 125`

---

### Triangular
Generates triangular numbers: 1, 3, 6, 10, 15, ...

Formula: T(n) = n(n+1)/2

**Syntax:** `pattern triangular N`
- **N**: Number of triangular numbers (N ≥ 1)

**Example:**
```
tri = pattern triangular 7
print tri
```
**Output:** `1 3 6 10 15 21 28`

---

### Arithmetic
Generates arithmetic sequence with constant difference.

**Syntax:** `pattern arithmetic START, STEP, N`
- **START**: First term
- **STEP**: Common difference (STEP > 0)
- **N**: Number of terms (N ≥ 1)

**Formula:** a(i) = START + STEP × i

**Examples:**

Odd numbers:
```
odds = pattern arithmetic 1, 2, 8
print odds
```
**Output:** `1 3 5 7 9 11 13 15`

Multiples of 5:
```
fives = pattern arithmetic 5, 5, 6
print fives
```
**Output:** `5 10 15 20 25 30`

Custom sequence:
```
seq = pattern arithmetic 100, 15, 5
print seq
```
**Output:** `100 115 130 145 160`

---

### Geometric
Generates geometric sequence with constant ratio.

**Syntax:** `pattern geometric START, RATIO, N`
- **START**: First term
- **RATIO**: Common ratio (RATIO > 0)
- **N**: Number of terms (N ≥ 1)

**Formula:** a(i) = START × RATIO^i

**Examples:**

Powers of 2:
```
powers = pattern geometric 1, 2, 10
print powers
```
**Output:** `1 2 4 8 16 32 64 128 256 512`

Powers of 3:
```
threes = pattern geometric 1, 3, 6
print threes
```
**Output:** `1 3 9 27 81 243`

Custom geometric sequence:
```
geo = pattern geometric 5, 2, 6
print geo
```
**Output:** `5 10 20 40 80 160`

## Advanced Features

### Using Variables in Patterns

You can use previously defined variables in pattern arguments:

```
n = 5
start_val = 10
step_val = 3

seq = pattern arithmetic start_val, step_val, n
print seq
```
**Output:** `10 13 16 19 22`

### Array Element Assignment

Extract single elements from arrays and use them as scalars:

```
x = pattern square 5
y = x[2]        # y = 9
print y
```
**Output:** `9`

### Array Copy

Copy entire arrays to new variables:

```
x = pattern fibonacci 6
y = x
print y
```
**Output:** `0 1 1 2 3 5`

### Array Indexing with Variables

Use variables as array indices:

```
n = 3
arr = pattern fibonacci 10
elem = arr[n]
print elem
```
**Output:** `2`

### Using Array Elements in Patterns

Use array elements as arguments to create new patterns:

```
x = pattern square 5      # [1, 4, 9, 16, 25]
y = pattern cube x[3]     # x[3] = 16, so generate first 16 cubes
print y
```
**Output:** `1 8 27 64 125 216 343 512 729 1000 1331 1728 2197 2744 3375 4096`

Complex nested example:
```
n = 3
x = pattern fibonacci 10
count = x[n]              # count = 2
y = pattern square count  # Generate 2 squares
print x
print y
```
**Output:**
```
0 1 1 2 3 5 8 13 21 34
1 4
```

### Complete Example

```
# Define parameters
count = 8
index = 5

# Generate sequences
fib = pattern fibonacci count
squares = pattern square count
arith = pattern arithmetic 0, 5, count

# Print full arrays
print fib
print squares
print arith

# Extract and print specific elements
elem1 = fib[index]
elem2 = squares[index]
elem3 = arith[index]
print elem1
print elem2
print elem3

# Use array element in pattern
x = pattern triangular 6
y = pattern geometric 2, 2, x[3]
print x
print y
```

**Output:**
```
0 1 1 2 3 5 8 13
1 4 9 16 25 36 49 64
0 5 10 15 20 25 30 35
5
36
25
1 3 6 10 15 21
2 4 8 16 32 64 128 256 512 1024
```

## Language Rules & Constraints

1. **Variable names** must start with a letter or underscore, followed by letters, digits, or underscores
2. **Scalar variables** can only hold single integer values
3. **Array variables** hold sequences generated by patterns
4. **Array elements** can be extracted using indexing: `y = x[2]`
5. **Arrays can be copied** to new variables: `y = x`
6. **Pattern arguments** can be:
   - Literal numbers: `pattern fibonacci 5`
   - Scalar variables: `pattern square n`
   - Array elements: `pattern cube x[3]`
7. **Print statements** work on both scalars and arrays
8. **No arithmetic operations** on variables (e.g., `x + y` is not supported)
9. **Array bounds** are validated at runtime
10. **Comments** start with `#` and extend to end of line
11. **Each statement** should be on its own line

## Error Handling

The compiler provides errors for:
- **Lexical errors**: Unknown characters
- **Syntax errors**: Invalid statement structure
- **Semantic errors**: 
  - Undefined variables
  - Wrong number of pattern arguments
  - Invalid argument values (e.g., negative counts)
  - Out-of-bounds array access (runtime)
  - Type mismatches (e.g., using array as index)
  - Invalid pattern arguments

## Compilation Process

Sequentia uses a 4-phase compiler:

1. **Lexer**: Tokenizes source code and handles comments
2. **Parser**: Builds Abstract Syntax Tree (AST) with support for:
   - Pattern expressions
   - Array access expressions
   - Scalar and array assignments
3. **Semantic Analyzer**: Validates types and constraints
   - Type checking (int vs array)
   - Variable definition checking
   - Pattern argument validation
4. **Code Generator**: Produces executable Python code
   - Generates efficient list comprehensions
   - Handles dynamic runtime values

The generated Python code is displayed before execution.

