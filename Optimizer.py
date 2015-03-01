from compiler.ast import *
from PythonASTExtension import *

class Optimizer:

	@staticmethod
	def reduceMap(ast):
		if isinstance(ast,Add):
			if isinstance(ast.left,Const) and isinstance(ast.right,Const): return Const(ast.left.value+ast.right.value)
			else: return ast
		elif isinstance(ast,UnarySub):
			if isinstance(ast.expr,Const): return Const(-ast.expr.value)
			else: return ast
		elif isinstance(ast,Mul):
			if isinstance(ast.left,Const) and isinstance(ast.right,Const): return Const(ast.left.value*ast.right.value)
			else: return ast
		else: return ast

	@staticmethod
	def negationMap(ast):
		if isinstance(ast,UnarySub):
			if isinstance(ast.expr,UnarySub): return ast.expr.expr
			else: return ast
		else: return ast