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

            if ch == "#":
                while self.peek() and self.peek() not in "\n":
                    self.advance()
                continue

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

            if self.pos + 1 < len(self.text):
                two_char = ch + self.text[self.pos + 1]
                if two_char in DOUBLE:
                    out.append((DOUBLE[two_char], two_char))
                    self.advance()
                    self.advance()
                    continue

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
    def __repr__(self): return f"Program({len(self.stmts)} statements)"

class Assign:
    def __init__(self, name, expr): 
        self.name = name
        self.expr = expr
    def __repr__(self): return f"Assign({self.name}, {self.expr})"

class PatternExpr:
    def __init__(self, pattern_name, args):
        self.pattern_name = pattern_name
        self.args = args
    def __repr__(self): return f"PatternExpr({self.pattern_name}, {self.args})"

class NumberExpr:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"NumberExpr({self.value})"

class IDExpr:
    def __init__(self, name): self.name = name
    def __repr__(self): return f"IDExpr({self.name})"

class ArrayAccessExpr:
    def __init__(self, name, index_expr):
        self.name = name
        self.index_expr = index_expr
    def __repr__(self): return f"ArrayAccessExpr({self.name}, {self.index_expr})"

class SliceExpr:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end
    def __repr__(self): return f"SliceExpr({self.name}, {self.start}, {self.end})"

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self): return f"BinOp({self.left}, '{self.op}', {self.right})"

class IfStmt:
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
    def __repr__(self): return f"IfStmt({self.condition}, {len(self.true_block)} stmts, {len(self.false_block) if self.false_block else 0} else stmts)"

class ForStmt:
    def __init__(self, iterator, source, body):
        self.iterator = iterator
        self.source = source
        self.body = body
    def __repr__(self): return f"ForStmt({self.iterator} in {self.source}, {len(self.body)} stmts)"

class Print:
    def __init__(self, name, index_expr=None):
        self.name = name
        self.index_expr = index_expr
    def __repr__(self): return f"Print({self.name}, {self.index_expr})"

