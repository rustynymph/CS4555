from PythonASTExtension import *
from AssemblyAST import *
import copy

class MemoryAssignment:
	
	def __init__(self,memoryLocations):
		self.memory = {}
		self.memoryLocations = memoryLocations

	@staticmethod
	def getParameterMemoryLocations(ast,acc):
		if isinstance(ast,Function):
			partialAcc = {}
			for i in range(-len(ast.argnames),0):
				partialAcc = dict(partialAcc.items() +  {ast.argnames[i]:MemoryOperand(Registers32.EBP,-i * 4)}.items())
			return dict(partialAcc.items() + acc.items())
		else: return acc

	def assignMemoryLocationMap(self,ast):
		if isinstance(ast,AssName) or isinstance(ast,Name):
			if ast.name not in self.memory and ast.name not in self.memoryLocations: self.memory[ast.name]  = MemoryOperand(Registers32.EBP,-4*(len(self.memory)+1))
			# if ast.name in self.memoryLocations: self.memory[ast.name] = self.memoryLocations[ast.name]
			if ast.name not in self.memoryLocations: ast.memory = self.memory[ast.name]
			else:ast.memory = self.memoryLocations[ast.name]
			return ast
		elif isinstance(ast,Function):
			ast.memory = copy.deepcopy(self.memory)
			self.memory = {}
			return ast
		else: return ast;

