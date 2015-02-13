from compiler.ast import *
from AssemblyAST import *
from LivenessAnalysis import*

class Translator:

	@staticmethod
	def pythonASTToAssemblyAST(ast):
		colors = ["eax","ebx","ecx","edx","edi","esi"]
		memory = {}
		la = LivenessAnalysis.livenessAnalysis(ast)
		print la
		graph = LivenessAnalysis.createGraph(la)
		# print graph
		coloredgraph = LivenessAnalysis.colorGraph(graph)
		# print coloredgraph

		def getVariableInMemory(name): #update this
			# if name in coloredgraph:
			# 	if coloredgraph[name] not in colors:
			# 		return MemoryOperand(RegisterOperand("ebp"),coloredgraph[name])
			# 	else:
			# 		return RegisterOperand(coloredgraph[name])
			if name not in memory: memory[name] = -4*(len(memory)+1)
			return MemoryOperand(RegisterOperand("ebp"),memory[name])
			
		def translatePythonAST(ast,liveness=None):
			spill_vars = 0
			if isinstance(ast,Module): return AssemblyProgram([translatePythonAST(ast.node,liveness)])
			
			elif isinstance(ast,Stmt):
				if isinstance(liveness,list): x86 = [translatePythonAST(ast.nodes[i],liveness[i:i+2]) for i in range(len(ast.nodes)-1)]
				else: x86 = [translatePythonAST(n) for n in ast.nodes]
				return AssemblyFunction("main",x86,4*(len(memory)+1))
				
			elif isinstance(ast,Discard): return translatePythonAST(ast.expr,liveness)
			
			elif isinstance(ast,Const): return ConstantOperand(ast.value)
			
			elif isinstance(ast,Assign):

				assignInstruction = translatePythonAST(ast.nodes[0],liveness)
				x86AST = translatePythonAST(ast.expr,liveness)
				if isinstance(x86AST,Operand):
					if ast.nodes[0].name in coloredgraph and coloredgraph[ast.nodes[0].name] != "SPILL": 
						x86AST = MoveInstruction(x86AST,RegisterOperand(coloredgraph[ast.nodes[0].name]),"l")
					else: 
						x86AST = MoveInstruction(x86AST,getVariableInMemory(ast.nodes[0].name),"l")

				return x86AST
				# return ClusteredInstructions([x86AST] + [MoveInstruction(RegisterOperand("eax"),assignInstruction,"l")])


			
			elif isinstance(ast,AssName):				
				
				#need to change this, assign to registers
				
				if ast.name in coloredgraph:
					register = coloredgraph[ast.name]
					return RegisterOperand(register)
				else: return getVariableInMemory(ast.name)
				
			elif isinstance(ast,Name):
				if ast.name in coloredgraph and coloredgraph[ast.name] != "SPILL": 
					return RegisterOperand(coloredgraph[ast.name])
				else: return getVariableInMemory(ast.name)
			
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
				instruction = translatePythonAST(ast.expr,liveness)
				# instruction = [MoveInstruction(instruction,RegisterOperand("eax"),"l")]
				return ClusteredInstructions(instruction + [NegativeInstruction(RegisterOperand("eax"),"l")])
			
			elif isinstance(ast,Add):
				leftAST = translatePythonAST(ast.left,liveness)
				rightAST = translatePythonAST(ast.right,liveness)
				leftAST = [MoveInstruction(leftAST,RegisterOperand("eax"),"l")]
				rightAST = [AddInstruction(rightAST,RegisterOperand("eax"),"l")]
				return ClusteredInstructions(leftAST + rightAST)
			
			raise "Error: " + str(ast) + " currently not supported.\n"
			
		t = translatePythonAST(ast,la)
		return t