# --------------------------
# Parser (Recursive Descent - Top-Down)
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

        if tok[0] == 'LPAREN':
            self.advance()
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr

        if tok[0] == "PATTERN_KW":
            self.advance()
            pname = self.expect_any_pattern()
            args = [self.parse_additive()]
            while self.peek()[0] == "COMMA":
                self.advance()
                args.append(self.parse_additive())
            return PatternExpr(pname, args)

        if tok[0] == 'NUMBER':
            return NumberExpr(int(self.advance()[1]))

        if tok[0] == 'ID':
            name = self.advance()[1]
            if self.peek()[0] == 'LBRACKET':
                self.advance()
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
        if isinstance(expr, IDExpr):
            return Print(expr.name)
        elif isinstance(expr, ArrayAccessExpr):
            return Print(expr.name, expr.index_expr)
        else:
            return Print("_expr_", expr)

    def parse_if(self):
        self.expect('IF_KW')
        condition = self.parse_expr()
        self.expect('LBRACE')
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
        if isinstance(source_expr, IDExpr):
            source = source_expr.name
        else:
            source = source_expr
        
        self.expect('LBRACE')
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
        self.type = sym_type
        self.length = length
        self.pattern = pattern
        self.args = args
    
    def __repr__(self):
        if self.type == "array":
            return f"Symbol({self.name}, type={self.type}, length={self.length}, pattern={self.pattern})"
        return f"Symbol({self.name}, type={self.type})"

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
            return None
        raise Exception("Unsupported scalar expression")

    def check_assign(self, stmt):
        expr = stmt.expr

        if isinstance(expr, NumberExpr):
            self.sym[stmt.name] = Symbol(stmt.name, "int")
            return

        if isinstance(expr, ArrayAccessExpr):
            if expr.name not in self.sym:
                raise Exception("Undefined array " + expr.name)
            if self.sym[expr.name].type != "array":
                raise Exception(expr.name + " is not an array")
            self.check_expr_type(expr.index_expr, "int")
            self.sym[stmt.name] = Symbol(stmt.name, "int")
            return

        if isinstance(expr, SliceExpr):
            if expr.name not in self.sym:
                raise Exception("Undefined array " + expr.name)
            if self.sym[expr.name].type != "array":
                raise Exception(expr.name + " is not an array")
            if expr.start:
                self.check_expr_type(expr.start, "int")
            if expr.end:
                self.check_expr_type(expr.end, "int")
            
            # Try to compute slice length statically
            computed_length = None
            if isinstance(expr.start, NumberExpr) and isinstance(expr.end, NumberExpr):
                computed_length = expr.end.value - expr.start.value
            elif expr.start is None and isinstance(expr.end, NumberExpr):
                # [:5] means [0:5], length = 5
                computed_length = expr.end.value
            elif isinstance(expr.start, NumberExpr) and expr.end is None:
                # [2:] means from 2 to end, length depends on source array
                src_len = self.sym[expr.name].length
                if src_len is not None:
                    computed_length = src_len - expr.start.value
            
            self.sym[stmt.name] = Symbol(stmt.name, "array", length=computed_length)
            return

        if isinstance(expr, IDExpr):
            if expr.name not in self.sym:
                raise Exception("Undefined source variable " + expr.name)
            src_sym = self.sym[expr.name]
            if src_sym.type == "int":
                self.sym[stmt.name] = Symbol(stmt.name, "int")
            else:
                self.sym[stmt.name] = Symbol(stmt.name, "array", 
                                             length=src_sym.length,
                                             pattern=src_sym.pattern,
                                             args=src_sym.args)
            return

        if isinstance(expr, BinOp):
            result_type = self.check_binop(expr)
            # Try to preserve length information for array operations
            length = None
            if result_type == "array":
                # If left operand is array, use its length
                if isinstance(expr.left, IDExpr) and expr.left.name in self.sym:
                    if self.sym[expr.left.name].type == "array":
                        length = self.sym[expr.left.name].length
                # If right operand is array and left isn't, use right's length
                elif isinstance(expr.right, IDExpr) and expr.right.name in self.sym:
                    if self.sym[expr.right.name].type == "array":
                        length = self.sym[expr.right.name].length
            self.sym[stmt.name] = Symbol(stmt.name, result_type, length=length)
            return

        if isinstance(expr, PatternExpr):
            lengths = []
            for arg in expr.args:
                if isinstance(arg, NumberExpr):
                    lengths.append(arg.value)
                elif isinstance(arg, IDExpr):
                    if arg.name not in self.sym:
                        raise Exception("Undefined scalar variable " + arg.name)
                    if self.sym[arg.name].type != "int":
                        raise Exception("Pattern argument must be integer variable")
                    lengths.append(None)
                elif isinstance(arg, ArrayAccessExpr):
                    if arg.name not in self.sym:
                        raise Exception("Undefined array " + arg.name)
                    if self.sym[arg.name].type != "array":
                        raise Exception(arg.name + " is not an array")
                    if isinstance(arg.index_expr, IDExpr):
                        if arg.index_expr.name not in self.sym:
                            raise Exception("Undefined index variable " + arg.index_expr.name)
                        if self.sym[arg.index_expr.name].type != "int":
                            raise Exception("Index must be integer")
                    lengths.append(None)
                else:
                    raise Exception("Invalid pattern argument")

            self.sym[stmt.name] = Symbol(stmt.name, "array", length=lengths[-1],
                                         pattern=expr.pattern_name, args=expr.args)
            return

        raise Exception("Invalid assignment expression")

    def check_print(self, stmt):
        if stmt.name == "_expr_":
            self.check_expr_type(stmt.index_expr, None)
            return
        
        if stmt.name not in self.sym:
            raise Exception("Undefined variable in print " + stmt.name)

        if stmt.index_expr:
            self.check_expr_type(stmt.index_expr, "int")

    def check_expr_type(self, expr, expected_type=None):
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
            for arg in expr.args:
                self.check_expr_type(arg, None)
            actual = "array"
        else:
            raise Exception("Unknown expression type")
        
        if expected_type and actual != expected_type and expected_type is not None:
            raise Exception(f"Type mismatch: expected {expected_type}, got {actual}")
        
        return actual

    def check_binop(self, expr):
        left_type = self.check_expr_type(expr.left, None)
        right_type = self.check_expr_type(expr.right, None)
        
        if expr.op in ['==', '!=', '<', '>', '<=', '>=']:
            return "int"
        
        if left_type == "array" or right_type == "array":
            return "array"
        return "int"

    def check_if(self, stmt):
        self.check_expr_type(stmt.condition, None)
        
        for s in stmt.true_block:
            if isinstance(s, Assign):
                self.check_assign(s)
            elif isinstance(s, Print):
                self.check_print(s)
            elif isinstance(s, IfStmt):
                self.check_if(s)
            elif isinstance(s, ForStmt):
                self.check_for(s)
        
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
        if isinstance(stmt.source, str):
            if stmt.source not in self.sym:
                raise Exception("Undefined variable in for loop: " + stmt.source)
            if self.sym[stmt.source].type != "array":
                raise Exception("For loop source must be an array")
        else:
            source_type = self.check_expr_type(stmt.source, None)
            if source_type != "array":
                raise Exception("For loop source must be an array")
        
        self.sym[stmt.iterator] = Symbol(stmt.iterator, "int")
        
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
# Three-Address Code Generator
# --------------------------

