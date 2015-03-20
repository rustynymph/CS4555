from compiler.ast import *
import copy
import Queue
from PythonASTExtension import *

class LivenessAnalysis():
	def __init__(self,IR):
		self.liveVariables = {}
		self.IR = IR.node.nodes
	
	def liveness(self,node,prevSet):
		if isinstance(node,Assign):
			finSet = self.liveness(node.expr,prevSet)
			node.liveness = finSet | prevSet
			return finSet
		
		if isinstance(node,AssName):
			finSet = set([])
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,Subscript):
			finSet = self.liveness(node.expr)
			for i in node.subs:
				finSet = finSet | self.liveness(i,prevSet)
			node.liveness = finSet | prevSet 
			return finSet	
	
		elif isinstance(node,Name):
			finSet = set([node.name])
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,Const):
			finSet = set([])
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,CallFunc):
			save = set()
			for i in node.args:
				save = save | self.liveness(i,prevSet)
			node.liveness = save | prevSet
			return save
	
		elif isinstance(node,IfExp):
			save = self.liveness(node.test,prevSet)
			if isinstance(node.then,Stmt):
				for i in node.then.nodes:
					save = save | self.liveness(i,prevSet)
			else:
				save = save | self.liveness(node.then,prevSet)
			if isinstance(node.else_,Stmt):
				for i in node.else_.nodes:
					save = save | self.liveness(i,prevSet)
			else:
				save = save | self.liveness(node.else_,prevSet)
			node.liveness = save | prevSet
			return save
	
		elif isinstance(node,UnarySub):
			finSet = self.liveness(node.expr,prevSet)
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,Add):
			finSet = self.liveness(node.left,prevSet) | self.liveness(node.right,prevSet)
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,Dict):
			save = set()
			for i in node.items:
				save = save | self.liveness(i[0],prevSet) | self.liveness(i[1],prevSet)
			node.liveness = save | prevSet
			return save
	
		elif isinstance(node,List):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i,prevSet)
			node.liveness = save | prevSet
			return save
	
		elif isinstance(node,Not):
			finSet = self.liveness(node.expr,prevSet)
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,And):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i,prevSet)
			node.liveness = save | prevSet
			return save
	
		elif isinstance(node,Or):
			save = set()
			for i in node.nodes:
				save = save | self.liveness(i,prevSet)
			node.liveness = save | prevSet
			return save
	
		elif isinstance(node,Compare):
			finSet = self.liveness(node.expr,prevSet) | self.liveness(node.ops[0][1],prevSet)	
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,InjectFrom):
			finSet = self.liveness(node.arg,prevSet)
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,ProjectTo):
			finSet = self.liveness(node.arg,prevSet)
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,GetTag):
			finSet = self.liveness(node.arg,prevSet)
			node.liveness = finSet | prevSet
			return finSet
	
		elif isinstance(node,AssignCallFunc):
			finSet = self.liveness(node.name,prevSet)
			node.liveness = finSet | prevSet
			return finSet
		
		elif isinstance(node,Function):
			save = self.liveness(node.name,prevSet)
			if isinstance(node.code,Stmt):
				for i in node.code.nodes:
					save = save | self.liveness(i,prevSet)
			else:
				save = save | self.liveness(node.code,prevSet)
			node.liveness = save | prevSet
			return save
		
		elif isinstance(node,Lambda):
			save = set()
			if isinstance(node.code,Stmt):
				for i in node.code.nodes:
					save = save | self.liveness(i,prevSet)
			else:
				save = save | self.liveness(node.code,prevSet)
			node.liveness = save | prevSet
			return save
		
		elif isinstance(node,Return):
			save = set()
			if isinstance(node.value,Stmt):
				for i in node.value.nodes:
					save = save | self.liveness(i,prevSet)
			else:
				save = save | self.liveness(node.value,prevSet)
			node.liveness = save | prevSet
			return save		
	
		else: raise Exception(str(node) + " is an unsupported node type")
	
	def computeLivenessAnalysis(self,ast,j):
		remove = set()
		if isinstance(ast,Assign):
			remove = self.liveness(ast.nodes[0],self.liveVariables[j+1])
			new_set = (self.liveVariables[j+1] - remove) | self.liveness(ast.expr,self.liveVariables[j+1])
			ast.liveness = new_set
		else:
			new_set = self.liveVariables[j+1] | self.liveness(ast,self.liveVariables[j+1])
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
