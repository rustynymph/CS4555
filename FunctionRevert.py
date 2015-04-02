from PythonASTExtension import *
from AssemblyAST import *

class FunctionRevert:

	@staticmethod
	def revert(node):
		if isinstance(node,Assign):
			if isinstance(node.expr,Lambda):
				if isinstance(node.nodes[0],AssName):
					funny = Function(None,node.nodes[0].name,node.expr.argnames,(),0,None,node.expr.code)
					funny.uniquename = node.expr.uniquename
					return funny
				elif isinstance(node.nodes[0],Subscript):
					funny = Function(None,node.nodes[0],node.expr.argnames,(),0,None,node.expr.code)
					funny.uniquename = node.expr.uniquename
					return funny
				else: return node
			else: return node
		else: return node