class TACInstruction:
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
    
    def __repr__(self):
        if self.op in ['PATTERN_CALL']:
            return f"{self.result} = CALL {self.arg1}({self.arg2})"
        elif self.op in ['ARRAY_ACCESS']:
            return f"{self.result} = {self.arg1}[{self.arg2}]"
        elif self.op in ['SLICE']:
            return f"{self.result} = {self.arg1}[{self.arg2}]"
        elif self.op in ['ASSIGN']:
            return f"{self.result} = {self.arg1}"
        elif self.op in ['PRINT']:
            return f"PRINT {self.arg1}"
        elif self.op in ['LABEL']:
            return f"{self.arg1}:"
        elif self.op in ['GOTO']:
            return f"GOTO {self.arg1}"
        elif self.op in ['IF_FALSE']:
            return f"IF_FALSE {self.arg1} GOTO {self.result}"
        elif self.op in ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=']:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        else:
            return f"{self.op} {self.arg1} {self.arg2} {self.result}"

class TACGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def generate(self):
        for stmt in self.ast.stmts:
            self.gen_stmt(stmt)
        return self.instructions
    
    def gen_stmt(self, stmt):
        if isinstance(stmt, Assign):
            if isinstance(stmt.expr, PatternExpr):
                args_str = ', '.join([self.gen_expr(arg) for arg in stmt.expr.args])
                self.instructions.append(TACInstruction('PATTERN_CALL', stmt.expr.pattern_name, args_str, stmt.name))
            else:
                temp = self.gen_expr(stmt.expr)
                self.instructions.append(TACInstruction('ASSIGN', temp, None, stmt.name))
        
        elif isinstance(stmt, Print):
            if stmt.name == "_expr_":
                temp = self.gen_expr(stmt.index_expr)
                self.instructions.append(TACInstruction('PRINT', temp))
            elif stmt.index_expr:
                idx = self.gen_expr(stmt.index_expr)
                temp = self.new_temp()
                self.instructions.append(TACInstruction('ARRAY_ACCESS', stmt.name, idx, temp))
                self.instructions.append(TACInstruction('PRINT', temp))
            else:
                self.instructions.append(TACInstruction('PRINT', stmt.name))
        
        elif isinstance(stmt, IfStmt):
            cond_temp = self.gen_expr(stmt.condition)
            else_label = self.new_label()
            end_label = self.new_label()
            
            self.instructions.append(TACInstruction('IF_FALSE', cond_temp, None, else_label))
            
            for s in stmt.true_block:
                self.gen_stmt(s)
            
            self.instructions.append(TACInstruction('GOTO', end_label))
            self.instructions.append(TACInstruction('LABEL', else_label))
            
            if stmt.false_block:
                for s in stmt.false_block:
                    self.gen_stmt(s)
            
            self.instructions.append(TACInstruction('LABEL', end_label))
        
        elif isinstance(stmt, ForStmt):
            # For loop TAC generation (simplified)
            loop_label = self.new_label()
            end_label = self.new_label()
            
            self.instructions.append(TACInstruction('LABEL', loop_label))
            # Body
            for s in stmt.body:
                self.gen_stmt(s)
            self.instructions.append(TACInstruction('LABEL', end_label))
    
    def gen_expr(self, expr):
        if isinstance(expr, NumberExpr):
            return str(expr.value)
        
        elif isinstance(expr, IDExpr):
            return expr.name
        
        elif isinstance(expr, ArrayAccessExpr):
            idx = self.gen_expr(expr.index_expr)
            temp = self.new_temp()
            self.instructions.append(TACInstruction('ARRAY_ACCESS', expr.name, idx, temp))
            return temp
        
        elif isinstance(expr, SliceExpr):
            start = self.gen_expr(expr.start) if expr.start else "0"
            end = self.gen_expr(expr.end) if expr.end else "None"
            temp = self.new_temp()
            # Use SLICE instruction with format: result = array[start:end]
            self.instructions.append(TACInstruction('SLICE', expr.name, f"{start}:{end}", temp))
            return temp
        
        elif isinstance(expr, BinOp):
            left = self.gen_expr(expr.left)
            right = self.gen_expr(expr.right)
            temp = self.new_temp()
            self.instructions.append(TACInstruction(expr.op, left, right, temp))
            return temp
        
        elif isinstance(expr, PatternExpr):
            args_str = ', '.join([self.gen_expr(arg) for arg in expr.args])
            temp = self.new_temp()
            self.instructions.append(TACInstruction('PATTERN_CALL', expr.pattern_name, args_str, temp))
            return temp
        
        else:
            return "unknown"


