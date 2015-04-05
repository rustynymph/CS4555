from PythonASTExtension import *
from AssemblyAST import *
import copy

class MemoryAssignment:
	
	def __init__(self,parameterLocations,preassignedMemoryLocations):
		self.memory = {}
		self.parameterLocations = parameterLocations
		self.preassignedMemoryLocations = preassignedMemoryLocations

	@staticmethod
	def variablesWithAssociatedFunctions(ast,acc):
		if isinstance(ast,Function):
			return (dict(acc[0].items() + {ast.name:acc[1]}.items()),set([]))
		elif isinstance(ast,Name):
			return (acc[0],acc[1] | set([ast.name]))
		else: return acc

	@staticmethod
	def assignRegisterMemoryLocation(functionVariableMapping):
		functionDictionary = {}
		for functionName in functionVariableMapping:
			registerToMemory = {}
			functionVariables = functionVariableMapping[functionName].items()
			for i in range(len(functionVariables)):
				register = functionVariables[i][1]
				if register not in registerToMemory:
					memory = MemoryOperand(Registers32.EBP,-(len(registerToMemory)+1)*4)
					registerToMemory[register] = memory
			functionDictionary[functionName] = registerToMemory
		return functionDictionary

	@staticmethod
	def assignVariableWithRegisterMapping(functionVariableMapping,functionRegisterMapping):
		functionVariableMemoryMapping = {}
		for functionName in functionVariableMapping:
			variableToMemory = {}
			functionVariables = functionVariableMapping[functionName].items()
			functionRegister = functionRegisterMapping[functionName]
			for i in range(len(functionVariables)):
				variable = functionVariables[i][0]
				register = functionVariables[i][1]
				memory = functionRegister[register]
				variableToMemory[variable] = memory
			functionVariableMemoryMapping[functionName] = variableToMemory
		return functionVariableMemoryMapping


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
			if ast.name not in self.memory and ast.name not in self.parameterLocations and ast.name not in self.preassignedMemoryLocations: 
				self.memory[ast.name]  = MemoryOperand(Registers32.EBP,-4*(len(self.memory)+len(self.preassignedMemoryLocations)+1))
			# if ast.name in self.parameterLocations: self.memory[ast.name] = self.parameterLocations[ast.name]
			if ast.name not in self.parameterLocations and ast.name not in self.preassignedMemoryLocations: 
				ast.memory = self.memory[ast.name]
			elif ast.name in self.preassignedMemoryLocations: ast.memory = self.preassignedMemoryLocations[ast.name]
			else:ast.memory = self.parameterLocations[ast.name]
			return ast
		elif isinstance(ast,Function):
			ast.memory = copy.deepcopy(self.memory)
			self.memory = {}
			return ast
		else: return ast;

