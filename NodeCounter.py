from TraverseIR import *
import compiler
from compiler.ast import *
import sys

pythonFilename = sys.argv[1]
pythonAST = compiler.parseFile(pythonFilename)

print TraverseIR.foldPostOrderLeft(pythonAST,lambda ast,c: c + 1,acc=0)