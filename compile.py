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
# from LivenessAnalysis import *
from LivenessAnalysis2 import *
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

pythonFilename = sys.argv[1]

#file_to_parse = open(pythonFilename, 'r')
#text_to_parse = file_to_parse.read()
#raise Exception(text_to_parse)

pythonAST = compiler.parseFile(pythonFilename)
print pythonAST
pythonAST = TraverseIR.map(pythonAST,Simplify.removeDiscardMap)
pythonAST = TraverseIR.map(pythonAST,Simplify.nameToBoolMap)
pythonAST = TraverseIR.map(pythonAST,Optimizer.constantFoldingMap)

pythonAST = TraverseIR.map(pythonAST,Orphan.findParentMap,Orphan())
namespace = Namespace(Namespace.environmentKeywords + Namespace.reservedKeywords)
pythonAST = TraverseIR.map(pythonAST,Namespace.removeDependenciesMap,namespace)
pythonAST = TraverseIR.map(pythonAST,Namespace.uniquifyMap,namespace)

print "idk"
print pythonAST
print "\n"

pythonAST = TraverseIR.map(pythonAST,Explicate.explicateMap,Explicate())
pythonAST = TraverseIR.map(pythonAST,Explicate.shortCircuitMap,Explicate())
pythonAST = TraverseIR.map(pythonAST,Explicate.removeIsTagMap)
pythonAST = TraverseIR.map(pythonAST,Explicate.removeNot)
pythonAST = TraverseIR.map(pythonAST,Explicate.explicateCompareMap)
pythonAST = TraverseIR.map(pythonAST,Optimizer.explicateFoldingMap)

print "EXPLICATED"
print pythonAST
print "\n"

# tup = FreeVars.freeVars(pythonAST)
# free_vars = tup[0]
# env = tup[1]

# pythonAST = TraverseIR.map(pythonAST,Heapify.heapify,Heapify(free_vars,env))
# print "Heapified"
# print pythonAST
# mappings = TraverseIR.foldPostOrderLeft(pythonAST,FunctionLabelMapping.functionLabelMapping,{},FunctionLabelMapping())
# pythonAST = TraverseIR.map(pythonAST,ClosureConversion.createClosure,ClosureConversion(env))
# print "Closured"
# print pythonAST

pythonAST = TraverseIR.map(pythonAST,FunctionRevert.revert)
print pythonAST
# pythonAST = TraverseIR.map(pythonAST,Flatten.removeNestedStmtMap)
# pythonAST = TraverseIR.map(pythonAST,Flatten.removeUnnecessaryStmt)
pythonAST = TraverseIR.map(pythonAST,StrayCatcher.catchStray)
print "hello"
print pythonAST
pythonAST = TraverseIR.map(pythonAST,FlattenFunctions.flattenFunctions)
print "Flattened Functions"
print pythonAST

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
graph = TraverseIR.foldPostOrderRight(pythonAST,GraphColoring.createGraphFolding,{},GraphColoring(functions))
coloredgraph = GraphColoring.colorGraph(graph)
print coloredgraph
pythonAST = TraverseIR.map(pythonAST,MemoryAssignment.assignMemoryLocationMap,MemoryAssignment(coloredgraph))

x86 = TraverseIR.map(pythonAST,Translator.translateToX86,Translator(coloredgraph))
print x86
#x86 = SeparateFunctions.move(x86)
#print x86

x86Filename = sys.argv[1].rsplit(".",1)[0] + ".s"
x86File = open(x86Filename,"w")
x86File.write(x86.printInstruction())

