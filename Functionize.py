from PythonASTExtension import *

class Functionize():

	def __init__(self,replaceDictionary):
		self.replaceDictionary = replaceDictionary


	@staticmethod
	def replaceBigPyobjMap(ast):
		if isinstance(ast,Assign) and isinstance(ast.expr,Dict):
			stmtArray = []
			createDictionary = Assign(ast.nodes,CallFunc(Name("create_dict"),[],None,None))
			stmtArray += [createDictionary]

			stmtArray += [CallFunc(Name("set_subscript"),[Name(ast.nodes[0].name),t[0],t[1]],None,None) for t in ast.expr.items]

			return Stmt(stmtArray)
		elif isinstance(ast,Assign) and isinstance(ast.expr,List):
			stmtArray = []

			length = len(ast.expr.nodes) * 4
			createList = Assign(ast.nodes,CallFunc(Name("create_list"),[Const(length)],None,None))
			stmtArray += [createList]

			for i in range(len(ast.expr.nodes)):
				key = Const(i * 4)
				value = ast.expr.nodes[i]
				stmtArray += [CallFunc(Name("set_subscript"),[Name(ast.nodes[0].name),key,value],None,None)]
			return Stmt(stmtArray)

		else: return ast


	def replaceWithRuntimeEquivalentMap(self,ast):
		if isinstance(ast,Name) and ast.name in self.replaceDictionary:
			return Name(self.replaceDictionary[ast.name])
		elif isinstance(ast,Printnl):
			return CallFunc(Name("print_any"),ast.nodes,None,None)
		else: return ast
