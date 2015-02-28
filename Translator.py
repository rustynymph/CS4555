from compiler.ast import *
from AssemblyAST import *
from LivenessAnalysis import*

class Translator:

	@staticmethod
	def pythonASTToAssemblyAST(ast):
		colors = ["eax","ebx","ecx","edx","edi","esi"]
		memory = {}
		environment = ast[1]
		ast = ast[0]
		la = LivenessAnalysis.livenessAnalysis(ast,environment)
		graph = LivenessAnalysis.createGraph(la)
		coloredgraph = LivenessAnalysis.colorGraph(graph)

		def getName(name):
			if name in coloredgraph and coloredgraph[name] != "SPILL":
				new_name = getRegister(name)
			elif name in coloredgraph and coloredgraph[name] == "SPILL":
				new_name = getVariableInMemory(name)
			else:
				new_name = getVariableInMemory(name)
			return new_name

		def getRegister(name):
			return RegisterOperand(coloredgraph[name])

		def getVariableInMemory(name): 
			if name not in memory: memory[name] = -4*(len(memory)+1)
			return MemoryOperand(RegisterOperand("ebp"),memory[name])
		
		def saveNameAdd(name,leftval,rightval,reg,save_name):
			coloredgraph[name] = "SPILL"
			save_instruction = MoveInstruction(reg,getVariableInMemory(save_name),"l")
			mem_mov = MoveInstruction(leftval,reg,"l")
			add_instruction = AddIntegerInstruction(rightval,reg,"l")
			mem_mov2 = MoveInstruction(reg,getVariableInMemory(name),"l")
			load_instruction = MoveInstruction(getVariableInMemory(save_name),reg,"l")
			return ClusteredInstructions([save_instruction,mem_mov,add_instruction,mem_mov2,load_instruction])
		
		def checkName(register,liveindex,liveness):
			for x in liveness[liveindex]:
				for x in coloredgraph:
					if coloredgraph[x] == register:
						save_name = x
						return save_name
		
		def spillName(name,val,liveness):

			save_name = checkName("ebx",0,liveness)
								 
			save_instruction = MoveInstruction(RegisterOperand("ebx"),getVariableInMemory(save_name),"l")
			mem_mov1 = MoveInstruction(val,RegisterOperand("ebx"),"l")
			mem_mov2 = MoveInstruction(RegisterOperand("ebx"),getName(name),"l")
			load_instruction = MoveInstruction(getVariableInMemory(save_name),RegisterOperand("ebx"),"l")
			return ClusteredInstructions([save_instruction,mem_mov1,mem_mov2,load_instruction])
		
		def spillUnary(name,val,liveness):

			save_name = checkName("ebx",0,liveness)
			
			save_instruction = MoveInstruction(RegisterOperand("ebx"),getVariableInMemory(save_name),"l")
			mem_mov1 = MoveInstruction(val,RegisterOperand("ebx"),"l")
			neg_instruction = NegativeInstruction(RegisterOperand("ebx"),"l")
			mem_mov2 = MoveInstruction(RegisterOperand("ebx"),getName(name),"l")
			load_instruction = MoveInstruction(getVariableInMemory(save_name),RegisterOperand("ebx"),"l")
			return ClusteredInstructions([save_instruction,mem_mov1,neg_instruction,mem_mov2,load_instruction])
		
		def spillAdd(name,val,liveness):
			leftval = val[0]
			rightval = val[1]
			
			save_name = checkName("ebx",0,liveness)
									
			save_instruction = MoveInstruction(RegisterOperand("ebx"),getVariableInMemory(save_name),"l")
			mem_mov = MoveInstruction(leftval,RegisterOperand("ebx"),"l")
			add_instruction = AddIntegerInstruction(rightval,RegisterOperand("ebx"),"l")
			mem_mov2 = MoveInstruction(RegisterOperand("ebx"),getVariableInMemory(name),"l")
			load_instruction = MoveInstruction(getVariableInMemory(save_name),RegisterOperand("ebx"),"l")
			return ClusteredInstructions([save_instruction,mem_mov,add_instruction,mem_mov2,load_instruction])
			
		def assignFunction(ast,liveness):
			name = ast.nodes[0].name
			read = ast.expr
			if isinstance(read,UnarySub):
				return unaryFunction(name,read,liveness)
			elif isinstance(read,Add):
				return addFunction(name,read,liveness)
			elif isinstance(read,Name):
				return nameFunction(name,read,liveness)
			elif isinstance(read,Const):
				return constFunction(name,read,liveness)
			elif isinstance(read,CallFunc):
				return callfuncFunction(name,read,liveness)
			elif isinstance(read,List):
				return listFunction(name,read,liveness)
			elif isinstance(read,Dict):
				return dictFunction(name,read,liveness)
			elif isinstance(read,Not):
				return notFunction(name,read,liveness)
			elif isinstance(read,Compare):
				return compareFunction(name,read,liveness)
			elif isinstance(read,Or):
				return orFunction(name,read,liveness)
			elif isinstance(read,And):
				return andFunction(name,read,liveness)
			elif isinstance(read,IfExp):
				return ifExpFunction(name,read,liveness)
			elif isinstance(read,Subscript):
				return subscriptFunction(name,read,liveness)
			else:
				raise "Error: " + str(ast) + " currently not supported.\n"
		
		def notFunction(name,ast,liveness):
			print("wow")
		
		def compareFunction(name,ast,liveness):
			print("p1")
			
		def orFunction(name,ast,liveness):
			print("has")
			
		def andFunction(name,ast,liveness):
			print("a")
		
		def ifExpFunction(name,ast,liveness):
			print("lotta")
			
		def subscriptFunction(name,ast,liveness):
			print("sheeeet")
			
		def listFunction(name,ast,liveness):
			registers = []
			
			for x in liveness[1]:
				if isinstance(getName(x), RegisterOperand):
					registers += [x]
					
			save = [MoveInstruction(getRegister(x),getVariableInMemory(x),"l") for x in registers]

			
			eax = RegisterOperand("eax")

			#Creates the initial list
			createList = ClusteredInstructions([PushInstruction(ConstantOperand(len(ast.nodes))),CallInstruction(FunctionCallOperand("create_list")),AddIntegerInstruction(ConstantOperand(4),RegisterOperand("esp"))])
			#Moves pyobj into memory 
			nameInMemory = getVariableInMemory(name)
			movPyobjIntoMemory = MoveInstruction(eax,nameInMemory,"l")
			#Pushes pyobj onto the stack
			pushPyobj = PushInstruction(eax)
			#Pushes sentinal values onto the stack
			pushKey = PushInstruction(ConstantOperand(0))
			pushValue = PushInstruction(ConstantOperand(0))

			x86Values = []
			for i in range(len(ast.nodes)):
				#Removes old key and value from stack
				deallocateKVPair = AddIntegerInstruction(ConstantOperand(8),RegisterOperand("esp"))
				#Pushes new key and value onto the stack
				pushSubKey = PushInstruction(getName(ConstantOperand(i)))
				pushSubValue = PushInstruction(getName(ast.nodes[i]))
				#Adds subscription with parameters
				addSubIndex = CallInstruction(FunctionCallOperand("set_subscript"))
				#Adds index value to assembly
				x86Values += [deallocateKVPair,pushSubKey,pushSubValue,addSubIndex]

			#If the default location for the given name is a register move the value into the register
			nameInRegister = ClusteredInstructions()
			if isinstance(getName(name),RegisterOperand): nameInRegister = MoveInstruction(nameInMemory,getName(name))

			#Remove memory allocated for function calls
			deallocateFunctionCall = AddIntegerInstruction(ConstantOperand(12),RegisterOperand("esp"))

			#Assembly array for dictionary allocation
			listAllocation = [createList,movPyobjIntoMemory,pushPyobj,pushKey,pushValue] + x86Values + [nameInRegister,deallocateFunctionCall]
			
			if name in registers:
				registers.remove(name)
			
			load = [MoveInstruction(getVariableInMemory(x),getRegister(x),"l") for x in registers]
			 
			return ClusteredInstructions(save + dictionaryAllocation + load)
			
		def dictFunction(name,ast,liveness):
			registers = []
			
			for x in liveness[1]:
				if isinstance(getName(x), RegisterOperand):
					registers += [x]
					
			save = [MoveInstruction(getRegister(x),getVariableInMemory(x),"l") for x in registers]

			
			eax = RegisterOperand("eax")

			#Creates the initial dictionary
			createDictionary = CallInstruction(FunctionCallOperand("create_dict"))
			#Moves pyobj into memory 
			nameInMemory = getVariableInMemory(name)
			movPyobjIntoMemory = MoveInstruction(eax,nameInMemory,"l")
			#Pushes pyobj onto the stack
			pushPyobj = PushInstruction(eax)
			#Pushes sentinal values onto the stack
			pushKey = PushInstruction(ConstantOperand(0))
			pushValue = PushInstruction(ConstantOperand(0))

			x86Values = []
			for subscription in self.items:
				#Removes old key and value from stack
				deallocateKVPair = AddIntegerInstruction(ConstantOperand(8),RegisterOperand("esp"))
				#Pushes new key and value onto the stack
				pushSubKey = PushInstruction(getName(subscription[0]))
				pushSubValue = PushInstruction(getName(subscription[1]))
				#Adds subscription with parameters
				addSubIndex = CallInstruction(FunctionCallOperand("set_subscript"))
				#Adds new subscription to assembly
				x86Values += [deallocateKVPair,pushSubKey,pushSubValue,addSubIndex]

			#If the default location for the given name is a register move the value into the register
			nameInRegister = ClusteredInstructions()
			if isinstance(getName(name),RegisterOperand): nameInRegister = MoveInstruction(nameInMemory,getName(name))

			#Remove memory allocated for function calls
			deallocateFunctionCall = AddIntegerInstruction(ConstantOperand(12),RegisterOperand("esp"))

			#Assembly array for dictionary allocation
			dictionaryAllocation = [createDictionary,movPyobjIntoMemory,pushPyobj,pushKey,pushValue] + x86Values + [nameInRegister,deallocateFunctionCall]
			
			if name in registers:
				registers.remove(name)
			
			load = [MoveInstruction(getVariableInMemory(x),getRegister(x),"l") for x in registers]
			 
			return ClusteredInstructions(save + dictionaryAllocation + load)
				
		def unaryFunction(name,ast,liveness):
			val = translatePythonAST(ast.expr,liveness)
			if isinstance(val,MemoryOperand) and isinstance(getName(name),MemoryOperand): return spillUnary(name,val,liveness)
			mov_instruction = MoveInstruction(val,getName(name),"l")
			neg_instruction = NegativeInstruction(getName(name),"l")
			return ClusteredInstructions([mov_instruction] + [neg_instruction])
			 
		def addFunction(name,ast,liveness):

			vals = translatePythonAST(ast,liveness)
						
			if isinstance(getName(name),MemoryOperand): return spillAdd(name,vals,liveness)

			leftval = vals[0]
			rightval = vals[1]
							
			remove_registers = [coloredgraph[x] for x in liveness[0]]

			avail_registers = ["eax","ebx","ecx","edx","esi","edi"]
			for element in remove_registers:
				if element in avail_registers:
					avail_registers.remove(element)
						
			new_name = coloredgraph[name]
			
			if new_name not in avail_registers:
				if isinstance(rightval,RegisterOperand) and not(isinstance(leftval,RegisterOperand)):
					if rightval.name == "ebx":
						reg = RegisterOperand("edi")
						for x in liveness[1]:
							for x in coloredgraph:
								if coloredgraph[x] == "edi":
									save_name = x
									return saveNameAdd(name,leftval,rightval,reg,save_name)
					else:
						reg = RegisterOperand("ebx")
						for x in liveness[1]:
							for x in coloredgraph:							
								if coloredgraph[x] == "ebx":
									save_name = x
									return saveNameAdd(name,leftval,rightval,reg,save_name)
				elif isinstance(leftval,RegisterOperand) and not(isinstance(rightval,RegisterOperand)):
					if leftval.name == "ebx":
						reg = RegisterOperand("edi")
						for x in liveness[1]:
							for x in coloredgraph:							
								if coloredgraph[x] == "edi":
									save_name = x
									return saveNameAdd(name,leftval,rightval,reg,save_name)
					else:
						reg = RegisterOperand("ebx")
						for x in liveness[1]:
							for x in coloredgraph:							
								if coloredgraph[x] == "ebx":
									save_name = x
									return saveNameAdd(name,leftval,rightval,reg,save_name)
									
				elif isinstance(leftval,RegisterOperand) and isinstance(rightval,RegisterOperand):
					callers = ["ebx","edi","esi"]
					color1 = leftval.name
					color2 = rightval.name
					if color1 in callers:
						callers.remove(color1)
					if color2 in callers:
						callers.remove(color2)
					new_color = callers[0]
					reg = RegisterOperand(new_color)
					for x in liveness[1]:
						for x in coloredgraph:	
							if coloredgraph[x] == new_color:
								save_name = x
								return saveNameAdd(name,leftval,rightval,reg,save_name)
				else: return spillAdd(name,vals,liveness)
						
				coloredgraph[name] = "SPILL"
				mem_mov = MoveInstruction(leftval,reg,"l")
				add_instruction = AddIntegerInstruction(rightval,reg,"l")
				mem_mov2 = MoveInstruction(reg,getVariableInMemory(name),"l")
				return ClusteredInstructions([mem_mov,add_instruction,mem_mov2])
							
			mov_instruction = MoveInstruction(leftval,RegisterOperand(new_name),"l")
			add_instruction = AddIntegerInstruction(rightval,RegisterOperand(new_name),"l")
			mov2_instruction = MoveInstruction(RegisterOperand(new_name),getName(name),"l")
			return ClusteredInstructions([mov_instruction,add_instruction,mov2_instruction])
	
					
		def nameFunction(name,ast,liveness):
			val = translatePythonAST(ast,liveness)
			if isinstance(val,MemoryOperand) and isinstance(getName(name),MemoryOperand): return spillName(name,val,liveness)			
			mov_instruction = MoveInstruction(val,getName(name),"l")
			return ClusteredInstructions([mov_instruction])
			
		def constFunction(name,ast,liveness):
			val = translatePythonAST(ast,liveness)
			mov_instruction = MoveInstruction(val,getName(name),"l")
			return ClusteredInstructions([mov_instruction])
			
		def callfuncFunction(name,ast,liveness):
			registers = []
			
			for x in liveness[1]:
				if isinstance(getName(x), RegisterOperand):
					registers += [x]
					
			save = [MoveInstruction(getRegister(x),getVariableInMemory(x),"l") for x in registers]

			createDictionary = CallInstruction(FunctionCallOperand(ast.node.name))
			mov_instruction = MoveInstruction(RegisterOperand("eax"),getName(name),"l")
			
			if name in registers:
				registers.remove(name)
			
			load = [MoveInstruction(getVariableInMemory(x),getRegister(x),"l") for x in registers]
			 
			return ClusteredInstructions(save + [createDictionary, mov_instruction] + load)
		
		def printFunction(ast,liveness):
			registers = []
			
			for x in liveness[1]:
				if isinstance(getName(x), RegisterOperand):
					registers += [x]
					
			save = [MoveInstruction(getRegister(x),getVariableInMemory(x),"l") for x in registers]
			
			operand = getName(ast.nodes[0].name)
			
			instruction = [PushInstruction(operand,"l")]
			instruction += [CallInstruction(FunctionCallOperand("print_int_nl"))]
			instruction += [AddIntegerInstruction(ConstantOperand(4),RegisterOperand("esp"),"l")]
				
			if name in registers:
				registers.remove(name)
			
			load = [MoveInstruction(getVariableInMemory(x),getRegister(x),"l") for x in registers]
			 
			return ClusteredInstructions(save + instruction + load)


		def removeTrivialMoves(assemblyInstructions):

			for i in assemblyInstructions:
				if isinstance(i,ClusteredInstructions):
					for j in i.nodes:
						if isinstance(j,MoveInstruction):
							toOp = j.toOperand
							fromOp = j.fromOperand
							if str(toOp) == str(fromOp):
								i.nodes.remove(j)

			return assemblyInstructions
					
				
		def translatePythonAST(ast,liveness=None):
			spill_vars = 0
			if isinstance(ast,Module): return AssemblyProgram([translatePythonAST(ast.node,liveness)])
			
			elif isinstance(ast,Stmt):
				
				x86 = []
				for i in range(0,len(ast.nodes)):
					x86.append(translatePythonAST(ast.nodes[i],liveness[i:i+2]))
				
				x86 = removeTrivialMoves(x86)
				return AssemblyFunction("main",x86,4*(len(memory)+1))
				
			elif isinstance(ast,Discard): return translatePythonAST(ast.expr,liveness)
			
			elif isinstance(ast,Const): return ConstantOperand(ast.value)
			
			elif isinstance(ast,Assign): return assignFunction(ast,liveness)
							
			elif isinstance(ast,AssName): return getName(ast)
				
			elif isinstance(ast,Name): return getName(ast.name)
			
			elif isinstance(ast,Printnl): return printFunction(ast,liveness)

			#elif isinstance(ast,And):
				
			#elif isinstance(ast,Or):
				
			#elif isinstance(ast,Compare):
			
			#elif isinstance(ast,IfExp):
				
			#elif isinstance(ast,Let):
				
			#elif isinstance(ast,GetTag):			
				#mov_instruction = 
				#and_instruction = And(getName(ast.arg),ConstantOperand(3),"")
				
			#elif isinstance(ast,IsTag):
				
			
			elif isinstance(ast,UnarySub):
				neg_name = translatePythonAST(ast.expr,liveness)
				if isinstance(neg_name,Operand):
					x86AST = neg_name
				return x86AST
			
			elif isinstance(ast,Add):
				leftAST = translatePythonAST(ast.left,liveness)
				rightAST = translatePythonAST(ast.right,liveness)
				x86AST = [leftAST,rightAST]
				return x86AST
			
			raise "Error: " + str(ast) + " currently not supported.\n"
		t = translatePythonAST(ast,la)
		return t
