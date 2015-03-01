from PythonASTExtension import *
class TraverseIR():
	@staticmethod
	def map(ast,f,environment=None):
		#P0 nodes
		if isinstance(ast,Module): 
			module = Module(ast.doc,TraverseIR.map(ast.node,f,environment))
			return f(environment, module) if environment else f(module)
		elif isinstance(ast,Stmt):
			stmt = Stmt([TraverseIR.map(n,f,environment) for n in ast.nodes])
			return f(environment,stmt) if environment else f(stmt)
		elif isinstance(ast,Printnl):
			printnl = Printnl([TraverseIR.map(n,f,environment) for n in ast.nodes],ast.dest)
			return f(environment,printnl) if environment else f(printnl)
		elif isinstance(ast,Assign):
			assign = Assign([TraverseIR.map(n,f,environment) for n in ast.nodes],TraverseIR.map(ast.expr,f,environment))
			return f(environment,assign) if environment else f(assign)
		elif isinstance(ast,Discard):
			discard = Discard(TraverseIR.map(ast.expr))
			return f(environment,discard) if environment else f(discard)
		elif isinstance(ast,Add):
			lhs = TraverseIR.map(ast.left,f,environment)
			rhs = TraverseIR.map(ast.right,f,environment)
			add = Add((lhs,rhs))
			return f(environment,add) if environment else f(add)
		elif isinstance(ast,UnarySub):
			unarysub = UnarySub(TraverseIR.map(ast.expr,f,environment))
			return f(environment,unarysub) if environment else f(unarysub)
		elif isinstance(ast,CallFunc):
			callfunc = CallFunc(TraverseIR.map(ast.node,f,environment),[TraverseIR.map(n,f,environment) for n in ast.args])
			return f(environment,callfunc) if environment else f(callfunc)
		elif isinstance(ast,Const):
			print ast
			return f(environment,ast) if environment else f(ast)
		elif isinstance(ast,AssName):
			return f(environment,ast) if environment else f(ast)
		elif isinstance(ast,Name):
			return f(environment,ast) if environment else f(ast)

		#P1 nodes
		elif isinstance(ast,List):
			l = List([TraverseIR.map(n,f,environment) for n in ast.nodes])
			return f(environment,l) if environment else f(l)
		elif isinstance(ast,IfExp):
			ifexp = IfExp(TraverseIR.map(ast.test,f,environment),TraverseIR.map(ast.then,f,environment),TraverseIR.map(ast.else_,f,environment))
			return f(environment,ifexp) if environment else f(ifexp)
		elif isinstance(ast,Dict):
			d = Dict([(TraverseIR.map(t[0]),TraverseIR.map(t[1])) for t in ast.items])
			return f(environment,d) if environment else f(d)
		elif isinstance(ast,Or):
			o = Or([TraverseIR.map(n,f,environment) for n in ast.nodes])
			return f(environment,o) if environment else f(o)
		elif isinstance(ast,And):
			a = And([TraverseIR.map(n,f,environment) for n in ast.nodes])
			return f(environment,a) if environment else f(a)
		elif isinstance(ast,Compare):
			compare = Compare(TraverseIR.map(ast.expr,f,environment),[(t[0],TraverseIR.map(t[1],f,environment)) for t in ast.ops])
			return f(environment,compare) if environment else f(compare)
		elif isinstance(ast,Subscript):
			subscript = Subscript(TraverseIR.map(ast.expr,f,environment),ast.flags,[TraverseIR.map(n) for n in ast.subs])
			return f(environment,subscript) if environment else f(subscript)
		elif isinstance(ast,Not):
			n = Not(TraverseIR.map(ast.expr))
			return f(environment,n) if environment else f(n)

		#P1 Extension nodes
		elif isinstance(ast,Boolean):
			return f(environment,ast) if environment else f(ast)

		else: raise Exception("map does not currently support the " + ast.__class__.__name__ + " node.")
