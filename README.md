##CS4555 Compiler Construction, University of Colorado Boulder
###Python to x86 Compiler -- Homework 1
####Annie Kelly and Andrew Arnopoulos
---------------------------------

This compiler works on a small subset of Python, P0. Programs that can be compiled include: variable assignments, addition, negation, taking input(), and printing. Here is an example of a sample program:

```
a = 5 + input() +-6 + input()
print a
```

######To compile a Python program to x86:
`python compile.py <filename.py>`

This will create a `<filename.s>` file

######To run the compiled x86 code:
`gcc -m32 *.c <filename.s> -o <executablename> -lm`

Note: make sure all runtime source and header files are in the same directory.
