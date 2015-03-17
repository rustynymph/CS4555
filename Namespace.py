from PythonASTExtension import *
class Namespace():
	environmentKeywords = ["input"]
	reservedKeywords = ["True","False"]
	def __init__(self,keywords):
		self.keywords = keywords
		self.counter = 0
		self.uniquify = {}

	def getAndIncrement(self):
		counter = self.counter
		self.counter += 1
		return counter

	def uniquifyName(self,name):
		return name + "$" + str(self.getAndIncrement())

	def removeDependenciesMap(self,ast):
		if isinstance(ast,Name) and ast.name not in self.keywords: return Name("__"+ast.name)
		elif isinstance(ast,AssName) and ast.name not in self.keywords: return AssName("__"+ast.name,ast.flags)
		elif isinstance(ast,Function) and ast.name not in self.keywords:
			return Function(ast.decorators,"__"+ast.name,["__"+ arg for arg in ast.argnames],ast.defaults,ast.flags,ast.doc,ast.code)
		else: return ast

	def uniquifyMap(self,ast):
		if isinstance(ast,Name) and ast.name not in self.keywords:
			if ast.name not in self.uniquify: self.uniquify[ast.name] = self.uniquifyName(ast.name)

			return Name(self.uniquify[ast.name])
		elif isinstance(ast,AssName) and ast.name not in self.keywords:
			if ast.name not in self.uniquify: self.uniquify[ast.name] = self.uniquifyName(ast.name)

			return AssName(self.uniquify[ast.name],ast.flags)
		elif isinstance(ast,Function):
			args = []
			for arg in ast.argnames:
				if arg in self.uniquify: 
					args += [self.uniquify[arg]]
					del self.uniquify[arg]
				else: args += [arg]

			if ast.name not in self.uniquify: self.uniquify[ast.name] = self.uniquifyName(ast.name)

			return Function(ast.decorators,self.uniquify[ast.name],args,ast.defaults,ast.flags,ast.doc,ast.code)

		elif isinstance(ast,Lambda):
			args = []
			for arg in ast.argnames:
				if arg in self.uniquify: 
					args += [self.uniquify[arg]]
					del self.uniquify[arg]
				else: args += [arg]

			return Lambda(args,ast.defaults,ast.flags,ast.code)

		else: return ast