"""
for now
"""

temp_code = """
let i = 0

while i < 10
    let i = i + 1
    if i > 6
        print "i is more than 6"
    end
end

print "Buh bye"
"""

# === Tokenize each line into words ===
def tokenize_lines(code: str):
    res = [line.strip().split() for line in code.strip().splitlines()]
    print("tokenized: ",res)
    return res

# === Parse a single expression like: x + 1 ===
def parse_expr(tokens):
    # if just one value (number or variable name)
    if len(tokens) == 1:
        token = tokens[0]

        # Check for string
        if token.startswith('"') and token.endswith('"'):
            return ("string", token[1:-1])

        # Try to parse int
        try:
            return int(token)
        except ValueError:
            return token  # treat as variable name


    # if it's a binary operation like x + 1
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


# === Parse the entire code into a nested AST ===
def parse_block(lines, i=0):
    ast = []  # this will contain all parsed instructions for this block

    while i < len(lines):
        tokens = lines[i]
        if not tokens:
            i += 1
            continue

        cmd = tokens[0]

        # let x = expr
        if cmd == 'let':
            ast.append(('assign', tokens[1], parse_expr(tokens[3:])))
            i += 1

        # print expr
        elif cmd == 'print':
            ast.append(('print', parse_expr(tokens[1:])))
            i += 1

        # if condition
        elif cmd == 'if':
            condition = parse_expr(tokens[1:])
            body, i = parse_block(lines, i + 1)  # recursively parse inner block
            ast.append(('if', condition, body))

        # while condition
        elif cmd == 'while':
            condition = parse_expr(tokens[1:])
            body, i = parse_block(lines, i + 1)  # recursively parse inner block
            ast.append(('while', condition, body))

        # end → end of this block
        elif cmd == 'end':
            return ast, i + 1  # return this block and the next line index

        else:
            # fallback for unknown instruction (e.g. function call)
            ast.append(('call', cmd, [parse_expr(tokens[1:])]))
            i += 1

    return ast, i

# === Evaluate an expression like ('+', 'x', 1) ===
def eval_expr(expr, env):
    if isinstance(expr, int):
        return expr
    if isinstance(expr, tuple) and expr[0] == "string":
        return expr[1]
    if isinstance(expr, str) and expr in env:
        return env[expr]
    if isinstance(expr, str):
        raise Exception(f"Idk this variable: {expr}")
        

    # otherwise it's a tuple like ('+', 'x', 1)
    op, a, b = expr
    a_val = eval_expr(a, env)
    b_val = eval_expr(b, env)

    if op == '+':
        return a_val + b_val
    elif op == '-':
        return a_val - b_val
    elif op == '*':
        return a_val * b_val
    elif op == '/':
        return a_val // b_val  # integer division
    elif op == '%':
        return a_val % b_val
    elif op == '<':
        return a_val < b_val
    elif op == '>':
        return a_val > b_val
    elif op == '<=':
        return a_val <= b_val
    elif op == '>=':
        return a_val >= b_val
    
    elif op == '==':
        return a_val == b_val
    else:
        raise Exception(f"Unknown operator: {op}")


# === Run a single instruction ===
def run_stmt(stmt, env):
    kind = stmt[0]

    if kind == 'assign':  # let x = expr
        _, name, expr = stmt
        env[name] = eval_expr(expr, env)

    elif kind == 'print':  # print expr
        _, expr = stmt
        print("OUTPUT:", eval_expr(expr, env))

    elif kind == 'if':  # if expr ... end
        _, condition, body = stmt
        if eval_expr(condition, env):
            run_block(body, env)

    elif kind == 'while':  # while expr ... end
        _, condition, body = stmt
        while eval_expr(condition, env):
            run_block(body, env)

    elif kind == 'call':
        print(f"Unknown function call: {stmt}")


# === Run a list of instructions ===
def run_block(block, env):
    for stmt in block:
        run_stmt(stmt, env)

tokens = tokenize_lines(temp_code)

ast, _ = parse_block(tokens)
env = {}
run_block(ast, env)