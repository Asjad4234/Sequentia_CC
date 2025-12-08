import sys
import io, contextlib
from typing import List, Tuple, Dict, Any


# --------------------------
# Lexer
# --------------------------

KEYWORDS = {
    'pattern': 'PATTERN_KW',
    'print': 'PRINT_KW',
    'fibonacci': 'FIB_KW',
    'factorial': 'FACT_KW',
    'square': 'SQUARE_KW',
    'cube': 'CUBE_KW',
    'arithmetic': 'ARITH_KW',
    'geometric': 'GEO_KW',
    'triangular': 'TRI_KW',
    'if': 'IF_KW',
    'else': 'ELSE_KW',
    'for': 'FOR_KW',
    'in': 'IN_KW'
}

SINGLE = {
    '=': 'ASSIGN',
    ',': 'COMMA',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    '{': 'LBRACE',
    '}': 'RBRACE',
    ':': 'COLON',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'STAR',
    '/': 'SLASH',
    '(': 'LPAREN',
    ')': 'RPAREN'
}

DOUBLE = {
    '==': 'EQ',
    '!=': 'NEQ',
    '<=': 'LEQ',
    '>=': 'GEQ'
}

COMPARISON = {
    '<': 'LT',
    '>': 'GT'
}

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def peek(self):
        return self.text[self.pos] if self.pos < len(self.text) else None

    def advance(self):
        ch = self.peek()
        if ch: self.pos += 1
        return ch

    def skip_ws(self):
        while self.peek() and self.peek() in " \t\r":
            self.advance()

    def lex_number(self):
        start = self.pos
        while self.peek() and self.peek().isdigit():
            self.advance()
        return ('NUMBER', self.text[start:self.pos])

    def lex_id(self):
        start = self.pos
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
        word = self.text[start:self.pos]
        if word in KEYWORDS:
            return (KEYWORDS[word], word)
        return ('ID', word)

    def tokens(self):
        out = []
        while True:
            ch = self.peek()
            if not ch:
                break

            # --- NEW: comment support ---
            if ch == "#":
                # Skip until newline but do not consume newline
                while self.peek() and self.peek() not in "\n":
                    self.advance()
                continue
            # ----------------------------

            if ch in " \t\r":
                self.skip_ws()
                continue

            if ch == "\n":
                self.advance()
                out.append(("NEWLINE", "\n"))
                continue

            if ch.isdigit():
                out.append(self.lex_number())
                continue

            if ch.isalpha() or ch == '_':
                out.append(self.lex_id())
                continue

            # Check for double-character operators first
            if self.pos + 1 < len(self.text):
                two_char = ch + self.text[self.pos + 1]
                if two_char in DOUBLE:
                    out.append((DOUBLE[two_char], two_char))
                    self.advance()
                    self.advance()
                    continue

            # Check for single-character comparison operators
            if ch in COMPARISON:
                out.append((COMPARISON[ch], ch))
                self.advance()
                continue

            if ch in SINGLE:
                out.append((SINGLE[ch], ch))
                self.advance()
                continue

            raise Exception("Unknown character " + ch)

        out.append(("EOF", ""))
        return out

# Abstract Syntax Tree (AST)

class Program: 
    def __init__(self, stmts): self.stmts = stmts

class Assign:
    def __init__(self, name, expr): 
        self.name = name
        self.expr = expr

class PatternExpr:
    def __init__(self, pattern_name, args):
        self.pattern_name = pattern_name
        self.args = args  # list of expr (either number or ID)

class NumberExpr:
    def __init__(self, value): self.value = value

class IDExpr:
    def __init__(self, name): self.name = name

class ArrayAccessExpr:
    def __init__(self, name, index_expr):
        self.name = name
        self.index_expr = index_expr  # NumberExpr or IDExpr

class SliceExpr:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start  # NumberExpr, IDExpr, or None
        self.end = end      # NumberExpr, IDExpr, or None

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op  # '+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>='
        self.right = right

