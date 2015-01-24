from compiler.ast import *
from AssemblyAST import *

class Translator:

	@staticmethod
	def pythonASTToAssemblyAST(ast):
		memory = {}
		def getVariableInMemory(name):
			return MemoryOperand(RegisterOperand("ebp"),memory[name])
		def translatePythonAST(ast):
			if isinstance(ast,Module): return AssemblyProgram([translatePythonAST(ast.node)])
			elif isinstance(ast,Stmt):
				x86 = []
				for n in ast.nodes:
					x86 += translatePythonAST(n)
				return AssemblyFunction("main",x86,4*(len(memory)+1))
			elif isinstance(ast,Discard): return translatePythonAST(ast.expr)
			elif isinstance(ast,Const): return [ConstantOperand(ast.value)]
			elif isinstance(ast,Assign):
				assignInstruction = translatePythonAST(ast.nodes[0])[0]
				x86AST = translatePythonAST(ast.expr)
				if len(x86AST) == 1:
					if isinstance(x86AST[0],Operand):
						x86AST = [MoveInstruction(x86AST[0],RegisterOperand("eax"),"l")]
					return x86AST + [MoveInstruction(RegisterOperand("eax"),assignInstruction,"l")]
				return x86AST + [MoveInstruction(RegisterOperand("eax"),assignInstruction,"l")]
			elif isinstance(ast,AssName):
				if ast.name not in memory: memory[ast.name] = -4*(len(memory)+1)
				return [getVariableInMemory(ast.name)]
			elif isinstance(ast,Name): return [getVariableInMemory(ast.name)]
			elif isinstance(ast,CallFunc): return [CallInstruction(FunctionCallOperand(ast.node.name))]
			elif isinstance(ast,Printnl):
				i = [PushInstruction(getVariableInMemory(ast.nodes[0].name),"l")]
				i += [CallInstruction(FunctionCallOperand("print_int_nl"))]
				i += [AddInstruction(ConstantOperand(4),RegisterOperand("esp"),"l")]
				return i
			elif isinstance(ast,UnarySub):
				instruction = translatePythonAST(ast.expr)[0]
				instruction = [MoveInstruction(instruction,RegisterOperand("eax"),"l")]
				return instruction + [NegativeInstruction(RegisterOperand("eax"),"l")]
			elif isinstance(ast,Add):
				leftAST = translatePythonAST(ast.left)
				rightAST = translatePythonAST(ast.right)
				leftAST = [MoveInstruction(leftAST[0],RegisterOperand("eax"),"l")]
				rightAST = [AddInstruction(rightAST[0],RegisterOperand("eax"),"l")]
				return leftAST + rightAST

			raise "Error: " + str(ast) + " currently not supported.\n"
		t = translatePythonAST(ast)
		print memory
		return t