# --------------------------
# Code Optimizer
# --------------------------

class Optimizer:
    def __init__(self, tac_instructions):
        self.instructions = tac_instructions
    
    def optimize(self):
        # Apply optimization passes
        self.constant_folding()
        self.copy_propagation()
        self.dead_code_elimination()
        # Run copy propagation again after DCE to catch new opportunities
        self.copy_propagation()
        # Final cleanup pass
        self.remove_redundant_constant_assigns()
        return self.instructions
    
    def remove_redundant_constant_assigns(self):
        """Remove t1 = 8; a = 8 patterns, keeping only a = 8"""
        optimized = []
        skip_next = set()
        
        for i, instr in enumerate(self.instructions):
            if i in skip_next:
                continue
            
            # Check for pattern: t_x = const; var = const (where const is same)
            if (instr.op == 'ASSIGN' and 
                instr.result.startswith('t') and 
                str(instr.arg1).isdigit()):
                # Look ahead to see if next instruction assigns same value
                if i + 1 < len(self.instructions):
                    next_instr = self.instructions[i + 1]
                    if (next_instr.op == 'ASSIGN' and 
                        next_instr.arg1 == instr.arg1 and
                        not next_instr.result.startswith('t')):
                        # Skip the temp assignment, keep the variable assignment
                        skip_next.add(i)
                        continue
            
            optimized.append(instr)
        
        self.instructions = optimized
    
    def constant_folding(self):
        """Fold constant expressions"""
        optimized = []
        for instr in self.instructions:
            if instr.op in ['+', '-', '*', '/'] and instr.arg1.isdigit() and instr.arg2.isdigit():
                val1 = int(instr.arg1)
                val2 = int(instr.arg2)
                if instr.op == '+':
                    result = val1 + val2
                elif instr.op == '-':
                    result = val1 - val2
                elif instr.op == '*':
                    result = val1 * val2
                elif instr.op == '/':
                    result = val1 // val2
                optimized.append(TACInstruction('ASSIGN', str(result), None, instr.result))
            else:
                optimized.append(instr)
        self.instructions = optimized
    
    def dead_code_elimination(self):
        """Remove unused variables and their assignments"""
        # First pass: collect ALL used variables (those that appear in operations or prints)
        used_vars = set()
        
        for instr in self.instructions:
            # Variables used in PRINT statements are essential
            if instr.op == 'PRINT':
                if instr.arg1:
                    used_vars.add(instr.arg1)
            # Variables used in conditionals
            elif instr.op == 'IF_FALSE':
                if instr.arg1:
                    used_vars.add(instr.arg1)
            # Variables used in operations (left and right operands)
            elif instr.op in ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=']:
                if instr.arg1 and not str(instr.arg1).isdigit():
                    used_vars.add(instr.arg1)
                if instr.arg2 and not str(instr.arg2).isdigit():
                    used_vars.add(instr.arg2)
            # Variables used in array operations
            elif instr.op in ['ARRAY_ACCESS', 'SLICE']:
                if instr.arg1:
                    used_vars.add(instr.arg1)
            # Variables used in assignments (right-hand side)
            elif instr.op == 'ASSIGN':
                if instr.arg1 and not str(instr.arg1).isdigit():
                    used_vars.add(instr.arg1)
        
        # Second pass: recursively find dependencies
        # If variable X is used, and X = Y, then Y is also used
        changed = True
        while changed:
            changed = False
            for instr in self.instructions:
                if instr.result in used_vars:
                    # If we're using the result, we need the arguments
                    if instr.arg1 and not str(instr.arg1).isdigit():
                        if instr.arg1 not in used_vars:
                            used_vars.add(instr.arg1)
                            changed = True
                    if instr.arg2 and not str(instr.arg2).isdigit() and ':' not in str(instr.arg2):
                        if instr.arg2 not in used_vars:
                            used_vars.add(instr.arg2)
                            changed = True
        
        # Third pass: keep only instructions needed for used variables
        optimized = []
        for instr in self.instructions:
            # Always keep side effects (PRINT, labels, control flow)
            if instr.op in ['PRINT', 'LABEL', 'GOTO', 'IF_FALSE', 'PATTERN_CALL']:
                optimized.append(instr)
            # Keep assignments only if the result is used
            elif instr.result and instr.result in used_vars:
                optimized.append(instr)
        
        self.instructions = optimized
    
    def copy_propagation(self):
        """Propagate copies and eliminate redundant assignments"""
        optimized = []
        temp_to_value = {}  # Maps temps to their values
        
        for instr in self.instructions:
            # Track what each temp holds
            if instr.op == 'ASSIGN' and instr.result.startswith('t'):
                temp_to_value[instr.result] = instr.arg1
            
            # If we're assigning from a temp to a variable, use the temp's value directly
            if instr.op == 'ASSIGN' and instr.arg1 in temp_to_value:
                # Bypass the temp: var = temp → var = temp_value
                instr.arg1 = temp_to_value[instr.arg1]
            
            # Replace temp uses in operations
            if instr.arg1 in temp_to_value:
                instr.arg1 = temp_to_value[instr.arg1]
            if instr.arg2 in temp_to_value and ':' not in str(instr.arg2):
                instr.arg2 = temp_to_value[instr.arg2]
            
            optimized.append(instr)
        
        self.instructions = optimized


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
        if expr.op == '+':
            return f"_pat_add({left}, {right})"
        elif expr.op == '-':
            return f"_pat_sub({left}, {right})"
        elif expr.op == '*':
            return f"_pat_mul({left}, {right})"
        elif expr.op == '/':
            return f"_pat_div({left}, {right})"
        else:
            return f"({left} {expr.op} {right})"
    if isinstance(expr, PatternExpr):
        return gen_pattern_inline(expr.pattern_name, expr.args)
    raise Exception("Invalid expression")

