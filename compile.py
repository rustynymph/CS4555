#!/usr/bin/python

import sys
import string
from Flatten import *
from Translator import *
from Optimizer import *
from Parser_hw2 import *
from AssemblyAST import *
import compiler

pythonFilename = sys.argv[1]

#file_to_parse = open(pythonFilename, 'r')
#text_to_parse = file_to_parse.read()
#raise Exception(text_to_parse)

pythonAST = compiler.parseFile(pythonFilename)
print pythonAST
print("\n")
pythonAST = Optimizer.reduce(pythonAST)
pythonAST = Optimizer.negation(pythonAST)
flattenedAST = python_compiler.treeFlatten(pythonAST)
x86AST = Translator.pythonASTToAssemblyAST(flattenedAST)

x86Filename = sys.argv[1].rsplit(".",1)[0] + ".s"
x86File = open(x86Filename,"w")
x86File.write(x86AST.printInstruction())
