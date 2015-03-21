from compiler.ast import *
from PythonASTExtension import *
from AssemblyAST import *

class Heapify:
	
	def __init__(self,fvs):
		self.freeVariables = fvs

	def heapify(self,node):
		if isinstance(node,Name):
			if node.name in self.freeVariables:	return Subscript(Name(node.name),'OP_APPLY',[Const(0)])
			else: return node
		elif isinstance(node,Assign):
			if isinstance(node.nodes[0],AssName):
				if node.nodes[0].name in self.freeVariables:
					listcreate = Assign([AssName(Name(node.nodes[0].name),'OP_ASSIGN')],CallFunc('create_list',[1]))
					subassign = Assign(Subscript(Name(node.nodes[0].name),'OP_ASSIGN',[Const(0)]),node.expr)
					return Stmt([listcreate,subassign])
			else: return node
		return node

