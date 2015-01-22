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

ast = compiler.parse("tmp0 = (4 + 1); y = 5")
flat_ast = python_compiler.treeFlatten(ast)
#x86_ast = Translator.pythonASTToAssemblyAST(flat_ast)
#print x86_ast
print flat_ast

'''
filename = sys.argv[1]
prefix = filename[:len(filename)-3] #takes the prefix name from our *.py file
ast = compiler.parseFile(filename)
flat_ast = python_compiler.treeFlatten(ast)
x86_ast = Translator.pythonASTToAssemblyAST(flat_ast)
file = open(prefix+".s","w")
file.write(x86_ast)
file.close()
'''
