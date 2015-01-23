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
				subAST = translatePythonAST(ast.expr)
				assign = MoveInstruction(RegisterOperand("eax"),MemoryOperand(RegisterOperand("ebp"),offset),"l")
				if len(subAST) == 1: 
					# print MoveInstruction(subAST[0],MemoryOperand(RegisterOperand("ebp"),offset),"l").printInstruction()

					if isinstance(subAST[0],MemoryOperand):
						instructions = []
						instructions += [MoveInstruction(subAST[0],RegisterOperand("eax"),"l")]
						instructions += [MoveInstruction(RegisterOperand("eax"),MemoryOperand(RegisterOperand("ebp"),offset),"l")]
						return instructions
					elif isinstance(subAST[0],CallInstruction): return subAST + [MoveInstruction(RegisterOperand("eax"),MemoryOperand(RegisterOperand("ebp"),offset),"l")]
					elif isinstance(subAST[0],ConstantOperand): return [MoveInstruction(subAST[0],RegisterOperand("eax"),"l")]
					elif isinstance(subAST[0],NegativeInstruction): return subAST + [MoveInstruction(RegisterOperand("eax"),MemoryOperand(RegisterOperand("ebp"),offset),"l")]
					else: 
						
						return [MoveInstruction(subAST[0],MemoryOperand(RegisterOperand("ebp"),offset),"l")]
				else: return translatePythonAST(ast.expr) + [assign]
			elif isinstance(ast,Name): return [MemoryOperand(RegisterOperand("ebp"),memory[ast.name])]
			elif isinstance(ast,CallFunc): return [CallInstruction(FunctionCallOperand(ast.node.name))]
			elif isinstance(ast,Printnl):
				i = [PushInstruction(MemoryOperand(RegisterOperand("ebp"),memory[ast.nodes[0].name]),"l")]
				i += [CallInstruction(FunctionCallOperand("print_int_nl"))]
				i += [AddInstruction(ConstantOperand(4),RegisterOperand("esp"),"l")]
				return i
			elif isinstance(ast,UnarySub):
				if isinstance(ast.expr,Name):
					i = [MoveInstruction(MemoryOperand(RegisterOperand("ebp"),memory[ast.expr.name]),RegisterOperand("eax"),"l")]
					i = [NegativeInstruction(RegisterOperand("eax"),"l")]
					return i
				elif isinstance(ast.expr,Const):
					i = [MoveInstruction(ConstantOperand(ast.expr.value),RegisterOperand("eax"),"l")]
					i = [NegativeInstruction(RegisterOperand("eax"),"l")]
					return i
			elif isinstance(ast,Add):
				i = []
				if isinstance(ast.left,Name): i += [MoveInstruction(MemoryOperand(RegisterOperand("ebp"),memory[ast.left.name]),RegisterOperand("eax"),"l")]
				else: i += [MoveInstruction(ConstantOperand(ast.left.value),RegisterOperand("eax"),"l")]

				if isinstance(ast.right,Name): i += [AddInstruction(MemoryOperand(RegisterOperand("ebp"),memory[ast.right.name]),RegisterOperand("eax"),"l")]
				else: [AddInstruction(ConstantOperand(ast.right.value,RegisterOperand("eax"),"l"))]

				return i

			raise "Error: " + str(ast) + " currently not supported.\n"
		return translatePythonAST(ast)