class IfStmt:
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition  # BinOp or expression
        self.true_block = true_block  # list of statements
        self.false_block = false_block  # list of statements or None

class ForStmt:
    def __init__(self, iterator, source, body):
        self.iterator = iterator  # variable name (string)
        self.source = source      # variable name (string) or expression
        self.body = body          # list of statements

class Print:
    def __init__(self, name, index_expr=None):
        self.name = name
        self.index_expr = index_expr  # may be NumberExpr or IDExpr

# --------------------------
# Parser
# --------------------------

class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.pos = 0

    def peek(self):
        return self.toks[self.pos]

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expect(self, t):
        tok = self.peek()
        if tok[0] != t:
            raise Exception(f"Expected {t}, got {tok}")
        return self.advance()

    def parse_program(self):
        stmts = []
        while self.peek()[0] != "EOF":
            if self.peek()[0] == "NEWLINE":
                self.advance()
                continue
            stmts.append(self.parse_stmt())
            if self.peek()[0] == "NEWLINE":
                self.advance()
        return Program(stmts)

    def parse_stmt(self):
        tok = self.peek()
        if tok[0] == 'ID':
            return self.parse_assign()
        if tok[0] == 'PRINT_KW':
            return self.parse_print()
        if tok[0] == 'IF_KW':
            return self.parse_if()
        if tok[0] == 'FOR_KW':
            return self.parse_for()
        raise Exception("Invalid statement start " + str(tok))

    def parse_expr(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_additive()
        
        tok = self.peek()
        if tok[0] in ['EQ', 'NEQ', 'LT', 'GT', 'LEQ', 'GEQ']:
            op = self.advance()[1]
            right = self.parse_additive()
            return BinOp(left, op, right)
        
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        
        while self.peek()[0] in ['PLUS', 'MINUS']:
            op = self.advance()[1]
            right = self.parse_multiplicative()
            left = BinOp(left, op, right)
        
        return left

    def parse_multiplicative(self):
        left = self.parse_primary()
        
        while self.peek()[0] in ['STAR', 'SLASH']:
            op = self.advance()[1]
            right = self.parse_primary()
            left = BinOp(left, op, right)
        
        return left

    def parse_primary(self):
        tok = self.peek()

        # parenthesized expression
        if tok[0] == 'LPAREN':
            self.advance()
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr

        # pattern expression
        if tok[0] == "PATTERN_KW":
            self.advance()
            pname = self.expect_any_pattern()
            args = [self.parse_additive()]
            while self.peek()[0] == "COMMA":
                self.advance()
                args.append(self.parse_additive())
            return PatternExpr(pname, args)

        # number literal
        if tok[0] == 'NUMBER':
            return NumberExpr(int(self.advance()[1]))

        # ID or array access or slice
        if tok[0] == 'ID':
            name = self.advance()[1]
            # Check for array indexing or slicing
            if self.peek()[0] == 'LBRACKET':
                self.advance()
                # Check if it's a slice (has colon)
                start_expr = None
                if self.peek()[0] != 'COLON':
                    start_expr = self.parse_additive()
                
                if self.peek()[0] == 'COLON':
                    self.advance()
                    end_expr = None
                    if self.peek()[0] != 'RBRACKET':
                        end_expr = self.parse_additive()
                    self.expect('RBRACKET')
                    return SliceExpr(name, start_expr, end_expr)
                else:
                    # Regular array access
                    self.expect('RBRACKET')
                    return ArrayAccessExpr(name, start_expr)
            return IDExpr(name)

        raise Exception("Invalid expression start " + str(tok))

    def expect_any_pattern(self):
        tok = self.peek()
        if tok[0] in ['FIB_KW','FACT_KW','SQUARE_KW','CUBE_KW','ARITH_KW','GEO_KW','TRI_KW']:
            return self.advance()[1]
        raise Exception("Invalid pattern keyword")

    def parse_assign(self):
        name = self.expect('ID')[1]
        self.expect('ASSIGN')
        expr = self.parse_expr()
        return Assign(name, expr)

    def parse_print(self):
        self.expect('PRINT_KW')
        expr = self.parse_expr()
        # For backward compatibility, if it's just an ID or array access, use old Print format
        if isinstance(expr, IDExpr):
            return Print(expr.name)
        elif isinstance(expr, ArrayAccessExpr):
            return Print(expr.name, expr.index_expr)
        else:
            # For any other expression, store it as index_expr with special marker
            return Print("_expr_", expr)

    def parse_if(self):
        self.expect('IF_KW')
        condition = self.parse_expr()
        self.expect('LBRACE')
        # Skip newlines after opening brace
        while self.peek()[0] == 'NEWLINE':
            self.advance()
        
        true_block = []
        while self.peek()[0] != 'RBRACE':
            if self.peek()[0] == 'NEWLINE':
                self.advance()
                continue
            true_block.append(self.parse_stmt())
        
        self.expect('RBRACE')
        
        false_block = None
        if self.peek()[0] == 'ELSE_KW':
            self.advance()
            self.expect('LBRACE')
            # Skip newlines after opening brace
            while self.peek()[0] == 'NEWLINE':
                self.advance()
            
            false_block = []
            while self.peek()[0] != 'RBRACE':
                if self.peek()[0] == 'NEWLINE':
                    self.advance()
                    continue
                false_block.append(self.parse_stmt())
            
            self.expect('RBRACE')
        
        return IfStmt(condition, true_block, false_block)

    def parse_for(self):
        self.expect('FOR_KW')
        iterator = self.expect('ID')[1]
        self.expect('IN_KW')
        source_expr = self.parse_expr()
        # Extract variable name if it's an IDExpr
        if isinstance(source_expr, IDExpr):
            source = source_expr.name
        else:
            source = source_expr  # Keep the expression for codegen
        
        self.expect('LBRACE')
        # Skip newlines after opening brace
        while self.peek()[0] == 'NEWLINE':
            self.advance()
        
        body = []
        while self.peek()[0] != 'RBRACE':
            if self.peek()[0] == 'NEWLINE':
                self.advance()
                continue
            body.append(self.parse_stmt())
        
        self.expect('RBRACE')
        
        return ForStmt(iterator, source, body)


# --------------------------
# Semantic Analyzer
# --------------------------

class Symbol:
    def __init__(self, name, sym_type, length=None, pattern=None, args=None):
        self.name = name
        self.type = sym_type  # "int" or "array"
        self.length = length
        self.pattern = pattern
        self.args = args

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.sym = {}

    def check(self):
        for stmt in self.ast.stmts:
            if isinstance(stmt, Assign):
                self.check_assign(stmt)
            elif isinstance(stmt, Print):
                self.check_print(stmt)
            elif isinstance(stmt, IfStmt):
                self.check_if(stmt)
            elif isinstance(stmt, ForStmt):
                self.check_for(stmt)

    def eval_scalar(self, expr):
        if isinstance(expr, NumberExpr): return expr.value
        if isinstance(expr, IDExpr):
            if expr.name not in self.sym: raise Exception("Undefined variable " + expr.name)
            if self.sym[expr.name].type != "int":
                raise Exception(expr.name + " is not a scalar integer")
            return None  # means dynamic
        raise Exception("Unsupported scalar expression")

    def check_assign(self, stmt):
        expr = stmt.expr

        # Case 1: scalar int assignment: n = 3
        if isinstance(expr, NumberExpr):
            self.sym[stmt.name] = Symbol(stmt.name, "int")
            return

        # Case 2: array element access: y = x[2]
        if isinstance(expr, ArrayAccessExpr):
            if expr.name not in self.sym:
                raise Exception("Undefined array " + expr.name)
            if self.sym[expr.name].type != "array":
                raise Exception(expr.name + " is not an array")
            # Validate index expression
            self.check_expr_type(expr.index_expr, "int")
            # Result is an integer
            self.sym[stmt.name] = Symbol(stmt.name, "int")
            return

        # Case 2.5: slice expression: y = x[1:5]
        if isinstance(expr, SliceExpr):
            if expr.name not in self.sym:
                raise Exception("Undefined array " + expr.name)
            if self.sym[expr.name].type != "array":
                raise Exception(expr.name + " is not an array")
            # Validate slice bounds
            if expr.start:
                self.check_expr_type(expr.start, "int")
            if expr.end:
                self.check_expr_type(expr.end, "int")
            # Result is an array
            self.sym[stmt.name] = Symbol(stmt.name, "array")
            return

        # Case 3: ID assignment (scalar or array)
        if isinstance(expr, IDExpr):
            if expr.name not in self.sym:
                raise Exception("Undefined source variable " + expr.name)
            # Copy type from source
            src_sym = self.sym[expr.name]
            if src_sym.type == "int":
                self.sym[stmt.name] = Symbol(stmt.name, "int")
            else:  # array
                self.sym[stmt.name] = Symbol(stmt.name, "array", 
                                             length=src_sym.length,
                                             pattern=src_sym.pattern,
                                             args=src_sym.args)
            return

        # Case 4: BinOp (arithmetic or comparison result)
        if isinstance(expr, BinOp):
            result_type = self.check_binop(expr)
            self.sym[stmt.name] = Symbol(stmt.name, result_type)
            return

        # Case 5: pattern expression
        if isinstance(expr, PatternExpr):
            # args may contain IDs or array access → must be int variables
            lengths = []
            for arg in expr.args:
                if isinstance(arg, NumberExpr):
                    lengths.append(arg.value)
                elif isinstance(arg, IDExpr):
                    if arg.name not in self.sym:
                        raise Exception("Undefined scalar variable " + arg.name)
                    if self.sym[arg.name].type != "int":
                        raise Exception("Pattern argument must be integer variable")
                    lengths.append(None)  # dynamic
                elif isinstance(arg, ArrayAccessExpr):
                    # Validate array exists and is array type
                    if arg.name not in self.sym:
                        raise Exception("Undefined array " + arg.name)
                    if self.sym[arg.name].type != "array":
                        raise Exception(arg.name + " is not an array")
                    # Validate index
                    if isinstance(arg.index_expr, IDExpr):
                        if arg.index_expr.name not in self.sym:
                            raise Exception("Undefined index variable " + arg.index_expr.name)
                        if self.sym[arg.index_expr.name].type != "int":
                            raise Exception("Index must be integer")
                    lengths.append(None)  # dynamic - result of array access
                else:
                    raise Exception("Invalid pattern argument")

            # array length is last argument
            self.sym[stmt.name] = Symbol(stmt.name, "array", length=lengths[-1],
                                         pattern=expr.pattern_name, args=expr.args)
            return

        raise Exception("Invalid assignment expression")

    def check_print(self, stmt):
        # Special case for expression printing
        if stmt.name == "_expr_":
            self.check_expr_type(stmt.index_expr, None)  # Any type is ok
            return
        
        if stmt.name not in self.sym:
            raise Exception("Undefined variable in print " + stmt.name)

        # Allow printing both scalars and arrays
        if stmt.index_expr:
            # print x[n]
            self.check_expr_type(stmt.index_expr, "int")

    def check_expr_type(self, expr, expected_type=None):
        """Check expression and return its type. If expected_type is set, validate it matches."""
        if isinstance(expr, NumberExpr):
            actual = "int"
        elif isinstance(expr, IDExpr):
            if expr.name not in self.sym:
                raise Exception("Undefined variable " + expr.name)
            actual = self.sym[expr.name].type
        elif isinstance(expr, ArrayAccessExpr):
            if expr.name not in self.sym:
                raise Exception("Undefined array " + expr.name)
            if self.sym[expr.name].type != "array":
                raise Exception(expr.name + " is not an array")
            self.check_expr_type(expr.index_expr, "int")
            actual = "int"
        elif isinstance(expr, SliceExpr):
            if expr.name not in self.sym:
                raise Exception("Undefined array " + expr.name)
            if self.sym[expr.name].type != "array":
                raise Exception(expr.name + " is not an array")
            if expr.start:
                self.check_expr_type(expr.start, "int")
            if expr.end:
                self.check_expr_type(expr.end, "int")
            actual = "array"
        elif isinstance(expr, BinOp):
            actual = self.check_binop(expr)
        elif isinstance(expr, PatternExpr):
            # Pattern expressions create arrays
            # Validate arguments
            for arg in expr.args:
                self.check_expr_type(arg, None)
            actual = "array"
        else:
            raise Exception("Unknown expression type")
        
        if expected_type and actual != expected_type and expected_type is not None:
            raise Exception(f"Type mismatch: expected {expected_type}, got {actual}")
        
        return actual

    def check_binop(self, expr):
        """Check binary operation and return result type."""
        left_type = self.check_expr_type(expr.left, None)
        right_type = self.check_expr_type(expr.right, None)
        
        # Comparison operators always return int (boolean)
        if expr.op in ['==', '!=', '<', '>', '<=', '>=']:
            return "int"
        
        # Arithmetic operators: can handle scalar or vector
        # Result type depends on operands:
        # int op int -> int
        # array op array -> array
        # array op int -> array (broadcast)
        # int op array -> array (broadcast)
        if left_type == "array" or right_type == "array":
            return "array"
        return "int"

    def check_if(self, stmt):
        """Check if statement."""
        # Check condition
        self.check_expr_type(stmt.condition, None)
        
        # Check true block
        for s in stmt.true_block:
            if isinstance(s, Assign):
                self.check_assign(s)
            elif isinstance(s, Print):
                self.check_print(s)
            elif isinstance(s, IfStmt):
                self.check_if(s)
            elif isinstance(s, ForStmt):
                self.check_for(s)
        
        # Check false block if present
        if stmt.false_block:
            for s in stmt.false_block:
                if isinstance(s, Assign):
                    self.check_assign(s)
                elif isinstance(s, Print):
                    self.check_print(s)
                elif isinstance(s, IfStmt):
                    self.check_if(s)
                elif isinstance(s, ForStmt):
                    self.check_for(s)

    def check_for(self, stmt):
        """Check for loop."""
        # Check source exists and is iterable (array)
        if isinstance(stmt.source, str):
            if stmt.source not in self.sym:
                raise Exception("Undefined variable in for loop: " + stmt.source)
            if self.sym[stmt.source].type != "array":
                raise Exception("For loop source must be an array")
        else:
            # Source is an expression, check it returns an array
            source_type = self.check_expr_type(stmt.source, None)
            if source_type != "array":
                raise Exception("For loop source must be an array")
        
        # Add iterator variable to symbol table as int
        self.sym[stmt.iterator] = Symbol(stmt.iterator, "int")
        
        # Check body
        for s in stmt.body:
            if isinstance(s, Assign):
                self.check_assign(s)
            elif isinstance(s, Print):
                self.check_print(s)
            elif isinstance(s, IfStmt):
                self.check_if(s)
            elif isinstance(s, ForStmt):
                self.check_for(s)


# --------------------------
# Code Generation
# --------------------------

def py_expr(expr, gen_inline=False):
    if isinstance(expr, NumberExpr): 
        return str(expr.value)
    if isinstance(expr, IDExpr): 
        return expr.name
    if isinstance(expr, ArrayAccessExpr):
        idx = py_expr(expr.index_expr)
        return f"{expr.name}[{idx}]"
    if isinstance(expr, SliceExpr):
        start = py_expr(expr.start) if expr.start else ""
        end = py_expr(expr.end) if expr.end else ""
        return f"{expr.name}[{start}:{end}]"
    if isinstance(expr, BinOp):
        left = py_expr(expr.left)
        right = py_expr(expr.right)
        # Map operators to helper functions for arithmetic
        if expr.op == '+':
            return f"_pat_add({left}, {right})"
        elif expr.op == '-':
            return f"_pat_sub({left}, {right})"
        elif expr.op == '*':
            return f"_pat_mul({left}, {right})"
        elif expr.op == '/':
            return f"_pat_div({left}, {right})"
        else:
            # Comparison operators use native Python
            return f"({left} {expr.op} {right})"
    if isinstance(expr, PatternExpr):
        # Generate inline pattern expression
        return gen_pattern_inline(expr.pattern_name, expr.args)
    raise Exception("Invalid expression")

def gen_pattern_inline(pattern, args):
    """Generate inline pattern expression (without assignment)."""
    arg_values = [py_expr(a) for a in args]
    
    # For complex patterns like fibonacci and factorial, we can't easily inline
    # So we'll use simpler expressions where possible
    
    if pattern == "square":
        n = arg_values[0]
        return f"[(i+1)**2 for i in range({n})]"
    
    if pattern == "cube":
        n = arg_values[0]
        return f"[(i+1)**3 for i in range({n})]"
    
    if pattern == "triangular":
        n = arg_values[0]
        return f"[(i+1)*(i+2)//2 for i in range({n})]"
    
    if pattern == "arithmetic":
        start, step, n = arg_values
        return f"[{start} + {step}*i for i in range({n})]"
    
    if pattern == "geometric":
        start, ratio, n = arg_values
        return f"[{start}*({ratio}**i) for i in range({n})]"
    
    # For fibonacci and factorial, generate using a lambda with proper logic
    if pattern == "fibonacci":
        n = arg_values[0]
        return f"(lambda n: (lambda a, b: [(a := (b, a+b)[0], a)[1] for _ in range(n)])(0, 1) if n > 0 else [])({n})" if False else f"_fib_inline({n})"
    
    if pattern == "factorial":
        n = arg_values[0]
        return f"_fact_inline({n})"
    
    raise Exception("Unknown pattern " + pattern)

def gen_pattern(name, pattern, args):
    arg_values = [py_expr(a) for a in args]

    if pattern == "fibonacci":
        n = arg_values[0]
        return f"""
def _gen_{name}():
    a,b = 0,1
    arr=[]
    for _ in range({n}):
        arr.append(a)
        a,b = b, a+b
    return arr
{name} = _gen_{name}()
"""

    if pattern == "factorial":
        n = arg_values[0]
        return f"""
def _gen_{name}():
    arr=[]
    f=1
    for i in range(1, {n}+1):
        f*=i
        arr.append(f)
    return arr
{name} = _gen_{name}()
"""

    if pattern == "square":
        n = arg_values[0]
        return f"""
{name} = [(i+1)**2 for i in range({n})]
"""

    if pattern == "cube":
        n = arg_values[0]
        return f"""
{name} = [(i+1)**3 for i in range({n})]
"""

    if pattern == "triangular":
        n = arg_values[0]
        return f"""
{name} = [(i+1)*(i+2)//2 for i in range({n})]
"""

    if pattern == "arithmetic":
        start, step, n = arg_values
        return f"""
{name} = [{start} + {step}*i for i in range({n})]
"""

    if pattern == "geometric":
        start, ratio, n = arg_values
        return f"""
{name} = [{start}*({ratio}**i) for i in range({n})]
"""

    raise Exception("Unknown pattern " + pattern)


def get_runtime_helpers():
    return """# Runtime Helper Functions for Vector/Scalar Operations
def _pat_add(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return [x + y for x, y in zip(a, b)]
    elif isinstance(a, list):
        return [x + b for x in a]
    elif isinstance(b, list):
        return [a + x for x in b]
    else:
        return a + b

def _pat_sub(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return [x - y for x, y in zip(a, b)]
    elif isinstance(a, list):
        return [x - b for x in a]
    elif isinstance(b, list):
        return [a - x for x in b]
    else:
        return a - b

def _pat_mul(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return [x * y for x, y in zip(a, b)]
    elif isinstance(a, list):
        return [x * b for x in a]
    elif isinstance(b, list):
        return [a * x for x in b]
    else:
        return a * b

def _pat_div(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return [x // y for x, y in zip(a, b)]
    elif isinstance(a, list):
        return [x // b for x in a]
    elif isinstance(b, list):
        return [a // x for x in b]
    else:
        return a // b

def _fib_inline(n):
    a, b = 0, 1
    arr = []
    for _ in range(n):
        arr.append(a)
        a, b = b, a + b
    return arr

def _fact_inline(n):
    arr = []
    f = 1
    for i in range(1, n+1):
        f *= i
        arr.append(f)
    return arr
"""

def generate_python(ast):
    code = ["# Generated Python Code"]
    code.append(get_runtime_helpers())
    
    for stmt in ast.stmts:
        code.extend(gen_stmt(stmt, 0))

    return "\n".join(code)

def gen_stmt(stmt, indent_level):
    """Generate Python code for a statement with proper indentation."""
    indent = "    " * indent_level
    code = []
    
    if isinstance(stmt, Assign):
        if isinstance(stmt.expr, PatternExpr):
            # pattern expression
            p = stmt.expr
            pattern_code = gen_pattern(stmt.name, p.pattern_name, p.args)
            # Add indentation to each line
            for line in pattern_code.strip().split('\n'):
                if line.strip():
                    code.append(indent + line)
        else:
            # All other assignments
            code.append(f"{indent}{stmt.name} = {py_expr(stmt.expr)}")
    
    elif isinstance(stmt, Print):
        if stmt.name == "_expr_":
            # Print any expression
            expr_code = py_expr(stmt.index_expr)
            code.append(f"{indent}print({expr_code} if isinstance({expr_code}, int) else ' '.join(str(x) for x in {expr_code}))")
        elif stmt.index_expr:
            code.append(f"{indent}print({stmt.name}[{py_expr(stmt.index_expr)}])")
        else:
            code.append(f"{indent}print({stmt.name} if isinstance({stmt.name}, int) else ' '.join(str(x) for x in {stmt.name}))")
    
    elif isinstance(stmt, IfStmt):
        condition = py_expr(stmt.condition)
        code.append(f"{indent}if {condition}:")
        
        for s in stmt.true_block:
            code.extend(gen_stmt(s, indent_level + 1))
        
        if stmt.false_block:
            code.append(f"{indent}else:")
            for s in stmt.false_block:
                code.extend(gen_stmt(s, indent_level + 1))
    
    elif isinstance(stmt, ForStmt):
        if isinstance(stmt.source, str):
            source_code = stmt.source
        else:
            source_code = py_expr(stmt.source)
        
        code.append(f"{indent}for {stmt.iterator} in {source_code}:")
        
        for s in stmt.body:
            code.extend(gen_stmt(s, indent_level + 1))
    
    return code


# --------------------------
# Compiler Driver
# --------------------------

def compile_and_run(src):
    tokens = Lexer(src).tokens()
    ast = Parser(tokens).parse_program()
    SemanticAnalyzer(ast).check()
    py = generate_python(ast)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(py, {})
    return py, buf.getvalue()

# --------------------------
# CLI / REPL
# --------------------------

def repl():
    print("Sequentia REPL - enter lines, empty line to execute block. Ctrl-C to exit.")
    lines: List[str] = []
    try:
        while True:
            line = input('>>> ')
            if line.strip() == '':
                if not lines:
                    continue
                source = '\n'.join(lines) + '\n'
                try:
                    py, out = compile_and_run(source)
                    print('--- Generated Python ---')
                    print(py)
                    print('--- Output ---')
                    print(out, end='')
                except Exception as e:
                    print('Error:', e)
                lines = []
            else:
                lines.append(line)
    except KeyboardInterrupt:
        print('\nExiting REPL.')

def run_file(path: str):
    with open(path, 'r') as f:
        src = f.read()
    try:
        py, out = compile_and_run(src)
    except Exception as e:
        print('Compilation / execution error:')
        print(str(e))
        import traceback
        traceback.print_exc()
        return
    print('--- Generated Python ---')
    print(py)
    print('--- Program Output ---')
    print(out, end='')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        repl()
    else:
        run_file(sys.argv[1])
