from PythonASTExtension import *
class Simplify():
	@staticmethod
	def removeNamespaceDependency(ast):
		if isinstance(ast,Module): return Module(ast.doc,Simplify.removeNamespaceDependency(ast.node))
		elif isinstance(ast,Stmt): return Stmt([Simplify.removeNamespaceDependency(n) for n in ast.nodes])
		elif isinstance(ast,Printnl): return Printnl([Simplify.removeNamespaceDependency(n) for n in ast.nodes],ast.dest)
		elif isinstance(ast,Assign): return Assign([Simplify.removeNamespaceDependency(n) for n in ast.nodes],Simplify.removeNamespaceDependency(ast.expr))
		elif isinstance(ast,Discard): return Discard(Simplify.removeNamespaceDependency(ast.expr))
		elif isinstance(ast,Add): return Add((Simplify.removeNamespaceDependency(ast.left),Simplify.removeNamespaceDependency(ast.right)))
		elif isinstance(ast,UnarySub): return UnarySub(Simplify.removeNamespaceDependency(ast.expr))

		elif isinstance(ast,Compare): return Compare(Simplify.removeNamespaceDependency(ast.expr,[(t[0],Simplify.removeNamespaceDependency(t[1])) for t in ast.ops]))
		elif isinstance(ast,Or): return Or([Simplify.removeNamespaceDependency(n) for n in ast.nodes])
		elif isinstance(ast,And): return And([Simplify.removeNamespaceDependency(n) for n in ast.nodes])
		elif isinstance(ast,Not): return Not(Simplify.removeNamespaceDependency(ast.expr))
		elif isinstance(ast,List): return List([Simplify.removeNamespaceDependency(ast.e)])
		elif isinstance(ast,Dict): return Dict([(Simplify.removeNamespaceDependency(t[0]),Simplify.removeNamespaceDependency(t[1])) for t in ast.items])
		elif isinstance(ast,Subscript): return Subscript(Simplify.removeNamespaceDependency(ast.expr),ast.flags,[Simplify.removeNamespaceDependency(n) for n in ast.subs])
		elif isinstance(ast,IfExp): return IfExp(Simplify.removeNamespaceDependency(ast.test),Simplify.removeNamespaceDependency(ast.then),Simplify.removeNamespaceDependency(ast.else_))

		#Leaf Nodes
		#Prepends "__" to the names of all of the variables
		elif isinstance(ast,Name): return Name("__"+ast.name)
		elif isinstance(ast,AssName): return AssName("__"+ast.name,ast.flags)
		elif isinstance(ast,Const): return ast
		elif isinstance(ast,Boolean): return ast
		#Needs to change in for next assignment
		elif isinstance(ast,CallFunc): 
			if isinstance(ast.node,Name):
				return CallFunc(ast.node,Simplify.removeNamespaceDependency(ast.args))
			else:
				return CallFunc(Simplify.removeNamespaceDependency(ast.node),Simplify.removeNamespaceDependency(ast.args))

	@staticmethod
	def nameToBool(ast):
		if isinstance(ast,Module): return Module(ast.doc,Simplify.nameToBool(ast.node))
		elif isinstance(ast,Stmt): return Stmt([Simplify.nameToBool(n) for n in ast.nodes])
		elif isinstance(ast,Printnl): return Printnl([Simplify.nameToBool(n) for n in ast.nodes],ast.dest)
		elif isinstance(ast,Assign): return Assign([Simplify.nameToBool(n) for n in ast.nodes],Simplify.nameToBool(ast.expr))
		elif isinstance(ast,Discard): return Discard(Simplify.nameToBool(ast.expr))
		elif isinstance(ast,Add): return Add((Simplify.nameToBool(ast.left),Simplify.nameToBool(ast.right)))
		elif isinstance(ast,UnarySub): return UnarySub(Simplify.nameToBool(ast.expr))

		elif isinstance(ast,Compare): return Compare(Simplify.nameToBool(ast.expr,[(t[0],Simplify.nameToBool(t[1])) for t in ast.ops]))
		elif isinstance(ast,Or): return Or([Simplify.nameToBool(n) for n in ast.nodes])
		elif isinstance(ast,And): return And([Simplify.nameToBool(n) for n in ast.nodes])
		elif isinstance(ast,Not): return Not(Simplify.nameToBool(ast.expr))
		elif isinstance(ast,List): return List([Simplify.nameToBool(ast.e)])
		elif isinstance(ast,Dict): return Dict([(Simplify.nameToBool(t[0]),Simplify.nameToBool(t[1])) for t in ast.items])
		elif isinstance(ast,Subscript): return Subscript(Simplify.nameToBool(ast.expr),ast.flags,[Simplify.nameToBool(n) for n in ast.subs])
		elif isinstance(ast,IfExp): return IfExp(Simplify.nameToBool(ast.test),Simplify.nameToBool(ast.then),Simplify.nameToBool(ast.else_))


		#Leaf Nodes
		#Prepends "__" to the names of all of the variables
		elif isinstance(ast,Name): 
			if ast.name == "True": return Boolean(True)
			elif ast.name == "False": return Boolean(False)
			else: return ast
		elif isinstance(ast,AssName):
			if ast.name == "True" or ast.name == "False": raise Exception(ast.name + " cannot be assigned to a value.")
			else: return ast
		elif isinstance(ast,Const): return ast
		#Needs to change in for next assignment
		elif isinstance(ast,CallFunc): 
			if isinstance(ast.node,Name):
				return CallFunc(ast.node,Simplify.removeNamespaceDependency(ast.args))
			else:
				return CallFunc(Simplify.removeNamespaceDependency(ast.node),Simplify.removeNamespaceDependency(ast.args))
