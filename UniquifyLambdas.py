from compiler.ast import *
from PythonASTExtension import *

class nameGenerator():

	def __init__(self,prefix,count=0):
		self.prefix = prefix
		self.count = count

	def getName(self):
		return self.prefix + "$" + str(self.count)

	def getNameAndIncrementCounter(self):
		name = self.getName()
		self.count += 1
		return name

class UniquifyLambdas:

	def __init__(self):
		self.createName = nameGenerator("lammy")	

	def labelLambdas(self,ast):
		if isinstance(ast,Lambda):
			ast.uniquename = self.createName.getNameAndIncrementCounter()
			return ast
		else: return ast