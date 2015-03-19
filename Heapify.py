from compiler.ast import *
from PythonASTExtension import *

class Heapify(node):
	
	def __init__(self,IR):
		self.freeVariables = {}
		self.IR = IR.node.nodes
		self.heapifySet = set()
	
	def freeVars(self,node):
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
			if isinstance(node.expr,Let): return save = save | self.freeVars(node.expr)
			save = save | self.freeVars(node.body)
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
			if isinstance(node.code,Lambda):
				self.heapifySet = self.heapifySet |  self.needHeapification(node.code)
			else: 
				if isinstance(node.code,Stmt):
					save = set()
					for node in node.code.nodes:
						save = save | self.freeVars(node)
					self.heapifySet = self.heapifySet | save
				else: self.heapifySet = self.heapifySet | self.freeVars()
	
	def heapify(self,ast):
		if isinstance(ast,Name):
			if ast.name in self.heapifySet: return Subscript(ast.name,FLAGS,[Const(DecimalValue(0))])
		elif isinstance(ast,Assign):
			if isinstance(ast.nodes[0],AssName) and isinstance(ast.expr,Name):
				if ast.expr.name in self.heapifySet:
					return Assign(Subscript(ast.name,FLAGS,[Const(DecimalValue(0))]),self.heapify(ast.expr))
		else: return ast

	def heapifyInstructions(self,IR): return [self.heapify(i) for i in self.IR]
