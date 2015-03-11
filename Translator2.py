from compiler.ast import *
from AssemblyAST import *
from PythonASTExtension import *
#from LivenessAnalysis import*

class Translator:
	def __init__(self,coloredgraph,liveness):
		self.coloredgraph = coloredgraph
		self.liveness = liveness
		self.memory = {}
	
	def getInvertedGraph(self,coloredgraph):
		invertedgraph = {}
		for k in coloredgraph: invertedgraph[k] = []

		for k,v in coloredgraph.items(): invertedgraph[k] += [v]
		return invertedgraph

	def getVariableLocation(self,variable):
		register = self.getRegister(variable)
		if register: return register
		else: return self.getVariableInMemory(variable)

		
	def getVariableInMemory(self,variable): return self.memory[variable]
	
	def getRegister(self,variable): 
		if variable in self.coloredgraph: return self.coloredgraph[variable]
		else: return None
	
	def putVariableInMemory(self,variable):
		if variable not in self.memory:
			self.memory[variable] = MemoryOperand(Registers32.EBP,self.getActivationRecordSize())
	
	def getActivationRecordSize(self): return 4*(len(self.memory)+1)


	def translateToX86(self,ast):
		if isinstance(ast,Module):
			print self.getActivationRecordSize()
			assFunction = AssemblyFunction(SectionHeaderInstruction("main"),ast.node,self.getActivationRecordSize(),ConstantOperand(DecimalValue(0)))
			clusteredAssFunction = ClusteredInstruction([assFunction])
			return AssemblyProgram(EntryPointInstruction(NameOperand("main")),clusteredAssFunction)
		
		elif isinstance(ast,Stmt): return ClusteredInstruction(ast.nodes)			
		
		elif isinstance(ast,Const): return ConstantOperand(DecimalValue(ast.value))

		elif isinstance(ast,AssName):
			print "AssName"
			print ast.name
			self.putVariableInMemory(ast.name)
			return self.getVariableLocation(ast.name)

		elif isinstance(ast,Name): return self.getVariableLocation(ast.name)

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
		
		elif isinstance(ast,GetTag): return AndInstruction(ConstantOperand(DecimalValue(3)),self.getVariableLocation(ast.arg))

		# elif isinstance(ast, Assign):
			
		elif isinstance(ast,Compare): return CompareInstruction()
		
		elif isinstance(ast,UnarySub): return NegativeInstruction(self.getVariableLocation(ast.arg))
			
		elif isinstance(ast,IfExp):
			test = getVariableLocation(ast.test)
			return ast
			
			# jumpInst = JumpInstruction(test,
			
		elif isinstance(ast,Add):
			leftAdd = getVariableLocation(ast.left)
			rightAdd = getVariableLocation(ast.right)

			if isinstance(leftAdd,MemoryOperand) and isinstance(rightAdd,MemoryOperand):
				evictedVariable = self.getInvertedGraph(self.coloredgraph)[Registers32.EAX][0]
				evictedVariableMemoryLocation = getVariableInMemory(evictedVariable)
				moveEvictedVariableIntoMemory = MoveInstruction(Registers32.EAX,evictedVariableMemoryLocation)

				moveRightAddIntoEAX = MoveInstruction(rightAdd,Registers32.EAX)
				add = AddInstruction(Registers32.EAX,leftAdd)

				unevictVariable = MoveInstruction(evictedVariableMemoryLocation,Registers32.EAX)

				return ClusteredInstruction([moveEvictedVariableIntoMemory,moveRightAddIntoEAX,add,unevictVariable])
			else: return AddInstruction(rightAdd,leftAdd)
		
		else: return ast
