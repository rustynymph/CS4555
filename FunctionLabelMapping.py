from compiler.ast import *
from PythonASTExtension import *
from AssemblyAST import *

class FunctionLabelMapping:
	
#	def __init__(self):
#		self.varsToLambdas = {}

	def functionLabelMapping(self,node,acc):
		if isinstance(node,Assign):
			if isinstance(node.expr,Lambda):
				acc[node.expr.uniquename] = node.nodes[0].name
				
		return acc