def gen_pattern_inline(pattern, args):
    arg_values = [py_expr(a) for a in args]
    
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
    
    if pattern == "fibonacci":
        n = arg_values[0]
        return f"_fib_inline({n})"
    
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
    indent = "    " * indent_level
    code = []
    
    if isinstance(stmt, Assign):
        if isinstance(stmt.expr, PatternExpr):
            p = stmt.expr
            pattern_code = gen_pattern(stmt.name, p.pattern_name, p.args)
            for line in pattern_code.strip().split('\n'):
                if line.strip():
                    code.append(indent + line)
        else:
            code.append(f"{indent}{stmt.name} = {py_expr(stmt.expr)}")
    
    elif isinstance(stmt, Print):
        if stmt.name == "_expr_":
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
# Helper Functions for Output Formatting
# --------------------------

def format_tokens(tokens):
    output = ["=" * 70]
    output.append("LEXER OUTPUT (Tokens)")
    output.append("=" * 70)
    for i, (token_type, token_value) in enumerate(tokens):
        if token_type == "NEWLINE":
            output.append(f"{i:3d}. {token_type:<15} '\\n'")
        elif token_type == "EOF":
            output.append(f"{i:3d}. {token_type:<15} (end of file)")
        else:
            output.append(f"{i:3d}. {token_type:<15} '{token_value}'")
    output.append("")
    return "\n".join(output)

