from PythonASTExtension import *

class Functionize():

	def __init__(self,replaceDictionary):
		self.replaceDictionary = replaceDictionary


	@staticmethod
	def replaceBigPyobjMap(ast):

		if isinstance(ast,Assign):
			if isinstance(ast.expr,Dict):
				stmtArray = []
				createDictionary = Assign(ast.nodes,CallFunc(Name("create_dict"),[],None,None))
				stmtArray += [createDictionary,Assign(ast.nodes,InjectFrom(Const(3),Name(ast.nodes[0].name)))]

				stmtArray += [CallFunc(Name("set_subscript"),[Name(ast.nodes[0].name),t[0],t[1]],None,None) for t in ast.expr.items]

				return Stmt(stmtArray)

			elif isinstance(ast.expr,List):
				stmtArray = []

				length = len(ast.expr.nodes) * 4
				createList = Assign(ast.nodes,CallFunc(Name("create_list"),[Const(length)],None,None))
				stmtArray += [createList,Assign(ast.nodes,InjectFrom(Const(3),Name(ast.nodes[0].name)))]

				for i in range(len(ast.expr.nodes)):
					key = Const(i * 4)
					value = ast.expr.nodes[i]
					stmtArray += [CallFunc(Name("set_subscript"),[Name(ast.nodes[0].name),key,value],None,None)]
				return Stmt(stmtArray)
			
			elif isinstance(ast.expr,Subscript):
				func = CallFunc(Name("get_subscript"),[ast.expr.expr] + ast.expr.subs,None,None)
				assign = Assign(ast.nodes,func)
				return assign

			elif isinstance(ast.nodes[0],Subscript):
				subscript = ast.nodes[0]
				return CallFunc(Name("set_subscript"),[subscript.expr,subscript.subs[0],ast.expr],None,None)
				
			elif isinstance(ast.expr,CreateClosure): return CallFunc(Name("create_closure"),[ast.expr.name]+[ast.expr.fvs],None,None)	
				
			elif isinstance(ast,GetClosure):
				name1 = ast.nodes[0].name + '$funptr'
				name2 = ast.nodes[0].name + '$getfvs'
				func1 = CallFunc(Name("get_fun_ptr"),[ast.name])
				func2 = CallFunc(Name("get_free_vars"),[ast.name])
				assign1 = [Assign([AssName(name1,'OP_ASSIGN')],func1)]
				assign2 = [Assign([AssName(name2,'OP_ASSIGN')],func2)]
				return Stmt(asign1+assign2)

			else: return ast
					
		else: return ast


	def replaceWithRuntimeEquivalentMap(self,ast):
		if isinstance(ast,Name) and ast.name in self.replaceDictionary:
			return Name(self.replaceDictionary[ast.name])
		elif isinstance(ast,Printnl):
			return CallFunc(Name("print_any"),ast.nodes,None,None)
		else: return ast


	@staticmethod
	def assignCallFuncMap(ast):
		if isinstance(ast,Assign) and isinstance(ast.expr,CallFunc):
			return AssignCallFunc(ast.nodes[0],ast.expr.node,ast.expr.args)
		else: return ast
