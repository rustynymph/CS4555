#!/usr/bin/python

import sys
import string
from Flatten import *
from Translator import *
from Optimizer import *
from Explicate import *
from Parser_hw2 import *
import compiler
from Simplify import *
from TraverseIR import *
from Namespace import *
from Orphan import *

pythonFilename = sys.argv[1]

#file_to_parse = open(pythonFilename, 'r')
#text_to_parse = file_to_parse.read()
#raise Exception(text_to_parse)

def removeNestedStmtMap(ast):
	if isinstance(ast,Stmt):
		stmtArray = []
		for expr in ast.nodes:
			stmtArray += expr.nodes if isinstance(expr,Stmt) else [expr]
		return Stmt(stmtArray)
	else: return ast

pythonAST = compiler.parseFile(pythonFilename)
# pythonAST = TraverseIR.map(pythonAST,Optimizer.reduceMap)
pythonAST = TraverseIR.map(pythonAST,Simplify.removeDiscardMap)
# print pythonAST
pythonAST = TraverseIR.map(pythonAST,Optimizer.negationMap)
pythonAST = TraverseIR.map(pythonAST,Namespace.removeDependenciesMap,Namespace(Namespace.environmentKeywords + Namespace.reservedKeywords))
pythonAST = TraverseIR.map(pythonAST,Simplify.nameToBoolMap)
pythonAST = TraverseIR.map(pythonAST,Orphan.findParentMap,Orphan())
pythonAST = TraverseIR.map(pythonAST,Explicate.explicateMap,Explicate())
pythonAST = TraverseIR.map(pythonAST,Explicate.removeIsTagMap)
print pythonAST
print
pythonAST = TraverseIR.map(pythonAST,Flatten.flattenMap,Flatten())
pythonAST = TraverseIR.map(pythonAST,removeNestedStmtMap)
print pythonAST
# flattenedAST = python_compiler.treeFlatten(explicatedAST)
# print flattenedAST[0]
# flattenedAST = pythonAST
# x86AST = Translator.pythonASTToAssemblyAST(flattenedAST)

# x86Filename = sys.argv[1].rsplit(".",1)[0] + ".s"
# x86File = open(x86Filename,"w")
# x86File.write(x86AST.printInstruction())