def format_syntax_tree(ast, indent=0):
    """Format concrete syntax tree"""
    lines = []
    prefix = "│   " * indent
    last_prefix = "└── "
    mid_prefix = "├── "
    
    if isinstance(ast, Program):
        lines.append(f"{prefix}Program")
        for i, stmt in enumerate(ast.stmts):
            is_last = (i == len(ast.stmts) - 1)
            lines.extend(format_syntax_tree(stmt, indent))
    
    elif isinstance(ast, Assign):
        lines.append(f"{prefix}{last_prefix}Assignment")
        lines.append(f"{prefix}    {mid_prefix}Identifier: {ast.name}")
        lines.append(f"{prefix}    {last_prefix}Expression:")
        lines.extend(format_syntax_tree(ast.expr, indent + 2))
    
    elif isinstance(ast, Print):
        lines.append(f"{prefix}{last_prefix}Print Statement")
        if stmt.name == "_expr_":
            lines.extend(format_syntax_tree(ast.index_expr, indent + 1))
        else:
            lines.append(f"{prefix}    {last_prefix}Variable: {ast.name}")
    
    elif isinstance(ast, PatternExpr):
        lines.append(f"{prefix}    {last_prefix}Pattern: {ast.pattern_name}")
        for arg in ast.args:
            lines.extend(format_syntax_tree(arg, indent + 2))
    
    elif isinstance(ast, NumberExpr):
        lines.append(f"{prefix}        {last_prefix}Number: {ast.value}")
    
    elif isinstance(ast, IDExpr):
        lines.append(f"{prefix}        {last_prefix}Identifier: {ast.name}")
    
    elif isinstance(ast, BinOp):
        lines.append(f"{prefix}    {last_prefix}BinaryOp: {ast.op}")
        lines.extend(format_syntax_tree(ast.left, indent + 2))
        lines.extend(format_syntax_tree(ast.right, indent + 2))
    
    return lines

