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
		print("Colored graph")
		print(coloredgraph)
		print("\n")

		def getVariableInMemory(name): #update this
			if name in coloredgraph:
				if coloredgraph[name] not in colors:
					return MemoryOperand(RegisterOperand("ebp"),coloredgraph[name])
				else:
					return RegisterOperand(coloredgraph[name])
			#return MemoryOperand(RegisterOperand("ebp"),memory[name])
			
		def translatePythonAST(ast,liveness=None):
			spill_vars = 0
			if isinstance(ast,Module): return AssemblyProgram([translatePythonAST(ast.node)])
			
			elif isinstance(ast,Stmt):
				x86 = []
				for n in ast.nodes:
					x86 += translatePythonAST(n)
				return AssemblyFunction("main",x86,4*(len(memory)+1))
				
			elif isinstance(ast,Discard): return translatePythonAST(ast.expr)
			
			elif isinstance(ast,Const): return ConstantOperand(ast.value)
			
			elif isinstance(ast,Assign):
				assignInstruction = translatePythonAST(ast.nodes[0])
				x86AST = translatePythonAST(ast.expr)
				if len(x86AST) == 1:
					if isinstance(x86AST[0],Operand):
						x86AST = [MoveInstruction(x86AST[0],assignInstruction,"l")]
					return x86AST[0]
				return x86AST[0]
			
			elif isinstance(ast,AssName):				
				
				#need to change this, assign to registers
				if ast.name in coloredgraph:
					register = coloredgraph[ast.name]

				return RegisterOperand(register)
				
			elif isinstance(ast,Name): return getVariableInMemory(ast.name)
			
			elif isinstance(ast,CallFunc): return CallInstruction(FunctionCallOperand(ast.node.name))
			
			elif isinstance(ast,Printnl):
				i = [PushInstruction(getVariableInMemory(ast.nodes[0].name),"l")]
				i += [CallInstruction(FunctionCallOperand("print_int_nl"))]
				i += [AddInstruction(ConstantOperand(4),RegisterOperand("esp"),"l")]
				return ClusteredInstructions(i)
			
			elif isinstance(ast,UnarySub):
				instruction = translatePythonAST(ast.expr)
				instruction = [MoveInstruction(instruction,RegisterOperand("eax"),"l")]
				return ClusteredInstructions(instruction + [NegativeInstruction(RegisterOperand("eax"),"l")])
			
			elif isinstance(ast,Add):
				leftAST = translatePythonAST(ast.left)
				rightAST = translatePythonAST(ast.right)
				leftAST = [MoveInstruction(leftAST,RegisterOperand("eax"),"l")]
				rightAST = [AddInstruction(rightAST,RegisterOperand("eax"),"l")]
				return ClusteredInstructions(leftAST + rightAST)
			
			raise "Error: " + str(ast) + " currently not supported.\n"
			
		t = translatePythonAST(ast)
		return t
