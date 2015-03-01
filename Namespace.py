from PythonASTExtension import *
class Namespace():
	environmentKeywords = ["input"]
	reservedKeywords = ["True","False"]
	def __init__(self,keywords):
		self.keywords = keywords

	def removeDependenciesMap(self,ast):
		if isinstance(ast,Name) and ast.name not in self.keywords: return Name("__"+ast.name)
		if isinstance(ast,AssName) and ast.name not in self.keywords: return AssName("__"+ast.name,ast.flags)
		else: return ast