from PythonASTExtension import *
from AssemblyAST import *
from FreeVars import *


class NameTracker():
	def __init__(self,prefix,count=0):
		self.prefix = prefix
		self.count = count

	def getName(self):
		return self.prefix + "$" + str(self.count)

	def getNameAndIncrementCounter(self):
		name = self.getName()
		self.count += 1
		return name

class Heapify:
	
	def __init__(self,allFreeVars,mappings):
		self.variableMapping = mappings
		self.allFreeVars = allFreeVars
		self.generateName = NameTracker('fvs')

	def heapify(self,node):
		if isinstance(node,Name):
			if node.name in self.allFreeVars: return Subscript(node,'OP_APPLY',[Const(0)])
			else: return node
		elif isinstance(node,Assign):
			if isinstance(node.nodes[0],AssName):
				if node.nodes[0].name in self.allFreeVars:
					listcreate = Assign(node.nodes,List([node.expr]))
					return listcreate
				else: return node
			else: return node
		elif isinstance(node,Lambda):

			lambda_fvs = node.fvs
			var_list = [Name(var) for var in lambda_fvs]
			var_list = sorted(var_list)

			fvs_name = self.generateName.getNameAndIncrementCounter()

			loadVars = [Assign([AssName(var_list[i].name,'OP_ASSIGN')],Subscript(Name(fvs_name),'OP_APPLY',[Const(4*i)])) for i in range (len(var_list))]

			lammy = Lambda(node.argnames,node.defaults,node.flags,Stmt(loadVars+node.code.nodes))

			lammy.uniquename = node.uniquename
			lammy.fvsname = fvs_name 
			lammy.fvsList = List(var_list)

			return lammy
		return node

