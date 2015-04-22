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
from LivenessAnalysis2 import *
from GraphColoring import *
from Heapify import *
from FreeVars import *
from ClosureConversion import *
from FunctionLabelMapping import *
from FlattenFunctions import *
from FunctionRevert import *
from SeparateFunctions import *
from Deforestation import *

pythonFilename = sys.argv[1]

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
pythonAST = TraverseIR.map(pythonAST,Flatten.removeNestedStmtMap)
pythonAST = TraverseIR.map(pythonAST,Flatten.removeUnnecessaryStmt)
pythonAST = TraverseIR.map(pythonAST,FlattenFunctions.flattenFunctions)
pythonAST = TraverseIR.map(pythonAST,Flatten.flattenMap,Flatten())
pythonAST = TraverseIR.map(pythonAST,Functionize.replaceBigPyobjMap)
pythonAST = TraverseIR.map(pythonAST,Functionize.replaceWithRuntimeEquivalentMap,Functionize({"input":"input_int"}))
pythonAST = TraverseIR.map(pythonAST,Flatten.removeNestedStmtMap)
pythonAST = TraverseIR.map(pythonAST,Flatten.removeUnnecessaryStmt)
liveness = TraverseIR.foldPostOrderRight(pythonAST,LivenessAnalysis2.livenessFolding,set([]),LivenessAnalysis2(["input_int","print_any","set_subscript","is_true","get_subscript","add","equal","not_equal","create_list","create_dict"]))
graph = TraverseIR.foldPostOrderRight(pythonAST,GraphColoring.createGraphFolding,{},GraphColoring(["input_int","print_any","set_subscript","is_true","get_subscript","add"]))
coloredgraph = GraphColoring.colorGraph(graph)

x86 = TraverseIR.map(pythonAST,Translator.translateToX86,Translator(coloredgraph))

x86Filename = sys.argv[1].rsplit(".",1)[0] + ".s"
x86File = open(x86Filename,"w")
x86File.write(x86.printInstruction())

# pythonFilename = sys.argv[1]

# pythonAST = compiler.parseFile(pythonFilename)


# deforestList0 = [(None,Simplify.removeDiscardMap)]
# deforestList0 += [(None,Simplify.nameToBoolMap)]
# deforestList0 += [(None,Optimizer.constantFoldingMap)]
# deforestList0 += [(Orphan(),Orphan.findParentMap)]

# namespace = Namespace(Namespace.environmentKeywords + Namespace.reservedKeywords)
# deforestList0 += [(namespace,Namespace.removeDependenciesMap)]
# # deforestList0 += [(namespace,Namespace.uniquifyMap)]

# deforest0 = Deforestation(deforestList0)
# pythonAST = deforest0.map(pythonAST)
# # pythonAST = TraverseIR.map(pythonAST,Simplify.removeDiscardMap)
# # pythonAST = TraverseIR.map(pythonAST,Simplify.nameToBoolMap)
# # pythonAST = TraverseIR.map(pythonAST,Optimizer.constantFoldingMap)
# # pythonAST = TraverseIR.map(pythonAST,Orphan.findParentMap,Orphan())
# # namespace = Namespace(Namespace.environmentKeywords + Namespace.reservedKeywords)
# # pythonAST = TraverseIR.map(pythonAST,Namespace.removeDependenciesMap,namespace)
# pythonAST = TraverseIR.map(pythonAST,Namespace.uniquifyMap,namespace)

# deforestList1 = [(Explicate(),Explicate.explicateMap)]
# deforestList1 += [(Explicate(),Explicate.shortCircuitMap)]
# deforestList1 += [(None,Explicate.removeIsTagMap)]
# deforestList1 += [(None,Explicate.removeNot)]
# # deforestList1 += [(None,Explicate.explicateCompareMap)]
# # deforestList1 += [(None,Optimizer.explicateFoldingMap)]

# deforest1 = Deforestation(deforestList1)
# pythonAST = deforest1.map(pythonAST)

# # pythonAST = TraverseIR.map(pythonAST,Explicate.explicateMap,Explicate())
# # pythonAST = TraverseIR.map(pythonAST,Explicate.shortCircuitMap,Explicate())
# # pythonAST = TraverseIR.map(pythonAST,Explicate.removeIsTagMap)
# # pythonAST = TraverseIR.map(pythonAST,Explicate.removeNot)
# pythonAST = TraverseIR.map(pythonAST,Explicate.explicateCompareMap)
# pythonAST = TraverseIR.map(pythonAST,Optimizer.explicateFoldingMap)
# pythonAST = TraverseIR.map(pythonAST,Flatten.removeNestedStmtMap)
# pythonAST = TraverseIR.map(pythonAST,Flatten.removeUnnecessaryStmt)
# pythonAST = TraverseIR.map(pythonAST,FlattenFunctions.flattenFunctions)
# pythonAST = TraverseIR.map(pythonAST,Flatten.flattenMap,Flatten())
# pythonAST = TraverseIR.map(pythonAST,Functionize.replaceBigPyobjMap)
# pythonAST = TraverseIR.map(pythonAST,Functionize.replaceWithRuntimeEquivalentMap,Functionize({"input":"input_int"}))
# pythonAST = TraverseIR.map(pythonAST,Flatten.removeNestedStmtMap)
# pythonAST = TraverseIR.map(pythonAST,Flatten.removeUnnecessaryStmt)
# liveness = TraverseIR.foldPostOrderRight(pythonAST,LivenessAnalysis2.livenessFolding,set([]),LivenessAnalysis2(["input_int","print_any","set_subscript","is_true","get_subscript","add","equal","not_equal","create_list","create_dict"]))
# graph = TraverseIR.foldPostOrderRight(pythonAST,GraphColoring.createGraphFolding,{},GraphColoring(["input_int","print_any","set_subscript","is_true","get_subscript","add"]))
# coloredgraph = GraphColoring.colorGraph(graph)

# x86 = TraverseIR.map(pythonAST,Translator.translateToX86,Translator(coloredgraph))

# x86Filename = sys.argv[1].rsplit(".",1)[0] + ".s"
# x86File = open(x86Filename,"w")
# x86File.write(x86.printInstruction())

