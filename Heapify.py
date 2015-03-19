from compiler.ast import *
from PythonASTExtension import *

class FlattenTracker():
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
	
	def __init__(self,IR):
		self.freeVariables = {}
		self.IR = IR
		self.heapifySet = set()
		self.renameParameter = FlattenTracker("heapifyParam")
	
	def freeVars(self,node):
		#Const and Name are the base cases
		if isinstance(node,Const): return set([])
		elif isinstance(node,Name): return set([node.name])
		elif isinstance(node,Add): return self.freeVars(node.left) | self.freeVars(node.right)
		elif isinstance(node,CallFunc):
			fv_args = [self.freeVars(e) for e in node.args]
			free_in_args = reduce(lambda a, b:a, a|b, fv_args, set([]))
			return self.freeVars(node.node) | free_in_args
		elif isinstance(node,Lambda):
			save = set()
			if isinstance(node.code,Stmt):
				for x in node.code.nodes:
					save = save | self.freeVars(x)
			else: save = save | self.freeVars(node.code)
			return save - set(node.argnames)
		elif isinstance(node,UnarySub): return self.freeVars(node.expr)
		elif isinstance(node,List):
			fv_args = [self.freeVars(e) for e in node.nodes]
			free_in_args = reduce(lambda a, b:a, a|b, fv_args, set([]))
			return free_in_args			
		elif isinstance(node,Dict):
			fv_args = [self.freeVars(e) for e[0] in node.items]
			fv_args2 = [self.freeVars(e) for e[1] in node.items]
			free_in_args = reduce(lambda a, b:a, a|b, fv_args, set([]))
			free_in_args2 = reduce(lambda a, b:a, a|b, fv_args2, set([]))
			free_in_args3 = free_in_args | free_in_args
			return free_in_args3
		elif isinstance(node,Subscript):
			expression = self.freeVars(node.expr)
			subs = [self.freeVars(sub) for sub in node.subs]
			free_in_args = reduce(lambda a, b:a, a|b, subs, set([]))
			free_in_args2 = expression | free_in_args
			return free_in_args2
		elif isinstance(node,IfExp):
			save = self.freeVars(node.test)
			if isinstance(node.then,Stmt):
				for i in node.then.nodes:
					save = save | self.freeVars(i)
			else:
				save = save | self.freeVars(node.then)
			if isinstance(node.else_,Stmt):
				for i in node.else_.nodes:
					save = save | self.freeVars(i)
			else:
				save = save | self.freeVars(node.else_)
			return save			
		elif isinstance(node,Compare): return self.freeVars(node.expr) | self.freeVars(node.ops[0][1])	
		elif isinstance(node,And):
			save = set()
			for i in node.nodes:
				save = save | self.freeVars(i)
			return save			
		elif isinstance(node,Or):
			save = set()
			for i in node.nodes:
				save = save | self.freeVars(i)
			return save				
		elif isinstance(node,Let):
			save = self.freeVars(node.var)
			if isinstance(node.expr,Let): save = save | self.freeVars(node.expr)
			else: save = save | self.freeVars(node.body)
			return save			
		elif isinstance(node,InjectFrom): return self.freeVars(node.arg)
		elif isinstance(node,GetTag): return self.freeVars(node.arg)
		elif isinstance(node,ProjectTo): return self.freeVars(node.arg)
		elif isinstance(node,Not): return self.freeVars(node.expr)
		elif isinstance(node,Assign): return self.freeVars(node.expr)
		elif isinstance(node,Printnl): return self.freeVars(node.nodes[0])
		else: raise Exception("Unsupported node type")
	
	def needHeapification(self,node):
		if isinstance(node,Lambda):
			if isinstance(node.code,Stmt):
				save = set()
				for x in node.code.nodes:
					if isinstance(x,Lambda): save = save |  self.needHeapification(x)
					else: save = save | self.freeVars(x)
				self.heapifySet = self.heapifySet | save
			elif isinstance(node.code,Lambda): self.heapifySet = self.heapifySet | self.needHeapification(node.code)
			else: self.heapifySet = self.heapifySet | self.freeVars(node)
		else: return self.heapifySet
	
	def heapify(self,node):
		#Name and Assign are base cases
		if isinstance(node,Name):
			if node.name in self.heapifySet: return Subscript(node.name,'OP_APPLY',[Const(DecimalValue(0))])
			else: return node
		elif isinstance(node,Assign):
			if isinstance(node.nodes[0],AssName) and isinstance(node.expr,Name):
				if node.expr.name in self.heapifySet:
					return Assign(Subscript(node.name,FLAGS,[Const(DecimalValue(0))]),self.heapify(node.expr))
			else: return node
		if isinstance(node,Const): return node
		elif isinstance(node,Add): return Add(self.heapify(node.left),self.freeVars(node.right))
		elif isinstance(node,CallFunc): return CallFunc(node.name,[self.heapify(e) for e in node.args])
		elif isinstance(node,Lambda):
			save = []
			arg_save = []
			for arg in node.argnames:
				if arg in self.heapifySet:
					new_arg = self.renameParamater.getNameAndIncrementCounter()
					initialize = Assign([AssName(arg,'OP_APPLY')],CallFunc("create_list",[1,0]))
					assign = Assign(Subscript(arg,'OP_APPLY',[Const(DecimalValue(0))]),Name(new_arg))
					arg_save += [new_arg]
					save += [initalize,assign]
				else: arg_save += [arg]
			if isinstance(node.code,Stmt):
				save += [self.heapify(x) for x in node.code.nodes]
			else: save += self.heapify(node.code)
			return Lambda(arg_save,save)
		elif isinstance(node,UnarySub): return UnarySub(self.heapify(node.expr))
		elif isinstance(node,List): return List([self.heapify(e) for e in node.nodes])	
		elif isinstance(node,Dict): return Dict([(self.heapify(e[0]),self.heapify(e[1])) for e in node.items])
		elif isinstance(node,Subscript): return Subscript(self.heapify(node.expr), 'OP_APPLY',[self.heapify(e) for e in node.subs])
		elif isinstance(node,IfExp):
			savethen = []
			saveelse = []
			if isinstance(node.then,Stmt): savethen += [self.heapify(e) for e in node.then.nodes]
			else: savethen = self.heapify(node.then)
			if isinstance(node.else_,Stmt): saveelse += [self.heapify(e) for e in node.else_.nodes]
			else: saveelse = self.heapify(node.else_)
			return IfExp(self.heapify(ast.test),savethen,saveelse)	
		elif isinstance(node,Compare): return Compare(self.heapify(node.expr),self.freeVars(node.ops[0][1]))
		elif isinstance(node,And): return And([self.heapify(e) for e in node.nodes])
		elif isinstance(node,Or): return Or([self.heapify(e) for e in node.nodes])	
		elif isinstance(node,Let): return Let(self.heapify(node.var),self.heapify(node.expr),self.heapify(node.body))		
		elif isinstance(node,InjectFrom): return InjectFrom(node.typ,self.heapify(node.arg))
		elif isinstance(node,GetTag): return GetTag(self.heapify(node.arg))
		elif isinstance(node,ProjectTo): return ProjectTo(node.typ,self.heapify(node.arg))
		elif isinstance(node,Not): return Not(self.heapify(node.expr))
		elif isinstance(node,Printnl): return Printnl(self.heapify(node.nodes[0]))
		else: return node

	def heapifyInstructions(self):
		for instruction in self.IR.node.nodes:
			self.needHeapification(instruction) 
		stmt = [self.heapify(i) for i in self.IR.node.nodes]
		return Module(stmt)
