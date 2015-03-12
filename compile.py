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
from TraverseIR import TraverseIR
from Namespace import *
from Orphan import *
from Functionize import *
from LivenessAnalysis import *
from GraphColoring import *

pythonFilename = sys.argv[1]

#file_to_parse = open(pythonFilename, 'r')
#text_to_parse = file_to_parse.read()
#raise Exception(text_to_parse)

pythonAST = compiler.parseFile(pythonFilename)
# print pythonAST
pythonAST = TraverseIR.map(pythonAST,Simplify.removeDiscardMap)
pythonAST = TraverseIR.map(pythonAST,Simplify.nameToBoolMap)
pythonAST = TraverseIR.map(pythonAST,Optimizer.constantFoldingMap)

pythonAST = TraverseIR.map(pythonAST,Orphan.findParentMap,Orphan())
pythonAST = TraverseIR.map(pythonAST,Namespace.removeDependenciesMap,Namespace(Namespace.environmentKeywords + Namespace.reservedKeywords))

pythonAST = TraverseIR.map(pythonAST,Explicate.explicateMap,Explicate())
pythonAST = TraverseIR.map(pythonAST,Explicate.shortCircuitMap,Explicate())
pythonAST = TraverseIR.map(pythonAST,Explicate.removeIsTagMap)
pythonAST = TraverseIR.map(pythonAST,Explicate.explicateCompareMap)
pythonAST = TraverseIR.map(pythonAST,Optimizer.explicateFoldingMap)

pythonAST = TraverseIR.map(pythonAST,Flatten.flattenMap,Flatten())
pythonAST = TraverseIR.map(pythonAST,Functionize.replaceBigPyobjMap)
pythonAST = TraverseIR.map(pythonAST,Functionize.replaceWithRuntimeEquivalentMap,Functionize({"input":"input_int"}))
pythonAST = TraverseIR.map(pythonAST,Flatten.removeNestedStmtMap)
pythonAST = TraverseIR.map(pythonAST,Flatten.removeUnnecessaryStmt)
print "Final Python AST"
print pythonAST
liveness = LivenessAnalysis.livenessAnalysis(LivenessAnalysis(pythonAST))

graph = GraphColoring.createGraph(liveness)
coloredgraph = GraphColoring.colorGraph(graph)


x86 = TraverseIR.map(pythonAST,Translator.translateToX86,Translator(coloredgraph))
# print x86


x86Filename = sys.argv[1].rsplit(".",1)[0] + ".s"
x86File = open(x86Filename,"w")
x86File.write(x86.printInstruction())

