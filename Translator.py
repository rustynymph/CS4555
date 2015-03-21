from compiler.ast import *
from AssemblyAST import *
from PythonASTExtension import *

class NameGenerator():
	def __init__(self,prefix,count=0):
		self.prefix = prefix
		self.count = count
		
	def getName(self):
		return self.prefix + str(self.count)

	def getNameAndIncrementCounter(self):
		name = self.getName()
		self.count += 1
		return name

class Translator():
	def __init__(self,coloredgraph):
		self.branch = NameGenerator("branch")		
		self.coloredgraph = coloredgraph
		self.memory = {}
	
	def getInvertedGraph(self,coloredgraph):
		invertedgraph = {}
		for _,v in coloredgraph.items(): invertedgraph[v] = []

		for k,v in coloredgraph.items():
			if v:
				invertedgraph[v] += [k]
		return invertedgraph

	def getVariableLocation(self,variable):
		register = self.getRegister(variable)
		if register: return register
		else: return self.getVariableInMemory(variable)

	def getVariableInMemory(self,variable):
		if variable not in self.memory: self.putVariableInMemory(variable)
		return self.memory[variable]
	
	def getRegister(self,variable): 
		if variable in self.coloredgraph: return self.coloredgraph[variable]
		else: return None
	
	def putVariableInMemory(self,variable):
		if variable not in self.memory:
			self.memory[variable] = MemoryOperand(Registers32.EBP,-self.getActivationRecordSize())
	
	def getActivationRecordSize(self): return 4*(len(self.memory)+1)

	def evictVariable(self):
		reg = RegisterOperand(Registers32.EAX)
		if reg in self.getInvertedGraph(self.coloredgraph):
			evictedVariable = self.getInvertedGraph(self.coloredgraph)[reg][0]
			evictedVariableMemoryLocation = self.getVariableInMemory(evictedVariable)
			return (MoveInstruction(reg,evictedVariableMemoryLocation),True,evictedVariableMemoryLocation)
		return (ClusteredInstruction(),False,None)		
		
	def unevictVariable(self,evicted=True,loc=None):
		if evicted:	return MoveInstruction(loc,RegisterOperand(Registers32.EAX))
		else: return ClusteredInstruction()

	def translateToX86(self,ast):
		if isinstance(ast,Module):

			assFunction = AssemblyFunction(SectionHeaderInstruction("main"),ast.node,self.getActivationRecordSize(),ConstantOperand(DecimalValue(0)))
			clusteredAssFunction = ClusteredInstruction([assFunction])
			return AssemblyProgram(EntryPointInstruction(NameOperand("main")),clusteredAssFunction)
		
		elif isinstance(ast,Stmt): return ClusteredInstruction(ast.nodes)			
		
		elif isinstance(ast,Const):	return ConstantOperand(DecimalValue(ast.value))

		elif isinstance(ast,AssName):
			self.putVariableInMemory(ast.name)
			return self.getVariableLocation(ast.name)

		elif isinstance(ast,Name):
			if ast.name in self.memory:	return self.getVariableLocation(ast.name)
			else: return NameOperand(ast.name)

		elif isinstance(ast,CallFunc):
			callersavedvariables = []

			liveVariables = ast.liveness

			liveRegisters = []
			liveMemory = []

			for variable in liveVariables:
				variableLocation = self.getVariableLocation(variable)
				if isinstance(variableLocation.register,CallerSavedRegister): 
					liveMemory += [self.getVariableInMemory(variable)]
					liveRegisters += [variableLocation]

			if len(ast.args) > 0:
				pushArgsInstr = [PushInstruction(arg) for arg in reversed(ast.args)]
			else: pushArgsInstr = []		
					
			length = len(pushArgsInstr)*4
			addInstr = [AddIntegerInstruction(ConstantOperand(DecimalValue(length)),RegisterOperand(Registers32.ESP))]		
			saveInstr = [MoveInstruction(liveRegisters[i],liveMemory[i]) for i in range(len(liveRegisters))]
			callInstr = [CallInstruction(ast.node)]
			loadInstr = [MoveInstruction(liveMemory[i],liveRegisters[i]) for i in range(len(liveRegisters))]
			return ClusteredInstruction(saveInstr + pushArgsInstr + callInstr + addInstr + loadInstr)
					
		elif isinstance(ast,InjectFrom):

			location = ast.arg
			tag = ast.typ
			if ast.typ.value.value != 3:
				shiftLeftInstr = [ShiftLeftInstruction(ConstantOperand(DecimalValue(2)),location)]
				orInstr = [OrInstruction(tag,location)]
				return ClusteredInstruction(shiftLeftInstr + orInstr)
			else: return OrInstruction(tag,location)
			
		elif isinstance(ast,ProjectTo):
			location = ast.arg
			if ast.typ.value.value != 3:
				shiftRightInstr = [ShiftArithmeticRightInstruction(ConstantOperand(DecimalValue(2)),location)]
				return ClusteredInstruction(shiftRightInstr )
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
					evict = self.evictVariable()
					save = evict[0]
					boolean = evict[1]
					loc = evict[2]
					clusteredArrayBefore += [save]
					clusteredArrayBefore += [MoveInstruction(memory,RegisterOperand(Registers32.EAX))]
			
					clusteredArrayAfter += [self.unevictVariable(boolean,loc)]
			
				clusteredInstructionBefore = ClusteredInstruction(clusteredArrayBefore)
				clusteredInstructionAfter = ClusteredInstruction(clusteredArrayAfter)
			
				moveInstruction = [MoveInstruction(fromOperand,toOperand)]
			
				moveCluster = ClusteredInstruction(clusteredArrayBefore + moveInstruction + clusteredArrayAfter)
				return moveCluster
				
			elif isinstance(ast.expr,BinaryInstruction): return ast.expr
								
			elif isinstance(ast.expr,UnaryInstruction): return ast.expr					
								
			elif isinstance(ast.expr,ClusteredInstruction):
				assign = ast.nodes[0]
				clusteredArray = []
				for i in ast.expr.nodes:
					if isinstance(i,CallInstruction):
						clusteredArray += [i]
						clusteredArray += [MoveInstruction(RegisterOperand(Registers32.EAX),assign)]
					elif isinstance(i,MoveInstruction) and i.toOperand == assign: clusteredArray += []
					else: clusteredArray += [i]
				return ClusteredInstruction(clusteredArray)
			
			#elif isinstance(ast.expr,Subscript): print("hello")
			
			else: raise Exception("Error: Unrecognized node type")
			
		elif isinstance(ast,Compare):
			print ast
			leftcmp = ast.expr
			rightcmp = ast.ops[0][1]
			reg = RegisterOperand(Registers32.EAX)
			if isinstance(rightcmp,ConstantOperand) and isinstance(leftcmp,RegisterOperand): return CompareInstruction(rightcmp,leftcmp)
		
			elif (isinstance(leftcmp,MemoryOperand) and isinstance(rightcmp,MemoryOperand)) or (isinstance(leftcmp,MemoryOperand) and isinstance(rightcmp,ConstantOperand)) or (isinstance(leftcmp,ConstantOperand) and isinstance(rightcmp,MemoryOperand)) or (isinstance(leftcmp,ConstantOperand) and isinstance(rightcmp,ConstantOperand)):
				evict = self.evictVariable()
				save = evict[0]
				boolean = evict[1]
				loc = evict[2]
				evictInstr = [save]
				moveright = [MoveInstruction(rightcmp,reg)]
				compareInstr = [CompareInstruction(leftcmp,reg)]
				unevictInstr = [self.unevictVariable(boolean,loc)]
				return ClusteredInstruction(evictInstr + moveright + compareInstr + unevictInstr)
			return CompareInstruction(leftcmp,rightcmp)
		
		elif isinstance(ast,UnarySub): return NegativeInstruction(ast.expr)
		
		elif isinstance(ast,Not): return NotInstruction(ast.expr)
			
		elif isinstance(ast,IfExp):
			test = ast.test
			true = ast.then
			false = ast.else_
			save = []
			movcmp = []
			compare = []
			load = []
			
			if isinstance(test,MemoryOperand):
				evictStuff = self.evictVariable()
				save = [evictStuff[0]]
				boolean = evictStuff[1]
				loc = evictStuff[2]
				movcmp = [MoveInstruction(test,RegisterOperand(Registers32.EAX))]
				compare = CompareInstruction(ConstantOperand(DecimalValue(1)),RegisterOperand(Registers32.EAX))
				if isinstance(save,MoveInstruction): load = [self.unevictVariable(boolean,loc)]
				else: load = []
			
			elif isinstance(test,ClusteredInstruction):
				#I'm assuming if we have a clustered instruction here that it has length 4
				evict = [test.nodes[0]]
				mov = [test.nodes[1]]
				compare = test.nodes[2]
				unevict = [test.nodes[3]]
				name = self.branch.getNameAndIncrementCounter()
				trueSection = ClusteredInstruction(unevict + [ast.then])
				falseSection = ClusteredInstruction(unevict + [ast.else_])

				assIf = [AssemblyIf(compare,name,trueSection,falseSection)]
				return ClusteredInstruction(evict + mov + assIf)				
									
			
			elif isinstance(test,CompareInstruction): compare = test
				
			
			else:
				compare = CompareInstruction(ConstantOperand(DecimalValue(1)),test)
			
			name = self.branch.getNameAndIncrementCounter() 
			
			trueSection = ClusteredInstruction(load + [ast.then])
			falseSection = ClusteredInstruction(load + [ast.else_])

			assIf = [AssemblyIf(compare,name,trueSection,falseSection)]
			return ClusteredInstruction(save + movcmp + assIf + load)
			
		elif isinstance(ast,Add):
			leftAdd = ast.left
			rightAdd = ast.right

			if isinstance(leftAdd,MemoryOperand) and isinstance(rightAdd,MemoryOperand):
				reg = RegisterOperand(Registers32.EAX)
				evict = self.evictVariable()
				save = evict[0]
				boolean = evict[1]
				loc = evict[2]
				evictInstr = [save]
				moveRightAddIntoEAX = [MoveInstruction(rightAdd,reg)]
				add = [AddIntegerInstruction(reg,leftAdd)]
				unevictInstr = [self.unevictVariable(boolean,loc)]

				return ClusteredInstruction(evictInstr + moveRightAddIntoEAX + add + unevictInstr)
			else: return AddIntegerInstruction(rightAdd,leftAdd)
		
		elif isinstance(ast,Function):
			code = []
			if isinstance(ast.code,Stmt): code += [i for i in ast.code.nodes]
			else: code += [ast.code]
			assFunc = AssemblyFunction(SectionHeaderInstruction(ast.name),ClusteredInstruction(code),ConstantOperand(DecimalValue(len(ast.argnames))))
			return assFunc
		
		elif isinstance(ast,CreateClosure):
			name = self.getVariableLocation(ast.name)
			freeVariables = ast.fvs
			pushInstr1 = [PushInstruction(name)]
			pushInstr2 = [PushInstruction(ast.fvs)]
			callInstr = [CallInstruction(NameOperand('create_closure'))]
			return ClusteredInstruction(pushInstr1 + pushInstr2 + callInstr)
			
		elif isinstance(ast,GetClosure):
			#need a save instruction
			name = self.getVariableLocation(ast.name)
			pushInstr1 = [PushInstruction(name)]
			getFunPtr = [CallInstruction(NameOperand('get_fun_ptr'))]
			movInstr1 = [MoveInstruction(RegisterOperand(Registers32.EAX),RegisterOperand(Registers32.EBX))]
			pushInstr2 = [PushInstruction(name)]
			getFvs = [CallInstruction(NameOperand('get_free_vars'))]
			movInstr2 = [MoveInstruction(RegisterOperand(Registers32.EAX),RegisterOperand(Registers32.ECX))]
			indirectCall = [CallInstruction(DereferenceOperand(RegisterOperand(Registers32.ECX)))]
			return ClusteredInstruction(pushInstr1+getFunPtr+movInstr1+pushInstr2+getFvs+movInstr2+indirectCall)
			
		elif isinstance(ast,Return):
			val = ast.value
			movInstr = [MoveInstruction(val,RegisterOperand(Registers32.EAX))]
			retInstr = [ReturnInstruction()]
			return ClusteredInstruction(movInstr + retInstr)
		
		else: return ast
