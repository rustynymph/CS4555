class ClosureConversion(node):

		def __init__(self,freeVars):
			self.freeVars = freeVars

		def createClosure(self,ast):
			if isinstance(ast,Lambda):
				return 
				
			else: return ast
