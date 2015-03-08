from PythonASTExtension import *

class Functionize():

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
