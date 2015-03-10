from compiler.ast import *
from AssemblyAST import *
#from LivenessAnalysis import*

class Translator:
	def __init__(self,coloredgraph):
		self.coloredgraph = coloredgraph
		self.memory = {}
	
	def getVariableLocation(variable):
		register = getRegister(variable)
		if register: return register
		else: return getVariableInMemory(variable)
		
	def getVariableInMemory(variable): return self.memory[variable]
	
	def getRegister(variable): return self.coloredgraph[variable]
	
	def putVariableInMemory(variable):
		if variable not in self.memory:
			self.memory[variable] = MemoryOperand(Registers32.EBP,self.getActivationRecordSize())
	
	def getActivationRecordSize(self): return 4*(len(self.memory)+1)
	
	def translateToX86(self,ast):
		if isinstance(ast,Module):
			assFunction = AssemblyFunction(SectionHeaderInstruction("main"),ast.node,self.getActivationRecordSize(),ConstantOperand(DecimalValue(0)))
			clusteredAssFunction = ClusteredInstruction([assFunction])
			return AssemblyProgram(EntryPointInstruction(NameOperand("main")),clusteredAssFunction)
		
		if isinstance(ast,Stmt): return ClusteredInstruction(ast.nodes)			
		
		elif isinstance(ast,Const): return ConstantOperand(DecimalValue(ast.value))

		elif isinstance(ast,AssName):
			putVariableInMemory(ast.name)
			return getVariableLocation(ast.name)

		elif isinstance(ast,Name): return getVariableLocation(ast.name)

		elif isinstance(ast,CallFunc):
			callersavedvariables = []
			for variable in coloredgraph:
				if isinstance(coloredgraph[variable],CallerSavedRegister):
					callersavedvariables += [variable]
					#not finished
					
		elif isinstance(ast,InjectFrom):
			location = getVariableLocation(ast.arg)
			tag = ConstantOperand(DecimalValue(ast.typ))
			if ast.typ != 3:
				shiftLeftInstr = ShiftLeftInstruction(ConstantOperand(DecimalValue(2)),location)
				orInstr = OrInstruction(tag,location)
				return ClusteredInstruction([shiftLeftInstr,orInstr])
			else: return OrInstruction(tag,location)
			
		elif isinstance(ast,ProjectTo):
			location = getVariableLocation(ast.arg)
			if ast.typ != 3:
				shiftRightInstr = ShiftArithmeticRightInstruction(ConstantOperand(DecimalValue(2)),location)
				andInstr = AndInstruction(ConstantOperand(DecimalValue(-4)),location)
				return ClusteredInstruction([shiftRightInstr,andInstr])
			else: return AndInstruction(ConstantOperand(DecimalValue(-4)),location)
		
		
		else: return ast
