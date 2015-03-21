from compiler.ast import *
from PythonASTExtension import *

freeVarsSet = set()
variableMapping = {}

class nameGenerator():

	def __init__(self,prefix,count=0):
		self.prefix = prefix
		self.count = count

	def getName(self):
		return self.prefix + "$" + str(self.count)

	def getNameAndIncrementCounter(self):
		name = self.getName()
		self.count += 1
		return name

createName = nameGenerator("lammy")

class FreeVars:

	@staticmethod
	def freeVarsHelper(node):
		global variableMapping
		if isinstance(node,Const): return set([])
		elif isinstance(node,Name): return set([node.name])
		elif isinstance(node,Add): return FreeVars.freeVarsHelper(node.left) | FreeVars.freeVarsHelper(node.right)
		elif isinstance(node,CallFunc):
			fv_args = [FreeVars.freeVarsHelper(e) for e in node.args]
			free_in_args = reduce(lambda b,a: a|b, fv_args, set([]))
			return free_in_args
		elif isinstance(node,Lambda):
			save = set()
			if isinstance(node.code,Stmt):
				for x in node.code.nodes:
					save = save | FreeVars.freeVarsHelper(x)
			else: save = save | FreeVars.freeVarsHelper(node.code)
			node.uniquename = createName.getNameAndIncrementCounter()
			variableMapping[node.uniquename] = save - set(node.argnames)
			return save - set(node.argnames)
		elif isinstance(node,UnarySub): return FreeVars.freeVarsHelper(node.expr)
		elif isinstance(node,List):
			fv_args = [FreeVars.freeVarsHelper(e) for e in node.nodes]
			free_in_args = reduce(lambda b,a: a|b, fv_args, set([]))
			return free_in_args			
		elif isinstance(node,Dict):
			fv_args = [FreeVars.freeVarsHelper(e) for e[0] in node.items]
			fv_args2 = [FreeVars.freeVarsHelper(e) for e[1] in node.items]
			free_in_args = reduce(lambda b,a: a|b, fv_args, set([]))
			free_in_args2 = reduce(lambda b,a: a|b, fv_args2, set([]))
			free_in_args3 = free_in_args | free_in_args
			return free_in_args3
		elif isinstance(node,Subscript):
			expression = FreeVars.freeVarsHelper(node.expr)
			subs = [FreeVars.freeVarsHelper(sub) for sub in node.subs]
			free_in_args = reduce(lambda b,a: a|b, subs, set([]))
			free_in_args2 = expression | free_in_args
			return free_in_args2
		elif isinstance(node,IfExp):
			save = FreeVars.freeVarsHelper(node.test)
			if isinstance(node.then,Stmt):
				for i in node.then.nodes:
					save = save | FreeVars.freeVarsHelper(i)
			else:
				save = save | FreeVars.freeVarsHelper(node.then)
			if isinstance(node.else_,Stmt):
				for i in node.else_.nodes:
					save = save | FreeVars.freeVarsHelper(i)
			else:
				save = save | FreeVars.freeVarsHelper(node.else_)
			return save			
		elif isinstance(node,Compare): return FreeVars.freeVarsHelper(node.expr) | FreeVars.freeVarsHelper(node.ops[0][1])	
		elif isinstance(node,And):
			save = set()
			for i in node.nodes:
				save = save | FreeVars.freeVarsHelper(i)
			return save			
		elif isinstance(node,Or):
			save = set()
			for i in node.nodes:
				save = save | FreeVars.freeVarsHelper(i)
			return save				
		elif isinstance(node,Let):
			save = FreeVars.freeVarsHelper(node.var)
			if isinstance(node.expr,Let): save = save | FreeVars.freeVarsHelper(node.expr)
			else: save = save | FreeVars.freeVarsHelper(node.body)
			return save			
		elif isinstance(node,InjectFrom): return FreeVars.freeVarsHelper(node.arg)
		elif isinstance(node,GetTag): return FreeVars.freeVarsHelper(node.arg)
		elif isinstance(node,ProjectTo): return FreeVars.freeVarsHelper(node.arg)
		elif isinstance(node,Not): return FreeVars.freeVarsHelper(node.expr)
		elif isinstance(node,Assign): return FreeVars.freeVarsHelper(node.expr)
		elif isinstance(node,Printnl): return FreeVars.freeVarsHelper(node.nodes[0])
		elif isinstance(node,Return): return FreeVars.freeVarsHelper(node.value)			
		else: raise Exception(str(node) + " is an unsupported node type")
	
	@staticmethod
	def freeVars(IR):
		global freeVarsSet
		for i in IR.node.nodes:
			freeVarsSet = freeVarsSet | FreeVars.freeVarsHelper(i)
		return (freeVarsSet,variableMapping)
