from compiler.ast import *
from AssemblyAST import *

class Translator:

	@staticmethod
	def pythonASTToAssemblyAST(ast):
		if isinstance(ast,Module): return AssemblyProgram([Translator.pythonASTToAssemblyAST(ast.node)])
		elif isinstance(ast,Stmt): return AssemblyFunction("main",[Translator.pythonASTToAssemblyAST(n) for n in ast.nodes])
		elif isinstance(ast,Discard): return Translator.pythonASTToAssemblyAST(ast.expr)
		elif isinstance(ast,Const): return ConstantOperand(ast.value)

		return "Error: " + str(ast) + " currently not supported.\n"