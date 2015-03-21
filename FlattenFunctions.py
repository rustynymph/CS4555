from compiler.ast import *
from PythonASTExtension import *
from AssemblyAST import *


class FlattenFunctions:
	
	@staticmethod
	def flattenFunctions(node):
		if isinstance(node,Lambda):
			flattenCode = []
			print node
			for c in node.code:
				if isinstance(c,Stmt): flattenCode += c.nodes
				else: flattenCode += c
			
			functions = []
			newCode = []
			for c in flattenCode:
				if isinstance(c,Lambda) or isinstance(c,Function): funcs += c
				else: newCode += c
			
			functionDefinition = Lambda(node.argnames,node.defaults,node.flags,newCode)
			functionDefinition.uniquename = node.uniquename
			return Stmt(functions + [functionDefinition])
