from compiler.ast import *
import copy
from PythonASTExtension import *

class Heapify(node):
	
	def __init__(self,IR):
		self.freeVariables = {}
	
	def heapify(self,ast):
		if isinstance(ast,Name): return Subscript(ast.name,FLAGS,[Const(DecimalValue(0))])
		elif isinstance(ast,Assign):
			if isinstance(ast.node[0],AssName):
				return Assign(Subscript(ast.name,FLAGS,[Const(DecimalValue(0))]),self.heapify(ast.expr))
		else: return ast

'''	
	def freeVars(self,ast):
		if isinstance(node,Const): return set([])
		elif isinstance(node,Name): return set([node.name]) #HERE I AM
		elif isinstance(node,Add): return self.freeVars(node.left) | self.freeVars(node.right)
		elif isinstance(node,CallFunc):
			fv_args = [self.freeVars(i) for i in node.args]
			free_in_args = reduce(lambda a,b: a|b, fv_args, set([]))
			return self.freeVars(node.node)	| free_in_args	
		elif isinstance(node,Lamba): return self.freeVars(node.code) - self.freeVars(node.argnames)
		elif isinstance(node,): 
		elif isinstance(node,):
		elif isinstance(node,):																
		elif isinstance(node,):
		elif isinstance(node,):
'''
