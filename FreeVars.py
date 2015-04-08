from compiler.ast import *
from PythonASTExtension import *
from TraverseIR import TraverseIR

class FreeVars:

	allFreeVars = set()
	#variableMapping = {}
	#lambdafvs = set()

	def __init__(self):
		pass

	def calcFreeVars(self,ast):
		if isinstance(ast,Lambda):
			fvs_set = TraverseIR.foldPostOrderRight(ast,LambdaFreeVars.lambdaFoldRight,set(),LambdaFreeVars(ast.uniquename))
			FreeVars.allFreeVars = FreeVars.allFreeVars | fvs_set
			ast.fvs = fvs_set
			print "\n\n\n\n"+"FreeVars test"+"\n"+str(ast)+"\n"+str(ast.fvs)+"\n\n\n"
			return ast
		else: return ast

	@staticmethod
	def getAllFreeVars(): return FreeVars.allFreeVars

class LambdaFreeVars:

	def __init__(self,uniquename):
		self.uniquename = uniquename
		self.reservedNames = ['input','input_int','print_any','add','set_subscript','create_list','create_dict','get_fun_ptr','get_free_vars','main']

	def lambdaFoldRight(self,ast,acc):
		if isinstance(ast,Lambda): return acc - set([arg for arg in ast.argnames])
		elif isinstance(ast,AssName): return acc - set([ast.name])
		elif isinstance(ast,Name): return acc | set([ast.name])
		elif isinstance(ast,CallFunc): return acc - set([ast.node.name]) if (ast.node.name in self.reservedNames) else acc
		elif isinstance(ast,Let): return acc - set([ast.var.name])
		else: return acc