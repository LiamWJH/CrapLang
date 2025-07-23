# Building the dist

To build the project i recommend to use the python module pyinstaller, to use it go into the folder where your main.py lives

## basic building process
```
pyinstaller main.py --onefile
```
(for normal code change)

### IF YOUR TRYING TO ADD A NEW LIBRARY:

if your trying to add a new library, follow the conventions in the **conventions.md** then run this:

```
pyinstaller main.py --onefile --hidden-import=LIB_{libraryNAME}
```

then get the result in the dist folder and put it in the root dist folder for the file structure

## copy and paste current library build command: (CPCLBC)

```
pyinstaller main.py --onefile --hidden-import=LIB_fileio --hidden-import=LIB_rick --hidden-import=LIB_string
```