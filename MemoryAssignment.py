from PythonASTExtension import *
from AssemblyAST import *
import copy

class MemoryAssignment:
	
	def __init__(self,coloredGraph):
		self.memory = {}
		self.coloredGraph = coloredGraph

	def assignMemoryLocationMap(self,ast):
		if isinstance(ast,AssName) or isinstance(ast,Name):
			if ast.name not in self.memory: self.memory[ast.name] = MemoryOperand(Registers32.EBP,-4*(len(self.memory)+1))
			ast.memory = self.memory[ast.name]
			return ast
		elif isinstance(ast,Function):
			ast.memory = copy.deepcopy(self.memory)
			self.memory = {}
			return ast
		else: return ast;

