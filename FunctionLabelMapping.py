from compiler.ast import *
from PythonASTExtension import *
from AssemblyAST import *

class FunctionLabelMapping:
	
	def functionLabelMapping(self,node,acc):
		if isinstance(node,Assign):
			if isinstance(node.expr,Lambda):
				if isinstance(node.nodes[0],AssName): acc[node.expr.uniquename] = Name(node.nodes[0].name)
				else: acc[node.expr.uniquename] = node.nodes[0]
		return acc
