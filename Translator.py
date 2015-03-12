from compiler.ast import *
from AssemblyAST import *
from PythonASTExtension import *

class Translator():
	def __init__(self,coloredgraph):
		self.coloredgraph = coloredgraph
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
		reg = RegisterOperand(Registers32.EAX)
		evictedVariable = self.getInvertedGraph(self.coloredgraph)[reg][0]
		evictedVariableMemoryLocation = getVariableInMemory(evictedVariable)
		return MoveInstruction(reg,evictedVariableMemoryLocation)		
		
	def unevictVariable(self): return MoveInstruction(evictedVariableMemoryLocation,RegisterOperand(Registers32.EAX))

	def translateToX86(self,ast):
		if isinstance(ast,Module):
			assFunction = AssemblyFunction(SectionHeaderInstruction("main"),ast.node,self.getActivationRecordSize(),ConstantOperand(DecimalValue(0)))
			clusteredAssFunction = ClusteredInstruction([assFunction])
			return AssemblyProgram(EntryPointInstruction(NameOperand("main")),clusteredAssFunction)
		
		elif isinstance(ast,Stmt): return ClusteredInstruction(ast.nodes)			
		
		elif isinstance(ast,Const): return ConstantOperand(DecimalValue(ast.value))

		elif isinstance(ast,AssName):
			self.putVariableInMemory(ast.name)
			return self.getVariableLocation(ast.name)

		elif isinstance(ast,Name):
			if ast.name in self.memory:	return self.getVariableLocation(ast.name)
			else: return NameOperand(ast.name)

		elif isinstance(ast,CallFunc):
			callersavedvariables = []
			
			for variable in self.coloredgraph:
				if isinstance(self.coloredgraph[variable],CallerSavedRegister):
					callersavedvariables += [variable]
					
			if len(ast.args) > 0:
				pushArgsInstr = [PushInstruction(arg) for arg in ast.args]
			else: pushArgsInstr = []		
					
			saveInstr = [MoveInstruction(self.getVariableLocation(var),self.getVariableInMemory(var)) for var in callersavedvariables]
			callInstr = [CallInstruction(ast.node)]
			loadInstr = [MoveInstruction(self.getVariableInMemory(var),self.getVariableLocation(var)) for var in callersavedvariables]
			return ClusteredInstruction(saveInstr + pushArgsInstr + callInstr + loadInstr)
					
		elif isinstance(ast,InjectFrom):
			location = ast.arg
			tag = ast.typ
			if ast.typ != 3:
				shiftLeftInstr = ShiftLeftInstruction(ConstantOperand(DecimalValue(2)),location)
				orInstr = OrInstruction(tag,location)
				return ClusteredInstruction([shiftLeftInstr,orInstr])
			else: return OrInstruction(tag,location)
			
		elif isinstance(ast,ProjectTo):
			location = ast.arg
			if ast.typ != 3:
				shiftRightInstr = ShiftArithmeticRightInstruction(ConstantOperand(DecimalValue(2)),location)
				andInstr = AndInstruction(ConstantOperand(DecimalValue(-4)),location)
				return ClusteredInstruction([shiftRightInstr,andInstr])
			else: return AndInstruction(ConstantOperand(DecimalValue(-4)),location)
		
		elif isinstance(ast,GetTag): return AndInstruction(ConstantOperand(DecimalValue(3)),ast.arg)

		elif isinstance(ast, Assign):
			if isinstance(ast.expr,Operand):
				fromOperand = ast.expr
				toOperand = ast.nodes[0]
				clusteredArrayBefore = []
				clusteredArrayAfter = []
				if isinstance(fromOperand,MemoryOperand) and isinstance(toOperand,MemoryOperand):
					memory = fromOperand
					fromOperand = RegisterOperand(Registers32.EAX)
					clusteredArrayBefore += [self.evictVariable()]
					clusteredArrayBefore += [MemoryOperand(memory),RegisterOperand(Registers32.EAX)]
			
					clusteredArrayAfter += [self.unevictVariable()]
			
				clusteredInstructionBefore = ClusteredInstruction(clusteredArrayBefore)
				clusteredInstructionAfter = ClusteredInstruction(clusteredArrayAfter)
			
				moveInstruction = MoveInstruction(fromOperand,toOperand)
			
				moveCluster = ClusteredInstruction([clusteredArrayBefore,moveInstruction,clusteredArrayAfter])
				return moveCluster
				
			elif isinstance(ast.expr,BinaryInstruction): return ast.expr
								
			elif isinstance(ast.expr,UnaryInstruction): return ast.expr					
								
			elif isinstance(ast.expr,ClusteredInstruction):
				assign = ast.nodes[0]
				clusteredArray = []
				for i in ast.expr.nodes:
					if isinstance(i,AssemblyFunction):
						clusteredArray += [i]
						clusteredArray += [MoveInstruction(RegisterOperand(Registers32.EAX),assign)]
					elif isinstance(i,MoveInstruction) and i.toOperand == assign: clusteredArray += []
					else: clusteredArray += [i]
				return ClusteredInstruction(clusteredArray)
			
			else: raise Exception("Error: Unrecognized node type")
			
		elif isinstance(ast,Compare):
			leftcmp = ast.expr
			rightcmp = ast.ops[1]
			reg = RegisterOperand(Registers32.EAX)
			if isinstance(leftcmp,MemoryOperand) and isinstance(rightcmp,MemoryOperand):
				evictInstr = self.evictVariable()
				moveright = MoveInstruction(rightcmp,reg)
				compareInstr = CompareInstruction(leftcmp,reg)
				savecmp = MoveInstruction(reg,rightcmp)
				unevictInstr = self.unevictVariable()
				return ClusteredInstruction([evictInstr,moveright,compareInstr,savecmp,unevictInstr])
			return CompareInstruction(leftcmp,rightcmp)
		
		elif isinstance(ast,UnarySub): return NegativeInstruction(ast.expr)
			
		elif isinstance(ast,IfExp):
			test = self.getVariableLocation(ast.test)
			compareInstr = CompareInstruction(ConstantOperand(DecimalValue(1)),test)
			jumpInstr = JumpInstruction(test,SIGNEDGREATER)
			#how are we jumping TO a location?
			return ClusteredInstruction([compareInstr,jumpInstr])
			
		elif isinstance(ast,Add):
			leftAdd = ast.left
			rightAdd = ast.right

			if isinstance(leftAdd,MemoryOperand) and isinstance(rightAdd,MemoryOperand):
				reg = RegisterOperand(Registers32.EAX)
				evictInstr = self.evictVariable()
				moveRightAddIntoEAX = MoveInstruction(rightAdd,reg)
				add = AddInstruction(reg,leftAdd)
				unevictInstr = self.unevictVariable()

				return ClusteredInstruction([evictInstr,moveRightAddIntoEAX,add,unevictInstr])
			else: return AddInstruction(rightAdd,leftAdd)
		
		else: return ast
