import shlex
import argparse

argparser = argparse.ArgumentParser()

argparser.add_argument("-r", "--run", type = str, default=None)

args= argparser.parse_args()
def tokenize_lines(code: str):
    return [shlex.split(line, posix=False) for line in code.strip().splitlines()] # uses shlex to tokenize buy line by line

def parse_expr(tokens: str):

    if len(tokens) == 1:
        token = tokens[0]

        if token.startswith('"') and token.endswith('"'):
            return ("string", token[1:-1]) # this means its a single arg string just return a string
        
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
    else: # why then
        joined = " ".join(tokens)
        if joined.startswith('"') and joined.endswith('"'):
            return ('string', joined[1:-1])
        try:
            return int(token)
        except ValueError:
            return token
        raise Exception("Can't parse that expression yet.")

importlist = []
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
        
        elif cmd == 'input': # meh meh  mmeh for now lets say inpput does : input vartostore text
            ast.append(('input', tokens[1], parse_expr([tokens[2]])))
            i += 1

        elif cmd == "comment:":
            pass
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

        elif cmd == 'output':
            insidevar = tokens[1]
            outsidevar = tokens[2]
            ast.append(('output', insidevar, outsidevar))
            i += 1
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
        
        elif cmd == 'call':
            arg_exprs = [parse_expr([arg]) for arg in tokens[2:]] # collects the arguments needed in total
            ast.append(('call', tokens[1], arg_exprs))# append the custom 
            i += 1

        elif cmd == 'have':
            libname = tokens[1]
            ast.append(('have', libname))

            if libname == "string":
                importlist.append("string")
                from LIB_string import stringslices
            
            if libname == "fileio":
                importlist.append("fileio")
                from LIB_fileio import readfile, writetofile, appendtofile
            
            if libname == "rick":
                importlist.append("rick")
                from LIB_rick import rickroll
                
            i += 1

        else:
            ####################################
            #	str lib
            ####################################
            
            if cmd == "slice":
                if "string" in importlist:
                    ast.append(('slice', tokens[1], tokens[2], tokens[3]))
                    i += 1
                else:
                    raise Exception("string library was not imported")
            
            ####################################
            #	fileio
            ####################################
            
            if cmd == "readfile":
                if "fileio" in importlist: #file name #varname
                    ast.append(('readfile', parse_expr([tokens[1]]), parse_expr([tokens[2]])))
                    i += 1
                else:
                    raise Exception("fileio library has not yet been imported")
            if cmd == "writefile":
                if "fileio" in importlist:
                    ast.append(('writefile', parse_expr([tokens[1]]), parse_expr([tokens[2]])))
                    i += 1
                else:
                    raise Exception("fileio library has not yet been imported")
            if cmd == "appendfile":
                if "fileio" in importlist:
                    ast.append(('appendfile', parse_expr([tokens[1]]), parse_expr([tokens[2]])))
                    i += 1
                else:
                    raise Exception("fileio library has not yet been imported")
                
            ####################################
            #	rick
            ####################################
            
            if cmd == "rickroll":
                if "rick" in importlist:
                    ast.append(('rickroll', ""))
                    i += 1
                else:
                    raise Exception("sigma brainrot has not been imported")
            
            
            
    return ast, i # just returning results

# === Evaluate an expression ===
def eval_expr(expr, env):
    if expr is None:
        print(env, expr)
    
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
    elif op == '!=': return a_val != b_val

    else: raise Exception(f"Unknown operator: {op}")

functions = {} # where we store variables

# btw stmt stands for singe-STateMenT
def run_stmt(stmt, env, outer_env):
    kind = stmt[0] # Type of statement kinda like cmd variable in parse func

    if kind == 'assign': #variable asssign
        _, name, expr = stmt
        if "[" in name and "]" in name:
            listindex = int(name.split("[")[1][0:-1])
            name = name.split("[")[0]
            env[name][listindex] = expr
        else:
            env[name] = eval_expr(expr, env)

    elif kind == 'print': #print the output
        _, expr = stmt
        print("<stdout> : ", eval_expr(expr, env))

    elif kind == 'input':
        _, storevar, question = stmt
        env[storevar] = input(f"<stdin> : {eval_expr(question, env)}")
    
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

    elif kind == 'output':
        _, insidevar, outsidevar = stmt
        outer_env[outsidevar] = env[insidevar]
        
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
    
    elif kind == "slice":
        if "string" in importlist:
            from LIB_string import stringslices
            
            _, varname, idx1, idx2 = stmt
            env[varname] = stringslices(env[varname], int(idx1), int(idx2))
    elif kind == "readfile":
        if "fileio" in importlist:
            from LIB_fileio import readfile
            _, filename, storevar = stmt
            
            env[storevar] = readfile(eval_expr(filename, env))
            

    elif kind == "writefile":
        if "fileio" in importlist:
            from LIB_fileio import writetofile
            _, filename, content = stmt
            writetofile(eval_expr(filename, env), eval_expr(content, env))

    elif kind == "appendfile":
        if "fileio" in importlist:
            from LIB_fileio import appendtofile
            _, filename, content = stmt

            appendtofile(eval_expr(filename, env), eval_expr(content, env))

    elif kind == "rickroll":
        if "rick" in importlist:
            from LIB_rick import rickroll
            rickroll()
    
    elif kind == 'call': # function call, call and run the function
        _, name, arg_exprs = stmt # get function information
        
        if name not in functions: # error function does not exist
            raise Exception(f"Unknown function: {name}")
        args, body = functions[name]  #elsewise, get the arguments and body

        if len(args) != len(arg_exprs): # missing argument
            raise Exception(f"{name} expects {len(args)} args, got {len(arg_exprs)}")

        arg_vals = [eval_expr(arg_expr, env) for arg_expr in arg_exprs] # evals the given arguments
        inner_env = {}

        for vars, value in zip(args, arg_vals):
            inner_env[vars] = value # assign new values from the function made

        run_block(body, inner_env, env) # just run the block from function

# === Execute a block of statements ===
def run_block(block, env, outer_env=None):
    if outer_env is None: outer_env = env # if empty we need to copy the env for use
    for stmt in block:
        run_stmt(stmt, env, outer_env) # lolz



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


    # === Main execution ===
    tokens = tokenize_lines(usercode)
    ast, _ = parse_block(tokens)
    env = {}
    run_block(ast, env)