def readfile(filename):
    with open(filename, "r") as f:
        return f.read()

def writetofile(filename, content):
    with open(filename, "w") as f:
        return f.write(content)

def appendtofile(filename, content):
    with open(filename, "a") as f:
        f.write(content)