def format_ast(ast, indent=0):
    """Format abstract syntax tree"""
    lines = []
    prefix = "  " * indent
    
    if isinstance(ast, Program):
        lines.append(f"{prefix}Program:")
        for stmt in ast.stmts:
            lines.extend(format_ast(stmt, indent + 1))
    elif isinstance(ast, Assign):
        lines.append(f"{prefix}Assign: {ast.name} =")
        lines.extend(format_ast(ast.expr, indent + 1))
    elif isinstance(ast, Print):
        if ast.name == "_expr_":
            lines.append(f"{prefix}Print:")
            lines.extend(format_ast(ast.index_expr, indent + 1))
        elif ast.index_expr:
            lines.append(f"{prefix}Print: {ast.name}[index]")
            lines.extend(format_ast(ast.index_expr, indent + 1))
        else:
            lines.append(f"{prefix}Print: {ast.name}")
    elif isinstance(ast, PatternExpr):
        lines.append(f"{prefix}PatternExpr: {ast.pattern_name}")
        for arg in ast.args:
            lines.extend(format_ast(arg, indent + 1))
    elif isinstance(ast, NumberExpr):
        lines.append(f"{prefix}Number: {ast.value}")
    elif isinstance(ast, IDExpr):
        lines.append(f"{prefix}ID: {ast.name}")
    elif isinstance(ast, ArrayAccessExpr):
        lines.append(f"{prefix}ArrayAccess: {ast.name}[index]")
        lines.extend(format_ast(ast.index_expr, indent + 1))
    elif isinstance(ast, SliceExpr):
        lines.append(f"{prefix}Slice: {ast.name}[{ast.start}:{ast.end}]")
        if ast.start:
            lines.append(f"{prefix}  Start:")
            lines.extend(format_ast(ast.start, indent + 2))
        if ast.end:
            lines.append(f"{prefix}  End:")
            lines.extend(format_ast(ast.end, indent + 2))
    elif isinstance(ast, BinOp):
        lines.append(f"{prefix}BinOp: {ast.op}")
        lines.append(f"{prefix}  Left:")
        lines.extend(format_ast(ast.left, indent + 2))
        lines.append(f"{prefix}  Right:")
        lines.extend(format_ast(ast.right, indent + 2))
    elif isinstance(ast, IfStmt):
        lines.append(f"{prefix}If:")
        lines.append(f"{prefix}  Condition:")
        lines.extend(format_ast(ast.condition, indent + 2))
        lines.append(f"{prefix}  Then:")
        for stmt in ast.true_block:
            lines.extend(format_ast(stmt, indent + 2))
        if ast.false_block:
            lines.append(f"{prefix}  Else:")
            for stmt in ast.false_block:
                lines.extend(format_ast(stmt, indent + 2))
    elif isinstance(ast, ForStmt):
        lines.append(f"{prefix}For: {ast.iterator} in {ast.source}")
        lines.append(f"{prefix}  Body:")
        for stmt in ast.body:
            lines.extend(format_ast(stmt, indent + 2))
    else:
        lines.append(f"{prefix}{type(ast).__name__}: {ast}")
    
    return lines

def format_symbol_table(symbol_table):
    output = ["=" * 70]
    output.append("SYMBOL TABLE")
    output.append("=" * 70)
    output.append(f"{'Variable':<15} {'Type':<10} {'Length':<10} {'Pattern':<15}")
    output.append("-" * 70)
    
    for name, symbol in symbol_table.items():
        # For integers, don't show length at all (use '-')
        if symbol.type == "int":
            length_str = "-"
        # For arrays, show actual length or 'dynamic' if unknown
        else:
            length_str = str(symbol.length) if symbol.length is not None else "dynamic"
        
        pattern_str = symbol.pattern if symbol.pattern else "-"
        output.append(f"{name:<15} {symbol.type:<10} {length_str:<10} {pattern_str:<15}")
    
    output.append("")
    return "\n".join(output)

def format_tac(tac_instructions):
    output = ["=" * 70]
    output.append("THREE-ADDRESS CODE (TAC)")
    output.append("=" * 70)
    for i, instr in enumerate(tac_instructions):
        output.append(f"{i:3d}. {str(instr)}")
    output.append("")
    return "\n".join(output)

def format_optimizations(original_tac, optimized_tac):
    output = ["=" * 70]
    output.append("CODE OPTIMIZATION")
    output.append("=" * 70)
    output.append(f"Original TAC instructions: {len(original_tac)}")
    output.append(f"Optimized TAC instructions: {len(optimized_tac)}")
    output.append(f"Reduction: {len(original_tac) - len(optimized_tac)} instructions")
    output.append("")
    # output.append("Optimizations applied:")
    # output.append("  1. Constant Folding")
    # output.append("  2. Dead Code Elimination")
    # output.append("  3. Copy Propagation")
    # output.append("")
    return "\n".join(output)


# --------------------------
# Compiler Driver
# --------------------------

