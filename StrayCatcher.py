from PythonASTExtension import *
class StrayCatcher:

	@staticmethod
	def catchStray(ast):
		if isinstance(ast,Module):
			newStmtList = []
			newFuncList = []
			for n in ast.node.nodes:
				if not isinstance(n,Function) or not isinstance(n,Lambda): newFuncList += [n]
				else: 
					newStmtList += [n]
			newFuncReturn = Return(Const(0))
			newFunc = Function(None,'main',[],[],0,None,Stmt(newFuncList + [Return(Const(0))]))
			newFunc.uniquename = 'main'
			newStmtList += [newFunc]
			return Module(None,Stmt(newStmtList))
		else: return ast