from PythonASTExtension import *
from AssemblyAST import *

class Heapify:
	
	def __init__(self,fvs,vm):
		self.freeVariables = fvs
		self.variableMapping = vm

	def heapify(self,node):
		if isinstance(node,Name):
			if node.name in self.freeVariables:	return Subscript(Name(node.name),'OP_APPLY',[Const(0)])
			else: return node
		elif isinstance(node,Assign):
			if isinstance(node.nodes[0],AssName):
				if node.nodes[0].name in self.freeVariables:
					listcreate = Assign(node.nodes,List([Const(-7)]))
					subassign = Assign([Subscript(Name(node.nodes[0].name),'OP_APPLY',[Const(0)])],node.expr)
					return Stmt([listcreate,subassign])
			else: return node
		elif isinstance(node,Lambda):
			varSet = self.variableMapping[node.uniquename]
			varList = sorted(varSet)
			loadVars = [Assign([AssName(varList[i],'OP_ASSIGN')],Subscript(Name('fvs'),'OP_APPLY',[Const(4*i)])) for i in range (len(varList))]
			lammy = Lambda(node.argnames+['fvs'],node.defaults,node.flags,Stmt(loadVars+node.code.nodes))
			lammy.uniquename = node.uniquename
			return lammy
		return node

