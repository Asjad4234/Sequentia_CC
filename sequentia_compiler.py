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
    'triangular': 'TRI_KW'
}

SINGLE = {
    '=': 'ASSIGN',
    ',': 'COMMA',
    '[': 'LBRACKET',
    ']': 'RBRACKET'
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
        raise Exception("Invalid statement start " + str(tok))

    def parse_expr(self):
        tok = self.peek()

        # pattern expression
        if tok[0] == "PATTERN_KW":
            self.advance()
            pname = self.expect_any_pattern()
            args = [self.parse_expr()]
            while self.peek()[0] == "COMMA":
                self.advance()
                args.append(self.parse_expr())
            return PatternExpr(pname, args)

        # number literal
        if tok[0] == 'NUMBER':
            return NumberExpr(int(self.advance()[1]))

        # ID or array access
        if tok[0] == 'ID':
            name = self.advance()[1]
            # Check for array indexing
            if self.peek()[0] == 'LBRACKET':
                self.advance()
                idx_expr = self.parse_expr()
                self.expect('RBRACKET')
                return ArrayAccessExpr(name, idx_expr)
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
        name = self.expect('ID')[1]

        if self.peek()[0] == 'LBRACKET':
            self.advance()
            idx_expr = self.parse_expr()
            self.expect('RBRACKET')
            return Print(name, idx_expr)

        return Print(name)


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
            if isinstance(expr.index_expr, NumberExpr):
                pass  # Static index, valid
            elif isinstance(expr.index_expr, IDExpr):
                if expr.index_expr.name not in self.sym:
                    raise Exception("Undefined index variable " + expr.index_expr.name)
                if self.sym[expr.index_expr.name].type != "int":
                    raise Exception("Index must be integer")
            else:
                raise Exception("Invalid index expression")
            # Result is an integer
            self.sym[stmt.name] = Symbol(stmt.name, "int")
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

        # Case 2: pattern expression
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
        if stmt.name not in self.sym:
            raise Exception("Undefined variable in print " + stmt.name)

        # Allow printing both scalars and arrays
        if stmt.index_expr:
            # print x[n]
            if isinstance(stmt.index_expr, NumberExpr):
                return

            if isinstance(stmt.index_expr, IDExpr):
                if stmt.index_expr.name not in self.sym:
                    raise Exception("Undefined index variable " + stmt.index_expr.name)
                if self.sym[stmt.index_expr.name].type != "int":
                    raise Exception("Index must be integer variable")
                return

            raise Exception("Invalid index")


# --------------------------
# Code Generation
# --------------------------

def py_expr(expr):
    if isinstance(expr, NumberExpr): return str(expr.value)
    if isinstance(expr, IDExpr): return expr.name
    if isinstance(expr, ArrayAccessExpr):
        idx = py_expr(expr.index_expr)
        return f"{expr.name}[{idx}]"
    raise Exception("Invalid scalar expr")

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


def generate_python(ast):
    code = ["# Generated Python Code"]
    for stmt in ast.stmts:

        # scalar assignment from number
        if isinstance(stmt, Assign) and isinstance(stmt.expr, NumberExpr):
            code.append(f"{stmt.name} = {stmt.expr.value}")
            continue

        # array element access assignment: y = x[2]
        if isinstance(stmt, Assign) and isinstance(stmt.expr, ArrayAccessExpr):
            code.append(f"{stmt.name} = {py_expr(stmt.expr)}")
            continue

        # ID assignment (scalar or array copy)
        if isinstance(stmt, Assign) and isinstance(stmt.expr, IDExpr):
            code.append(f"{stmt.name} = {stmt.expr.name}")
            continue

        # pattern expression
        if isinstance(stmt, Assign) and isinstance(stmt.expr, PatternExpr):
            p = stmt.expr
            code.append(gen_pattern(stmt.name, p.pattern_name, p.args))
            continue

        # print
        if isinstance(stmt, Print):
            if stmt.index_expr:
                code.append(f"print({stmt.name}[{py_expr(stmt.index_expr)}])")
            else:
                # Check if printing scalar or array - need to look at context
                # For simplicity, try array-style print, fallback handled in execution
                code.append(f"print({stmt.name} if isinstance({stmt.name}, int) else ' '.join(str(x) for x in {stmt.name}))")

    return "\n".join(code)


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
        print(e)
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
