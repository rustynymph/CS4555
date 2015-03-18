from PythonASTExtension import *

class Orphan():
	def __init__(self,counter=0):
		self.counter = counter

	def getAndIncrement(self):
		counter = self.counter
		self.counter += 1
		return counter

	def findParentMap(self,ast):
		if isinstance(ast,Stmt):
			stmtArray =[]
			for n in ast.nodes:
				if (not isinstance(n,Printnl) and not isinstance(n,Function) and not isinstance(n,Return)) or isinstance(n,Assign):
					stmtArray += [Assign([AssName("orphan"+str(self.getAndIncrement()),'OP_ASSIGN')],n)]
				else: stmtArray += [n]
			return Stmt(stmtArray)
		else: return ast