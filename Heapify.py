from PythonASTExtension import *
from AssemblyAST import *
from FreeVars import *

class Heapify:
	
	def __init__(self,fvs,vm):
		self.freeVariables = fvs
		self.variableMapping = vm
		self.fvs = []

	def heapify(self,node):
		if isinstance(node,Name):
			if node.name in self.fvs: return Subscript(Name(node.name),'OP_APPLY',[Const(0)])
			else: return node
		elif isinstance(node,Assign):
			if isinstance(node.nodes[0],AssName):
				for l in self.variableMapping:
					if node.nodes[0].name in self.variableMapping[l]:
						listcreate = Assign(node.nodes,List([Const(0)]))
						subassign = Assign([Subscript(Name(node.nodes[0].name),'OP_APPLY',[Const(0)])],node.expr)
						return Stmt([listcreate,subassign])
					else: continue
			else: return node
		elif isinstance(node,Lambda):
			varSet = self.variableMapping[node.uniquename]
			varList = sorted(varSet)
			self.fvs += [Name(i) for i in varList]
			loadVars = [Assign([AssName(varList[i],'OP_ASSIGN')],Subscript(Name('fvs'),'OP_APPLY',[Const(4*i)])) for i in range (len(varList))]
			node.argnames = node.argnames + self.fvs
			lammy = Lambda(node.argnames,node.defaults,node.flags,Stmt(loadVars+node.code.nodes))
			lammy.uniquename = node.uniquename
			return lammy
		return node

