from compiler.ast import *
from AssemblyAST import *
from LivenessAnalysis import*

#EAX,ECX,EDX
#EBX,EDI,ESI

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
			else:
				new_name = getVariableInMemory(name)
			return new_name

		def getRegister(name):
			return RegisterOperand(coloredgraph[name])

		def getVariableInMemory(name): 
			if name not in memory: memory[name] = -4*(len(memory)+1)
			return MemoryOperand(RegisterOperand("ebp"),memory[name])
		
		def assignFunction(ast,liveness):
			print liveness
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
			
			else:
				raise "Error: " + str(ast) + " currently not supported.\n"
				
		def unaryFunction(name,ast,liveness):						
			value = translatePythonAST(ast.expr,liveness)
			mov_instruction = MoveInstruction(value,getName(name),"l")
			neg_instruction = NegativeInstruction(getName(name),"l")
			return ClusteredInstructions([mov_instruction] + [neg_instruction])
			 
		def addFunction(name,ast,liveness):
			vals = translatePythonAST(ast,liveness)
			leftval = vals[0]
			rightval = vals[1]
			mov_instruction = MoveInstruction(leftval,getName(name),"l")
			add_instruction = AddInstruction(rightval,getName(name),"l")
			return ClusteredInstructions([mov_instruction] + [add_instruction])
					
		def nameFunction(name,ast,liveness):
			val = translatePythonAST(ast,liveness)
			mov_instruction = MoveInstruction(val,getName(name),"l")
			return ClusteredInstructions([mov_instruction])
			
		def constFunction(name,ast,liveness):
			val = translatePythonAST(ast,liveness)
			mov_instruction = MoveInstruction(val,getName(name),"l")
			return ClusteredInstructions([mov_instruction])
			
		def callfuncFunction(name,ast,liveness):
			#eax,ecx,edx are caller save registers
			registers = []
			
			#liveness analysis is a LIST of SETS
			for x in liveness:
				if isinstance(getName(x), RegisterOperand):
					registers += [x]
					
			
			#move contents of registers into memory locations
			save = [MoveInstruction(getRegister(x),getVariableInMemory(x),"l") for x in registers]
			
			#move the contents of eax after functioncall into memory location or register
			call = CallInstruction(FunctionCallOperand(ast.node.name))
			mov_instruction = MoveInstruction(RegisterOperand("eax"),getName(name),"l")
			
			#move the contents of our memory locations back into the registers
			
			load = [MoveInstruction(getVariableInMemory(x),getRegister(x),"l") for x in registers]
			 
			return ClusteredInstructions(save + [call, mov_instruction] + load)
		
		#def printFunction(name,ast,liveness):
				
		def translatePythonAST(ast,liveness=None):
			spill_vars = 0
			if isinstance(ast,Module): return AssemblyProgram([translatePythonAST(ast.node,liveness)])
			
			elif isinstance(ast,Stmt):
				x86 = [translatePythonAST(ast.nodes[i],liveness[i+1]) for i in range(0,len(ast.nodes))]
				#else: x86 = [translatePythonAST(n) for n in ast.nodes]
				return AssemblyFunction("main",x86,4*(len(memory)+1))
				
			elif isinstance(ast,Discard): return translatePythonAST(ast.expr,liveness)
			
			elif isinstance(ast,Const): return ConstantOperand(ast.value)
			
			elif isinstance(ast,Assign):

				assignInstruction = translatePythonAST(ast.nodes[0],liveness)
				x86AST = translatePythonAST(ast.expr,liveness)
				
				return assignFunction(ast,liveness)
							
			elif isinstance(ast,AssName):				
								
				return getName(ast)
				
			elif isinstance(ast,Name):

				return getName(ast.name)
			
			elif isinstance(ast,CallFunc):
				call = CallInstruction(FunctionCallOperand(ast.node.name))
				if isinstance(liveness,list):
					saveToDisk = [MoveInstruction(coloredgraph[x],getVariableInMemory(x),"l") for x in liveness[0]]
					saveToRegister = [MoveInstruction(getVariableInMemory(x),coloredgraph[x],"l") for x in liveness[1]]
					return ClusteredInstructions(saveToDisk + [call] + saveToRegister)
				else: return call
			
			elif isinstance(ast,Printnl):
				operand = getVariableInMemory(ast.nodes[0].name)
				if ast.nodes[0].name in coloredgraph: operand = RegisterOperand(coloredgraph[ast.nodes[0].name])
				i = [PushInstruction(operand,"l")]
				i += [CallInstruction(FunctionCallOperand("print_int_nl"))]
				i += [AddInstruction(ConstantOperand(4),RegisterOperand("esp"),"l")]
				return ClusteredInstructions(i)
			
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
		
		print ast
		t = translatePythonAST(ast,la)
		return t
