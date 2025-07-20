import shlex

# === Your source code in the mini language ===
temp_code = """
fnc greet name
    print name
end

let i = 0

while i < 10
    let i = i + 1
    if i > 6
        greet "hi from loop"
    end
end

greet "Buh bye"
"""

# === Tokenize code into list of tokens per line ===
def tokenize_lines(code: str):
    return [shlex.split(line, posix=False) for line in code.strip().splitlines()]

# === Parse an expression ===
def parse_expr(tokens):

    if len(tokens) == 1:
        token = tokens[0]

        if token.startswith('"') and token.endswith('"'):
            return ("string", token[1:-1])
        
        try:
            return int(token)
        except ValueError:
            return token
        
    elif len(tokens) == 3:
        a, op, b = tokens
        return (op, parse_expr([a]), parse_expr([b]))
    else:
        joined = " ".join(tokens)
        if joined.startswith('"') and joined.endswith('"'):
            return ('string', joined[1:-1])
        try:
            return int(token)
        except ValueError:
            return token
        raise Exception("Can't parse that expression yet.")

# === Parse a block of code into an AST ===
def parse_block(lines, i=0):
    ast = []

    while i < len(lines):
        tokens = lines[i]
        if not tokens:
            i += 1
            continue

        cmd = tokens[0]

        if cmd == 'let':
            ast.append(('assign', tokens[1], parse_expr(tokens[3:])))
            i += 1

        elif cmd == 'print':
            ast.append(('print', parse_expr(tokens[1:])))
            i += 1

        elif cmd == 'if':
            condition = parse_expr(tokens[1:])
            body, i = parse_block(lines, i + 1)
            ast.append(('if', condition, body))

        elif cmd == 'while':
            condition = parse_expr(tokens[1:])
            body, i = parse_block(lines, i + 1)
            ast.append(('while', condition, body))

        elif cmd == 'fnc':
            name = tokens[1]
            args = tokens[2:]
            body, i = parse_block(lines, i + 1)
            ast.append(('fnc', name, args, body))

        elif cmd == 'end':
            return ast, i + 1
        
        else:
            arg_exprs = [parse_expr([arg]) for arg in tokens[1:]]
            ast.append(('call', cmd, arg_exprs))
            i += 1

    return ast, i

# === Evaluate an expression ===
def eval_expr(expr, env):
    if isinstance(expr, int):
        return expr
    
    if isinstance(expr, tuple) and expr[0] == "string":
        return expr[1]
    
    if isinstance(expr, str) and expr in env:
        return env[expr]
    
    if isinstance(expr, str):
        raise Exception(f"Idk this variable: {expr}")

    op, a, b = expr
    a_val = eval_expr(a, env)
    b_val = eval_expr(b, env)

    if op == '+': return a_val + b_val
    elif op == '-': return a_val - b_val
    elif op == '*': return a_val * b_val
    elif op == '/': return a_val // b_val
    elif op == '%': return a_val % b_val
    elif op == '<': return a_val < b_val
    elif op == '>': return a_val > b_val
    elif op == '<=': return a_val <= b_val
    elif op == '>=': return a_val >= b_val
    elif op == '==': return a_val == b_val
    else: raise Exception(f"Unknown operator: {op}")

# === Function table ===
functions = {}

# === Execute a single statement ===
def run_stmt(stmt, env):
    kind = stmt[0]

    if kind == 'assign':
        _, name, expr = stmt
        env[name] = eval_expr(expr, env)

    elif kind == 'print':
        _, expr = stmt
        print("<stdout> : ", eval_expr(expr, env))

    elif kind == 'if':
        _, condition, body = stmt
        if eval_expr(condition, env):
            run_block(body, env)

    elif kind == 'while':
        _, condition, body = stmt
        while eval_expr(condition, env):
            run_block(body, env)

    elif kind == 'fnc':
        _, name, args, body = stmt
        functions[name] = (args, body)

    elif kind == 'call':
        _, name, arg_exprs = stmt
        
        if name not in functions:
            raise Exception(f"Unknown function: {name}")
        args, body = functions[name]

        if len(args) != len(arg_exprs):
            raise Exception(f"{name} expects {len(args)} args, got {len(arg_exprs)}")

        arg_vals = [eval_expr(arg_expr, env) for arg_expr in arg_exprs]
        new_env = env.copy()

        for vars, value in zip(args, arg_vals):
            new_env[vars] = value

        run_block(body, new_env)

# === Execute a block of statements ===
def run_block(block, env):
    for stmt in block:
        run_stmt(stmt, env)

# === Main execution ===
tokens = tokenize_lines(temp_code)
ast, _ = parse_block(tokens)
env = {}
run_block(ast, env)
