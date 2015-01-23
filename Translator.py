from compiler.ast import *
from AssemblyAST import *

class Translator:

	@staticmethod
	def pythonASTToAssemblyAST(ast):
		memory = {}
		def translatePythonAST(ast):
			if isinstance(ast,Module): return AssemblyProgram([translatePythonAST(ast.node)])
			elif isinstance(ast,Stmt):
				x86 = []
				for n in ast.nodes:
					x86 += translatePythonAST(n)
				return AssemblyFunction("main",x86)
			elif isinstance(ast,Discard): return translatePythonAST(ast.expr)
			elif isinstance(ast,Const): return [ConstantOperand(ast.value)]
			elif isinstance(ast,Assign):
				offset = -4*(len(memory)+1)
				memory[ast.nodes[0].name] = offset
				assign = MoveInstruction(RegisterOperand("eax"),MemoryOperand(RegisterOperand("ebp"),offset),"l")
				subAST = translatePythonAST(ast.expr)
				if len(subAST) == 1: 
					print MoveInstruction(subAST[0],MemoryOperand(RegisterOperand("ebp"),offset),"l").printInstruction()
					if isinstance(subAST[0],MemoryOperand):
						instructions = []
						instructions += [MoveInstruction(subAST[0],RegisterOperand("eax"),"l")]
						instructions += [MoveInstruction(RegisterOperand("eax"),MemoryOperand(RegisterOperand("ebp"),offset),"l")]
						return instructions
					elif isinstance(subAST[0],CallInstruction): return subAST + [MoveInstruction(RegisterOperand("eax"),MemoryOperand(RegisterOperand("ebp"),offset),"l")]
					else: return [MoveInstruction(subAST[0],MemoryOperand(RegisterOperand("ebp"),offset),"l")]
				else: return translatePythonAST(ast.expr) + [assign]
			elif isinstance(ast,Name): return [MemoryOperand(RegisterOperand("ebp"),memory[ast.name])]
			elif isinstance(ast,CallFunc): return [CallInstruction(FunctionCallOperand(ast.node.name))]
			return "Error: " + str(ast) + " currently not supported.\n"
		return translatePythonAST(ast)