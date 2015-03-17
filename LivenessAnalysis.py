from compiler.ast import *
import copy
import Queue
from PythonASTExtension import *

class LivenessAnalysis():
	def __init__(self,IR):
		self.liveVariables = {}
		self.IR = IR.node.nodes
	
	def liveness(self,node):
		if isinstance(node,Assign): return self.liveness(node.expr)
		
		if isinstance(node,AssName): return set([])
	
		elif isinstance(node,Subscript): return self.liveness(node.expr) | self.liveness(node.subs[0])		
	
		elif isinstance(node,Name): return set([node.name])
	
		elif isinstance(node,Const): return set([])
	
		elif isinstance(node,CallFunc):
			save = set()
			for i in node.args:
				save = save | self.liveness(i)
			return save
	
		elif isinstance(node,IfExp):
			save = self.liveness(node.test)
			if isinstance(node.then,Stmt):
				for i in node.then.nodes:
					save = save | self.liveness(i)
			else:
				save = save | self.liveness(node.then)
			if isinstance(node.else_,Stmt):
				for i in node.else_.nodes:
					save = save | self.liveness(i)
			else:
				save = save | self.liveness(node.else_)
			return save
	
		elif isinstance(node,UnarySub): return self.liveness(node.expr)
	
		elif isinstance(node,Add): return self.liveness(node.left) | self.liveness(node.right)
	
		elif isinstance(node,Dict):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i[0]) | self.liveness(i[1])
			return save
	
		elif isinstance(node,List):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i)
			return save
	
		elif isinstance(node,Not): return self.liveness(node.expr)
	
		elif isinstance(node,And):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i)
			return save
	
		elif isinstance(node,Or):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i)
			return save
	
		elif isinstance(node,Compare): return self.liveness(node.expr) | self.liveness(node.ops[0][1])	
	
		elif isinstance(node,InjectFrom): return self.liveness(node.arg)
	
		elif isinstance(node,ProjectTo): return self.liveness(node.arg)
	
		elif isinstance(node,GetTag): return self.liveness(node.arg)
	
		elif isinstance(node,AssignCallFunc): return self.liveness(node.name)
		
		elif isinstance(node,Function):
			save = self.liveness(node.name)
			if isinstance(node.code,Stmt):
				for i in node.code.nodes:
					save = save | self.liveness(i)
			else:
				save = save | self.liveness(node.code)
		
		elif isinstance(node,Lambda):
			save = set()
			if isinstance(node.code,Stmt):
				for i in node.code.nodes:
					save = save | self.liveness(i)
			else:
				save = save | self.liveness(node.code)
			return save
		
		elif isinstance(node,Return): return self.liveness(node.value)		
	
		else: raise Exception("Unsupported node type")
	
	def computeLivenessAnalysis(self,ast,j):
		remove = set()
		if isinstance(ast,Assign):
			remove = self.liveness(ast.nodes[0])
			new_set = (self.liveVariables[j+1] - remove) | self.liveness(ast.expr)
		else:
			new_set = self.liveness(ast)
		return new_set
			
	def livenessAnalysis(self):
		ir = self.IR
		numInstructions = len(ir)
		for i in range (numInstructions,-1,-1):
			self.liveVariables[i] = set()
		j = numInstructions-1
		for instructions in reversed(ir):
			print instructions
			self.liveVariables[j] = self.computeLivenessAnalysis(instructions,j)
			j-=1
		return [self.liveVariables[x] for x in self.liveVariables]				
