from compiler.ast import *
from AssemblyAST import *
#from LivenessAnalysis import*

class Translator:
	def __init__(self,coloredgraph,liveness):
		self.coloredgraph = coloredgraph
		self.liveness = liveness
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

'''	
	def spill(variable):
		for x in coloredgraph:
			if coloredgraph[x] 
'''
	
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
					
			if len(ast.args) > 0:
				pushArgsInstr = [PushInstruction(getVariableLocation(arg)) for arg in ast.args]
			else: pushArgsInstr = []		
					
			saveInstr = [MoveInstruction(getVariableLocation(var),getVariableInMemory(var)) for var in callersavedvariables]
			callInstr = [CallInstruction(ast.node)]
			loadInstr = [MoveInstruction(getVariableInMemory(var),getVariableLocation(var)) for var in callersavedvariables]
			return ClusteredInstruction(saveInstr + pushArgsInstr + callInstr + loadInstr)
					
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
		
		elif isinstance(ast,GetTag): return AndInstruction(ConstantOperand(DecimalValue(3)),getVariableInMemory(ast.arg))

		elif isinstance(ast, Assign):
			
		elif isinstance(ast,Compare): return CompareInstruction()
		
		elif isinstance(ast,UnarySub): return NegativeInstruction(getVariableInMemory(ast.arg))
			
		elif isinstance(ast,IfExp):
			test = getVariableLocation(ast.test)
			
			jumpInst = JumpInstruction(test,
			
		elif isinstance(ast,Add):
			leftAdd = getVariableLocation(ast.left)
			rightAdd = getVariableLocation(ast.right)
		
		else: return ast
