from PythonASTExtension import *
class Simplify():

	@staticmethod
	def nameToBoolMap(ast):
		if isinstance(ast,Name) and (ast.name == "True" or ast.name == "False"): return Boolean(ast.name == "True")
		else: return ast

	@staticmethod
	def removeDiscardMap(ast):
		if isinstance(ast,Discard): return ast.expr
		else: return ast