import shlex
import argparse

argparser = argparse.ArgumentParser()

argparser.add_argument("-r", "--run", type = str, default=None)

args= argparser.parse_args()


if args.run != None:
    with open(args.run, "r") as f:
        usercode = f.read()



    test_code = """
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

    def tokenize_lines(code: str):
        return [shlex.split(line, posix=False) for line in code.strip().splitlines()] # uses shlex to tokenize buy line by line

    def parse_expr(tokens):

        if len(tokens) == 1:
            token = tokens[0]

            if token.startswith('"') and token.endswith('"'):
                return ("string", token[1:-1]) # this means its a single arg string just returna string
            
            if token.startswith('[') and token.endswith(']'):
                return ("list", token)
            
            if token.endswith("]") and "[" in token:
                varname, index = token.split("[")
                index = index[:-1]
                
                return ('index', varname, parse_expr([index]))
            
            try:
                return int(token) # try to turn it into a integer if it fails its a float or smth so we just return it
            except ValueError:
                return token
            
        elif len(tokens) == 3: # this means it is a binary operation like + - * /
            a, op, b = tokens # divide it into format

            return (op, parse_expr([a]), parse_expr([b])) # return the tuple version in right order
        else: # which means its a string so return whatever and try to int it
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

        while i < len(lines): # for all the lines
            tokens = lines[i]
            if not tokens: # pass the empty lines
                i += 1
                continue

            cmd = tokens[0] # get the first item or command from the tokens list

            # break into cases
            if cmd == 'let':
                ast.append(('assign', tokens[1], parse_expr(tokens[3:]))) #add variable assign
                i += 1

            elif cmd == 'print':
                ast.append(('print', parse_expr(tokens[1:]))) #add print
                i += 1

            elif cmd == 'if':
                condition = parse_expr(tokens[1:]) # get the condition
                body, i = parse_block(lines, i + 1) # get the body of the scope and sets the index where it ends
                ast.append(('if', condition, body))  # adds the full thing

            elif cmd == 'while':# almost same as if
                condition = parse_expr(tokens[1:]) 
                body, i = parse_block(lines, i + 1)
                ast.append(('while', condition, body))

            elif cmd == 'fnc':
                name = tokens[1] # gets the function name
                args = tokens[2:] # gets the arguments that can be passed in
                body, i = parse_block(lines, i + 1) # gets the body and sets the index
                ast.append(('fnc', name, args, body))# adds to ast

            elif cmd == "push":
                list_name = tokens[1]
                value = parse_expr(tokens[2:])
                ast.append(('push', list_name, value))
                i += 1
            
            elif cmd == "pop":
                list_name = tokens[1]
                index = parse_expr(tokens[2:])
                ast.append(('push', list_name, index))
                i += 1
            
            elif cmd == 'end': # which means end of scope
                return ast, i + 1 # just return the next index
            
            else:
                arg_exprs = [parse_expr([arg]) for arg in tokens[1:]] # collects the arguments needed in total
                ast.append(('call', cmd, arg_exprs))# append the custom 
                i += 1

        return ast, i # just returning results

    # === Evaluate an expression ===
    def eval_expr(expr, env):
        if isinstance(expr, int): # int if int
            return expr
        
        if isinstance(expr, tuple) and expr[0] == "string": # ('string', "Blablah") as Blablah
            return expr[1]
        
        if isinstance(expr, tuple) and expr[0] == "list":
            import ast
            return ast.literal_eval(expr[1])
        
        if isinstance(expr, tuple) and expr[0] == "index":
            _, name, idx = expr
            
            idx = eval_expr(idx, env)
            if name not in env:
                raise Exception(f"{name} not defined")
            if not isinstance(env[name], list):
                raise Exception(f"{name} not a list")
            return env[name][idx]
        
        
        if isinstance(expr, str) and expr in env: # variable names as variable values
            return env[expr]
        
        if isinstance(expr, str): # unknown strings that are not vaariable names as error
            raise Exception(f"Idk this variable: {expr}")

        op, a, b = expr # basic operation
        a_val = eval_expr(a, env) # passing in variables and values
        b_val = eval_expr(b, env)

        # calculations and bool opers
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

    functions = {} # where we store variables

    # btw stmt stands for singe-STateMenT
    def run_stmt(stmt, env):
        kind = stmt[0] # Type of statement kinda like cmd variable in parse func

        if kind == 'assign': #variable asssign
            _, name, expr = stmt
            env[name] = eval_expr(expr, env)

        elif kind == 'print': #print the output
            _, expr = stmt
            print("<stdout> : ", eval_expr(expr, env))

        elif kind == 'if': #run if statement
            _, condition, body = stmt
            if eval_expr(condition, env):
                run_block(body, env)

        elif kind == 'while': # run while statement
            _, condition, body = stmt
            while eval_expr(condition, env):
                run_block(body, env)

        elif kind == 'fnc': #collect the function information and assign it to the functions dictionaary
            _, name, args, body = stmt
            functions[name] = (args, body)

        elif kind == "push":
            _, name, value = stmt
            value = eval_expr(value, env)
            if name in env and isinstance(env[name], list):
                env[name].append(value)
        
        elif kind == "pop":
            _, name, index = stmt
            index = eval_expr(value, env)
            if name in env and isinstance(env[name], list):
                del env[name][index]
        
        elif kind == 'call': # function call, call and run the function
            _, name, arg_exprs = stmt # get function information
            
            if name not in functions: # error function does not exist
                raise Exception(f"Unknown function: {name}")
            args, body = functions[name]  #elsewise, get the arguments and body

            if len(args) != len(arg_exprs): # missing argument
                raise Exception(f"{name} expects {len(args)} args, got {len(arg_exprs)}")

            arg_vals = [eval_expr(arg_expr, env) for arg_expr in arg_exprs] # evals the given arguments
            new_env = env.copy() # make a copy oh the env

            for vars, value in zip(args, arg_vals):
                new_env[vars] = value # assign new values from the function made

            run_block(body, new_env) # just run the block from function

    # === Execute a block of statements ===
    def run_block(block, env):
        for stmt in block:
            run_stmt(stmt, env) # lolz

    # === Main execution ===
    tokens = tokenize_lines(usercode)
    ast, _ = parse_block(tokens)
    env = {}
    run_block(ast, env)
