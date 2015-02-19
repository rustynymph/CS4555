from compiler.ast import *
from AssemblyAST import *
from LivenessAnalysis import*

class Translator:

	@staticmethod
	def pythonASTToAssemblyAST(ast):
		colors = ["eax","ebx","ecx","edx","edi","esi"]
		memory = {}
		la = LivenessAnalysis.livenessAnalysis(ast)
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
		
		def spillName(name,val,liveness,current_instruction):
			for x in liveness[0]:
				for x in coloredgraph:
					if coloredgraph[x] == "ebx":
						save_name = x
								 
			save_instruction = MoveInstruction(RegisterOperand("ebx"),getVariableInMemory(save_name),"l")
			mem_mov1 = MoveInstruction(val,RegisterOperand("ebx"),"l")
			mem_mov2 = MoveInstruction(RegisterOperand("ebx"),getName(name),"l")
			load_instruction = MoveInstruction(getVariableInMemory(save_name),RegisterOperand("ebx"),"l")
			return ClusteredInstructions([save_instruction,mem_mov1,mem_mov2,load_instruction])
		
		def spillUnary(name,val,liveness,current_instruction):
			for x in liveness[0]:
				for x in coloredgraph:
					if coloredgraph[x] == "ebx":
						save_name = x
			
			save_instruction = MoveInstruction(RegisterOperand("ebx"),getVariableInMemory(save_name),"l")
			mem_mov1 = MoveInstruction(val,RegisterOperand("ebx"),"l")
			neg_instruction = NegativeInstruction(RegisterOperand("ebx"),"l")
			mem_mov2 = MoveInstruction(RegisterOperand("ebx"),getName(name),"l")
			load_instruction = MoveInstruction(getVariableInMemory(save_name),RegisterOperand("ebx"),"l")
			return ClusteredInstructions([save_instruction,mem_mov1,neg_instruction,mem_mov2,load_instruction])
		
		def spillAdd(name,val,liveness,current_instruction):
			leftval = val[0]
			rightval = val[1]
			
			for x in liveness[0]:
				for x in coloredgraph:
					if coloredgraph[x] == "ebx":
						save_name = x
						
			save_instruction = MoveInstruction(RegisterOperand("ebx"),getVariableInMemory(save_name),"l")
			mem_mov = MoveInstruction(leftval,RegisterOperand("ebx"),"l")
			add_instruction = AddInstruction(rightval,RegisterOperand("ebx"),"l")
			mem_mov2 = MoveInstruction(RegisterOperand("ebx"),getVariableInMemory(name),"l")
			load_instruction = MoveInstruction(getVariableInMemory(save_name),RegisterOperand("ebx"),"l")
			return ClusteredInstructions([save_instruction,mem_mov,add_instruction,mem_mov2,load_instruction])
			
		def assignFunction(ast,liveness,current_instruction):
			name = ast.nodes[0].name
			read = ast.expr
			if isinstance(read,UnarySub):
				return unaryFunction(name,read,liveness,current_instruction)
			elif isinstance(read,Add):
				return addFunction(name,read,liveness,current_instruction)
			elif isinstance(read,Name):
				return nameFunction(name,read,liveness,current_instruction)
			elif isinstance(read,Const):
				return constFunction(name,read,liveness,current_instruction)
			elif isinstance(read,CallFunc):
				return callfuncFunction(name,read,liveness,current_instruction)
			
			else:
				raise "Error: " + str(ast) + " currently not supported.\n"
				
		def unaryFunction(name,ast,liveness,current_instruction):
			i = current_instruction						
			val = translatePythonAST(ast.expr,liveness,i)
			if isinstance(val,MemoryOperand) and isinstance(getName(name),MemoryOperand): return spillUnary(name,val,liveness,i)
			mov_instruction = MoveInstruction(val,getName(name),"l")
			neg_instruction = NegativeInstruction(getName(name),"l")
			return ClusteredInstructions([mov_instruction] + [neg_instruction])
			 
		def addFunction(name,ast,liveness,current_instruction):
			i = current_instruction
			vals = translatePythonAST(ast,liveness,i)
						
			if isinstance(getName(name),MemoryOperand): return spillAdd(name,vals,liveness,i)

			leftval = vals[0]
			rightval = vals[1]
							
			
			remove_registers = [coloredgraph[x] for x in liveness[0]]
			#+ [coloredgraph[x] for x in liveness[1]]

			avail_registers = ["eax","ebx","ecx","edx","esi","edi"]
			for element in remove_registers:
				if element in avail_registers:
					avail_registers.remove(element)
			
			if name not in liveness[1]:
				return ClusteredInstructions()
			
			new_name = coloredgraph[name]
			
			if new_name not in avail_registers:
				if len(avail_registers) > 1:
					new_name = avail_registers[0]
				else:
					#new_name = "ebx"
					for x in liveness[0]:
						for x in coloredgraph:
							if isinstance(rightval,RegisterOperand):
								if rightval.name == "ebx":
									reg = RegisterOperand("edi")
									if coloredgraph[x] == "edi":
										save_name = x
								else:
									reg = RegisterOperand("ebx")
									if coloredgraph[x] == "ebx":
										save_name = x
							else:
								reg = RegisterOperand("ebx")
								if coloredgraph[x] == "ebx":
									save_name = x
					coloredgraph[name] = "SPILL"
					save_instruction = MoveInstruction(reg,getVariableInMemory(save_name),"l")
					mem_mov = MoveInstruction(leftval,reg,"l")
					add_instruction = AddInstruction(rightval,reg,"l")
					mem_mov2 = MoveInstruction(reg,getVariableInMemory(name),"l")
					load_instruction = MoveInstruction(getVariableInMemory(save_name),reg,"l")
					return ClusteredInstructions([save_instruction,mem_mov,add_instruction,mem_mov2,load_instruction])
							
			mov_instruction = MoveInstruction(leftval,RegisterOperand(new_name),"l")
			add_instruction = AddInstruction(rightval,RegisterOperand(new_name),"l")
			mov2_instruction = MoveInstruction(RegisterOperand(new_name),getName(name),"l")
			return ClusteredInstructions([mov_instruction,add_instruction,mov2_instruction])			
					
		def nameFunction(name,ast,liveness,current_instruction):
			i = current_instruction
			val = translatePythonAST(ast,liveness,i)
			print("=======")
			print val
			print getName(name)
			print liveness
			for x in liveness[0]:
				print coloredgraph[x]
			for x in liveness[1]:
				print coloredgraph[x]
			print("=======")
			if isinstance(val,MemoryOperand) and isinstance(getName(name),MemoryOperand): return spillName(name,val,liveness,i)			
			mov_instruction = MoveInstruction(val,getName(name),"l")
			return ClusteredInstructions([mov_instruction])
			
		def constFunction(name,ast,liveness,current_instruction):
			i = current_instruction
			val = translatePythonAST(ast,liveness,i)
			mov_instruction = MoveInstruction(val,getName(name),"l")
			return ClusteredInstructions([mov_instruction])
			
		def callfuncFunction(name,ast,liveness,current_instruction):
			#eax,ecx,edx are caller save registers
			i = current_instruction
			registers = []
			
			#liveness analysis is a LIST of SETS
			for x in liveness[1]:
				if isinstance(getName(x), RegisterOperand):
					registers += [x]
					
			#move contents of registers into memory locations
			save = [MoveInstruction(getRegister(x),getVariableInMemory(x),"l") for x in registers]
			
			#move the contents of eax after functioncall into memory location or register
			call = CallInstruction(FunctionCallOperand(ast.node.name))
			mov_instruction = MoveInstruction(RegisterOperand("eax"),getName(name),"l")
			
			#move the contents of our memory locations back into the registers
			if name in registers:
				registers.remove(name)
			
			load = [MoveInstruction(getVariableInMemory(x),getRegister(x),"l") for x in registers]
			 
			return ClusteredInstructions(save + [call, mov_instruction] + load)
		
		def printFunction(ast,liveness,current_instruction):
			i = current_instruction
			registers = []
			
			for x in liveness[1]:
				if isinstance(getName(x), RegisterOperand):
					registers += [x]
					
			save = [MoveInstruction(getRegister(x),getVariableInMemory(x),"l") for x in registers]
			
			operand = getName(ast.nodes[0].name)
			
			instruction = [PushInstruction(operand,"l")]
			instruction += [CallInstruction(FunctionCallOperand("print_int_nl"))]
			instruction += [AddInstruction(ConstantOperand(4),RegisterOperand("esp"),"l")]
				
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
					
				
		def translatePythonAST(ast,liveness=None,current_instruction=0):
			spill_vars = 0
			if isinstance(ast,Module): return AssemblyProgram([translatePythonAST(ast.node,liveness,0)])
			
			elif isinstance(ast,Stmt):
				
				x86 = []
				for i in range(0,len(ast.nodes)):
					x86.append(translatePythonAST(ast.nodes[i],liveness[i:i+2],current_instruction=i))
				
				x86 = removeTrivialMoves(x86)
				return AssemblyFunction("main",x86,4*(len(memory)+1))
				
			elif isinstance(ast,Discard): return translatePythonAST(ast.expr,liveness,current_instruction)
			
			elif isinstance(ast,Const): return ConstantOperand(ast.value)
			
			elif isinstance(ast,Assign): return assignFunction(ast,liveness,current_instruction)
							
			elif isinstance(ast,AssName): return getName(ast)
				
			elif isinstance(ast,Name): return getName(ast.name)
			
			elif isinstance(ast,Printnl): return printFunction(ast,liveness,current_instruction)
			
			elif isinstance(ast,UnarySub):
				neg_name = translatePythonAST(ast.expr,liveness,current_instruction)
				if isinstance(neg_name,Operand):
					x86AST = neg_name
				return x86AST
			
			elif isinstance(ast,Add):
				leftAST = translatePythonAST(ast.left,liveness,current_instruction)
				rightAST = translatePythonAST(ast.right,liveness,current_instruction)
				x86AST = [leftAST,rightAST]
				return x86AST
			
			raise "Error: " + str(ast) + " currently not supported.\n"
		print coloredgraph
		t = translatePythonAST(ast,la,0)
		return t
