from compiler.ast import *
from AssemblyAST import *
from PythonASTExtension import *

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

	def evictVariable(self):
		evictedVariable = self.getInvertedGraph(self.coloredgraph)[Registers32.EAX][0]
		evictedVariableMemoryLocation = getVariableInMemory(evictedVariable)
		return MoveInstruction(Registers32.EAX,evictedVariableMemoryLocation)		
		
	def unevictVariable(self): return MoveInstruction(evictedVariableMemoryLocation,Registers32.EAX)

	def translateToX86(self,ast):
		if isinstance(ast,Module):
			print self.getActivationRecordSize()
			assFunction = AssemblyFunction(SectionHeaderInstruction("main"),ast.node,self.getActivationRecordSize(),ConstantOperand(DecimalValue(0)))
			clusteredAssFunction = ClusteredInstruction([assFunction])
			return AssemblyProgram(EntryPointInstruction(NameOperand("main")),clusteredAssFunction)
		
		elif isinstance(ast,Stmt): return ClusteredInstruction(ast.nodes)			
		
		elif isinstance(ast,Const): return ConstantOperand(DecimalValue(ast.value))

		elif isinstance(ast,AssName):
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

		elif isinstance(ast, Assign): return MoveInstruction(ast.expr,self.getVariableLocation(ast.nodes[0]))
			
		elif isinstance(ast,Compare):
			leftcmp = self.getVariableLocation(ast.expr)
			rightcmp = self.getVariableLocation(ast.ops[1])
			reg = RegisterOperand(Registers32.EAX)
			if isinstance(leftcmp,MemoryOperand) and isinstance(rightcmp,MemoryOperand):
				evictInstr = self.evictVariable()
				moveright = MoveInstruction(rightcmp,reg)
				compareInstr = CompareInstruction(leftcmp,reg)
				savecmp = MoveInstruction(reg,rightcmp)
				unevictInstr = self.unevictVariable()
				return ClusteredInstruction([evictInstr,moveright,compareInstr,savecmp,unevictInstr])
			return CompareInstruction(leftcmp,rightcmp)
		
		elif isinstance(ast,UnarySub):
			usub = self.getVariableLocation(ast.expr)
			if isinstance(usub,MemoryOperand):
				reg = RegisterOperand(Registers32.EAX)
				evictInstr = self.evictVariable()
				moveNegIntoEAX = MoveInstruction(usub,reg)
				negate = NegativeInstruction(reg)
				saveneg = MoveInstruction(reg,usub)
				unevictInstr = self.unevictVariable()
				return ClusteredInstruction([evictInstr,moveNegIntoEAX,negate,saveneg,unevictInstr])
			return NegativeInstruction(usub)
			
		elif isinstance(ast,IfExp):
			test = getVariableLocation(ast.test)
			compareInstr = CompareInstruction(ConstantOperand(DecimalValue(1)),test)
			jumpInstr = JumpInstruction(test,SIGNEDGREATER)
			#how are we jumping TO a location?
			return ClusteredInstruction([compareInstr,jumpInstr])
			
		elif isinstance(ast,Add):
			leftAdd = self.getVariableLocation(ast.left)
			rightAdd = self.getVariableLocation(ast.right)

			if isinstance(rightAdd,MemoryOperand):
				reg = RegisterOperand(Registers32.EAX)
				evictInstr = self.evictVariable()
				moveRightAddIntoEAX = MoveInstruction(rightAdd,reg)
				add = AddInstruction(leftAdd,reg)
				saveadd = MoveInstruction(reg,rightAdd)
				unevictInstr = self.unevictVariable()

				return ClusteredInstruction([evictInstr,moveRightAddIntoEAX,add,saveadd,unevictInstr])
			else: return AddInstruction(leftAdd,rightAdd)
		
		else: return ast
