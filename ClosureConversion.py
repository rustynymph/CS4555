from compiler.ast import *
from PythonASTExtension import *
from AssemblyAST import *

class ClosureConversion:

		def __init__(self,varmap):
			self.variableMapping = varmap

		def createClosure(self,node):
			if isinstance(node,Lambda):
				return CallFunc('create_closure',[var for var in node.argnames if var in self.variableMapping[node.uniquename]])
			else: return node
