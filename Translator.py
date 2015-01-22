from compiler.ast import *
from AssemblyAST import *

class Translator:

	@staticmethod
	def pythonASTToAssemblyAST(ast):
		memory = {}
		hasEntry = False
		def translatePythonAST(ast):
			if isinstance(ast,Module): return AssemblyProgram([Translator.pythonASTToAssemblyAST(ast.node)])
			elif isinstance(ast,Stmt): 
				if hasEntry:
					hasEntry = True
					return AssemblyFunction("main",[Translator.pythonASTToAssemblyAST(n) for n in ast.nodes])
				else: [Translator.pythonASTToAssemblyAST(n) for n in ast.nodes]
			elif isinstance(ast,Discard): return Translator.pythonASTToAssemblyAST(ast.expr)
			elif isinstance(ast,Const): return ConstantOperand(ast.value)
			elif isinstance(ast,Assign):
				offset = 4*(len(memory)+1)
				memory[ast.nodes[0].name] = offset
				if isinstance(ast.expr,Const):

			return "Error: " + str(ast) + " currently not supported.\n"

		return translatePythonAST(ast)