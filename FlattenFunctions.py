from PythonASTExtension import *
from AssemblyAST import *


class FlattenFunctions:
	
	@staticmethod
	def flattenFunctions(node):
		if isinstance(node,Function):
			flattenCode = []
			
			for c in node.code:
				if isinstance(c,Stmt): flattenCode += c.nodes
				else: flattenCode += [c]
			
			
			functions = []
			newCode = []
			for c in flattenCode:
				if isinstance(c,Lambda) or isinstance(c,Function): functions += [c]
				else: newCode += [c]
			functionDefinition = Function(node.decorators,node.name,node.argnames,node.defaults,node.flags,node.doc,Stmt(newCode))
			# functionDefinition.uniquename = node.uniquename
			return Stmt(functions + [functionDefinition])
		else:
			return node
