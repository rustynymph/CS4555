#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
from Flatten import *
from Translator import *
from Optimizer import *
from Parser import *
from AssemblyAST import *

pythonFilename = sys.argv[1]
pythonAST = Parser.parseFile(pythonFilename)
pythonAST = Optimizer.reduce(pythonAST)
pythonAST = Optimizer.negation(pythonAST)
flattenedAST = python_compiler.treeFlatten(pythonAST)
x86AST = Translator.pythonASTToAssemblyAST(flattenedAST)

x86Filename = sys.argv[1].rsplit(".",1)[0] + ".s"
x86File = open(x86Filename,"w")
x86File.write(x86AST.printInstruction())
