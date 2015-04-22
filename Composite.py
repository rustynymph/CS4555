from PythonASTExtension import *
from TraverseIR import *
import inspect

class Composite:
	def __init__(self,envFuncPairList):
		self.envFuncPairList = envFuncPairList

	@staticmethod
	def transferAttributes(fromNode,toNode):
		fromAttributes = inspect.getmembers(fromNode)
		fromAttributes = [fromAttributes[i][0] for i in range(len(fromAttributes))]
		toAttributes = inspect.getmembers(toNode)
		toAttributes = [toAttributes[i][0] for i in range(len(toAttributes))]
		transferKeys = [k for k in fromAttributes if k not in toAttributes]

		for transfer in transferKeys:
			setattr(toNode,transfer,getattr(fromNode,transfer))

	def compositeMap(self,ast):
		newAST = ast
		for t in self.envFuncPairList:
			nAST = newAST
			newAST = t[1](t[0],nAST) if t[0] else t[1](nAST)
			Composite.transferAttributes(nAST,newAST)
		return newAST