def compile_and_run(src):
    # Lexical Analysis
    lexer = Lexer(src)
    tokens = lexer.tokens()
    
    # Parsing
    parser = Parser(tokens)
    ast = parser.parse_program()
    
    # Semantic Analysis
    analyzer = SemanticAnalyzer(ast)
    analyzer.check()
    
    # Three-Address Code Generation
    tac_gen = TACGenerator(ast)
    original_tac = tac_gen.generate()
    
    # Code Optimization
    optimizer = Optimizer(list(original_tac))
    optimized_tac = optimizer.optimize()
    
    # Final Code Generation
    py = generate_python(ast)

    # Execute
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(py, {})
    
    return tokens, ast, analyzer.sym, original_tac, optimized_tac, py, buf.getvalue()

# --------------------------
# CLI / REPL
# --------------------------

def repl():
    print("=" * 70)
    print("SEQUENTIA COMPILER - REPL Mode")
    print("=" * 70)
    print("Parser Type: Recursive Descent (Top-Down Parser)")
    print("Features: Lexer → Parser → Semantic Analysis → TAC → Optimization")
    print("")
    print("Enter lines, empty line to execute block. Ctrl-C to exit.")
    print("Note: Use 'print x' to display variable values")
    print("=" * 70)
    print("")
    
    lines: List[str] = []
    try:
        while True:
            line = input('>>> ')
            if line.strip() == '':
                if not lines:
                    continue
                source = '\n'.join(lines) + '\n'
                try:
                    tokens, ast, sym_table, original_tac, optimized_tac, py, out = compile_and_run(source)
                    
                    # Print Lexer Output
                    print(format_tokens(tokens))
                    
                    # Print AST
                    print("=" * 70)
                    print("ABSTRACT SYNTAX TREE (AST)")
                    print("=" * 70)
                    print("\n".join(format_ast(ast)))
                    print()
                    
                    # Print Symbol Table
                    print(format_symbol_table(sym_table))
                    
                    # Print TAC
                    print(format_tac(original_tac))
                    
                    # Print Optimizations
                    print(format_optimizations(original_tac, optimized_tac))
                    
                    # Print Optimized TAC
                    print("=" * 70)
                    print("OPTIMIZED THREE-ADDRESS CODE")
                    print("=" * 70)
                    for i, instr in enumerate(optimized_tac):
                        print(f"{i:3d}. {str(instr)}")
                    print()
                    
                    # Print Program Output
                    print("=" * 70)
                    print("PROGRAM OUTPUT")
                    print("=" * 70)
                    if out:
                        print(out, end='')
                    else:
                        print("(no output - use 'print' statement to display values)")
                    print()
                    
                except Exception as e:
                    print('Error:', e)
                    import traceback
                    traceback.print_exc()
                lines = []
            else:
                lines.append(line)
    except KeyboardInterrupt:
        print('\nExiting REPL.')

def run_file(path: str):
    with open(path, 'r') as f:
        src = f.read()
    try:
        tokens, ast, sym_table, original_tac, optimized_tac, py, out = compile_and_run(src)
    except Exception as e:
        print('Compilation / execution error:')
        print(str(e))
        import traceback
        traceback.print_exc()
        return
    
    # Print Lexer Output
    print(format_tokens(tokens))
    
    # Print AST
    print("=" * 70)
    print("ABSTRACT SYNTAX TREE (AST)")
    print("=" * 70)
    print("\n".join(format_ast(ast)))
    print()
    
    # Print Symbol Table
    print(format_symbol_table(sym_table))
    
    # Print TAC
    print(format_tac(original_tac))
    
    # Print Optimizations
    print(format_optimizations(original_tac, optimized_tac))
    
    # Print Optimized TAC
    print("=" * 70)
    print("OPTIMIZED THREE-ADDRESS CODE")
    print("=" * 70)
    for i, instr in enumerate(optimized_tac):
        print(f"{i:3d}. {str(instr)}")
    print()
    
    # Print Program Output
    print("=" * 70)
    print("PROGRAM OUTPUT")
    print("=" * 70)
    print(out, end='')
    print()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        repl()
    else:
        run_file(sys.argv[1])