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

	def lambdaFoldRight(self,ast,acc):
		if isinstance(ast,Lambda):
			acc = acc - set([arg for arg in ast.argnames])
			return acc
		elif isinstance(ast,AssName):
			acc = acc - set([ast.name])
			return acc
		elif isinstance(ast,Name):
			acc = acc | set([ast.name])
			return acc
		elif isinstance(ast,CallFunc):
			acc = acc - set([ast.node.name])
			return acc
		else: return acc