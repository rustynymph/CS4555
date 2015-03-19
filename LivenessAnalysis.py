from compiler.ast import *
import copy
import Queue
from PythonASTExtension import *

class LivenessAnalysis():
	def __init__(self,IR):
		self.liveVariables = {}
		self.IR = IR.node.nodes
	
	def liveness(self,node):
		if isinstance(node,Assign):
			node.liveness = self.liveness(node.expr)
			return node.liveness
		
		if isinstance(node,AssName):
			node.liveness = set([])
			return node.liveness
	
		elif isinstance(node,Subscript):
			node.liveness = self.liveness(node.expr) | self.liveness(node.subs[0])
			return node.liveness		
	
		elif isinstance(node,Name):
			node.liveness = set([node.name])
			return node.liveness
	
		elif isinstance(node,Const):
			node.liveness = set([])
			return node.liveness
	
		elif isinstance(node,CallFunc):
			save = set()
			for i in node.args:
				save = save | self.liveness(i)
			node.liveness = save
			print save
			return node.liveness
	
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
			node.liveness = save
			return node.liveness
	
		elif isinstance(node,UnarySub):
			node.liveness = self.liveness(node.expr)
			return node.liveness
	
		elif isinstance(node,Add):
			node.liveness = self.liveness(node.left) | self.liveness(node.right)
			return node.liveness
	
		elif isinstance(node,Dict):
			save = set()
			for i in node.items:
				save = save | self.liveness(i[0]) | self.liveness(i[1])
			node.liveness = save
			return node.liveness
	
		elif isinstance(node,List):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i)
			node.liveness = save
			return node.liveness
	
		elif isinstance(node,Not):
			node.liveness = self.liveness(node.expr)
			return node.liveness
	
		elif isinstance(node,And):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i)
			node.liveness = save
			return node.liveness
	
		elif isinstance(node,Or):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i)
			node.liveness = save
			return node.liveness
	
		elif isinstance(node,Compare):
			node.liveness = self.liveness(node.expr) | self.liveness(node.ops[0][1])	
			return node.liveness
	
		elif isinstance(node,InjectFrom):
			node.liveness = self.liveness(node.arg)
			return node.liveness
	
		elif isinstance(node,ProjectTo):
			node.liveness = self.liveness(node.arg)
			return node.liveness
	
		elif isinstance(node,GetTag):
			node.liveness = self.liveness(node.arg)
			return node.liveness
	
		elif isinstance(node,AssignCallFunc):
			node.liveness = self.liveness(node.name)
			return node.liveness
		
		elif isinstance(node,Function):
			save = self.liveness(node.name)
			if isinstance(node.code,Stmt):
				for i in node.code.nodes:
					save = save | self.liveness(i)
			else:
				save = save | self.liveness(node.code)
			node.liveness = save
			return node.liveness
		
		elif isinstance(node,Lambda):
			save = set()
			if isinstance(node.code,Stmt):
				for i in node.code.nodes:
					save = save | self.liveness(i)
			else:
				save = save | self.liveness(node.code)
			node.liveness = save
			return node.liveness
		
		elif isinstance(node,Return):
			save = set()
			if isinstance(node.value,Stmt):
				for i in node.value.nodes:
					save = save | self.liveness(i)
			else:
				save = save | self.liveness(node.value)
			node.liveness = save
			return node.liveness					
	
		else: raise Exception("Unsupported node type")
	
	def computeLivenessAnalysis(self,ast,j):
		remove = set()
		if isinstance(ast,Assign):
			remove = self.liveness(ast.nodes[0])
			new_set = (self.liveVariables[j+1] - remove) | self.liveness(ast.expr)
		else:
			new_set = self.liveVariables[j+1] | self.liveness(ast)
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
