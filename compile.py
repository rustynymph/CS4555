#!/usr/bin/python

import sys
import string
from Flatten import *
from Translator import *
from Optimizer import *
from Explicate import *
import compiler
from Simplify import *
from TraverseIR import TraverseIR
from Namespace import *
from Orphan import *
from Functionize import *
from LivenessAnalysis import *
from GraphColoring import *
from Heapify import *
from FreeVars import *
from ClosureConversion import *
from FunctionLabelMapping import *
from FlattenFunctions import *
from FunctionRevert import *
from SeparateFunctions import *
from MemoryAssignment import *
from StrayCatcher import *
from RuntimeFunctions import *
from UniquifyLambdas import *

pythonFilename = sys.argv[1]

#file_to_parse = open(pythonFilename, 'r')
#text_to_parse = file_to_parse.read()
#raise Exception(text_to_parse)

pythonAST = compiler.parseFile(pythonFilename)
pythonAST = TraverseIR.map(pythonAST,Simplify.removeDiscardMap)
pythonAST = TraverseIR.map(pythonAST,Simplify.nameToBoolMap)
pythonAST = TraverseIR.map(pythonAST,Optimizer.constantFoldingMap)

pythonAST = TraverseIR.map(pythonAST,Orphan.findParentMap,Orphan())
namespace = Namespace(Namespace.environmentKeywords + Namespace.reservedKeywords)
pythonAST = TraverseIR.map(pythonAST,Namespace.removeDependenciesMap,namespace)
pythonAST = TraverseIR.map(pythonAST,Namespace.uniquifyMap,namespace)


pythonAST = TraverseIR.map(pythonAST,Explicate.explicateMap,Explicate())
pythonAST = TraverseIR.map(pythonAST,Explicate.shortCircuitMap,Explicate())
pythonAST = TraverseIR.map(pythonAST,Explicate.removeIsTagMap)
pythonAST = TraverseIR.map(pythonAST,Explicate.removeNot)
pythonAST = TraverseIR.map(pythonAST,Explicate.explicateCompareMap)
pythonAST = TraverseIR.map(pythonAST,Optimizer.explicateFoldingMap)

def removeLet(ast):
	if isinstance(ast,Let):
		assign = Assign([AssName(ast.var.name,'OP_ASSIGN') if isinstance(ast.var,Name) else ast.var],ast.expr)
		body = ast.body
		return Stmt([assign,body])
	else: return ast

pythonAST = TraverseIR.map(pythonAST,removeLet)
pythonAST = TraverseIR.map(pythonAST,UniquifyLambdas.labelLambdas,UniquifyLambdas())
pythonAST = TraverseIR.map(pythonAST,FreeVars.calcFreeVars,FreeVars())

print "\n"+"PythonAST"
print pythonAST
print

allFreeVars = FreeVars.getAllFreeVars()
mappings = TraverseIR.foldPostOrderLeft(pythonAST,FunctionLabelMapping.functionLabelMapping,{},FunctionLabelMapping())

#tup = FreeVars.freeVars(pythonAST)
#free_vars = tup[0]
#env = tup[1]

pythonAST = TraverseIR.map(pythonAST,Heapify.heapify,Heapify(allFreeVars,mappings))
print "Heapified"
print pythonAST

pythonAST = TraverseIR.map(pythonAST,ClosureConversion.createClosure,ClosureConversion(mappings))
print "Closured"
print pythonAST

pythonAST = TraverseIR.map(pythonAST,FunctionRevert.revert)
# pythonAST = TraverseIR.map(pythonAST,Flatten.removeNestedStmtMap)
# pythonAST = TraverseIR.map(pythonAST,Flatten.removeUnnecessaryStmt)
pythonAST = TraverseIR.map(pythonAST,StrayCatcher.catchStray)

pythonAST = TraverseIR.map(pythonAST,Flatten.removeNestedStmtMap)
pythonAST = TraverseIR.map(pythonAST,Flatten.removeUnnecessaryStmt)
pythonAST = TraverseIR.map(pythonAST,FlattenFunctions.flattenFunctions)


pythonAST = TraverseIR.map(pythonAST,Flatten.flattenMap,Flatten())
pythonAST = TraverseIR.map(pythonAST,Functionize.replaceBigPyobjMap)
pythonAST = TraverseIR.map(pythonAST,Functionize.replaceWithRuntimeEquivalentMap,Functionize({"input":"input_int"}))
pythonAST = TraverseIR.map(pythonAST,Flatten.removeNestedStmtMap)
pythonAST = TraverseIR.map(pythonAST,Flatten.removeUnnecessaryStmt)
print "Final Python AST"
print pythonAST

def getFunctionNames(ast,acc):
	if isinstance(ast,Function):
		return acc + [ast.name]
	else: return acc

functions = TraverseIR.foldPostOrderRight(pythonAST,getFunctionNames,RuntimeFunctions.runtimeFunctions)

liveness = TraverseIR.foldPostOrderRight(pythonAST,LivenessAnalysis2.livenessFolding,set([]),LivenessAnalysis2(functions))

# graph = GraphColoring.createGraph(liveness)
# 

def getParameters(ast,acc):
	if isinstance(ast,Function) or isinstance(ast,Lambda):
		return acc + ast.argnames
	else: return acc

parameterNames = TraverseIR.foldPostOrderRight(pythonAST,getParameters,[])

graph = TraverseIR.foldPostOrderRight(pythonAST,GraphColoring.createGraphFolding,{},GraphColoring(functions + parameterNames))
print "Graph"
print graph
coloredgraph = GraphColoring.colorGraph(graph)
print "Colored Graph"
print coloredgraph
functionVariables = TraverseIR.foldPostOrderRight(pythonAST,MemoryAssignment.variablesWithAssociatedFunctions,({},set([])))
print functionVariables

def seperateVariables(functionVariables,coloredgraph):
	seperate = {}
	for (k,v) in functionVariables.items():
		if k not in seperate: seperate[k] = {}
		for variable in v:
			if variable in coloredgraph and coloredgraph[variable] != None: seperate[k] = dict(seperate[k].items() + {variable:coloredgraph[variable]}.items())
	return seperate

functionVariableMapping =  seperateVariables(functionVariables[0],coloredgraph)
print "fdjskla"
print functionVariableMapping

functionDictionary = MemoryAssignment.assignRegisterMemoryLocation(functionVariableMapping)
print functionDictionary

d = MemoryAssignment.assignVariableWithRegisterMapping(functionVariableMapping,functionDictionary)
print d

memory = {}
for (k,v) in d.items():
	memory = dict(memory.items() + v.items())


parameterMemoryLocations = TraverseIR.foldPostOrderRight(pythonAST,MemoryAssignment.getParameterMemoryLocations,{})
print parameterMemoryLocations
pythonAST = TraverseIR.map(pythonAST,MemoryAssignment.assignMemoryLocationMap,MemoryAssignment(parameterMemoryLocations,memory))

x86 = TraverseIR.map(pythonAST,Translator.translateToX86,Translator(coloredgraph,dict(memory.items() + parameterMemoryLocations.items())))
# print x86
#x86 = SeparateFunctions.move(x86)
#print x86

x86Filename = sys.argv[1].rsplit(".",1)[0] + ".s"
x86File = open(x86Filename,"w")
x86File.write(x86.printInstruction())

