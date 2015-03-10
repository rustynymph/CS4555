from PythonASTExtension import *

class Functionize():

	def __init__(self,replaceDictionary):
		self.replaceDictionary = replaceDictionary


	@staticmethod
	def replaceBigPyobjMap(ast):

		if isinstance(ast,Assign):
			if isinstance(ast.expr,Dict) and isinstance(ast.nodes[0],AssName):
				stmtArray = []
				createDictionary = Assign(ast.nodes,CallFunc(Name("create_dict"),[],None,None))
				stmtArray += [createDictionary]

				stmtArray += [CallFunc(Name("set_subscript"),[Name(ast.nodes[0].name),t[0],t[1]],None,None) for t in ast.expr.items]

				return Stmt(stmtArray)

			elif isinstance(ast.expr,List) and isinstance(ast.nodes[0],AssName):
				stmtArray = []

				length = len(ast.expr.nodes) * 4
				createList = Assign(ast.nodes,CallFunc(Name("create_list"),[Const(length)],None,None))
				stmtArray += [createList]

				for i in range(len(ast.expr.nodes)):
					key = Const(i * 4)
					value = ast.expr.nodes[i]
					stmtArray += [CallFunc(Name("set_subscript"),[Name(ast.nodes[0].name),key,value],None,None)]
				return Stmt(stmtArray)

			elif isinstance(ast.nodes[0],Subscript):
				subscript = ast.nodes[0]
				return CallFunc(Name("set_subscript"),[subscript.expr,subscript.subs[0],ast.expr],None,None)
			else: return ast

		else: return ast


	def replaceWithRuntimeEquivalentMap(self,ast):
		if isinstance(ast,Name) and ast.name in self.replaceDictionary:
			return Name(self.replaceDictionary[ast.name])
		elif isinstance(ast,Printnl):
			return CallFunc(Name("print_any"),ast.nodes,None,None)
		else: return ast
