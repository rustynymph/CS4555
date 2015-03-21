from PythonASTExtension import *
from LivenessAnalysis import *

class FunctionLiveness:
	
	@staticmethod
	def functionLiveness(ast,acc):
		if isinstance(ast,Function):
			func = LivenessAnalysis(ast)
			acc[ast.name] = LivenessAnalysis.livenessAnalysis(func)	
		return acc
