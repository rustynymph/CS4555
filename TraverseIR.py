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
			nodes = [TraverseIR.map(n,f,environment) for n in ast.nodes]
			assign = Assign(nodes,TraverseIR.map(ast.expr,f,environment))
			return f(environment,assign) if environment else f(assign)
		elif isinstance(ast,Discard):
			discard = Discard(TraverseIR.map(ast.expr,f,environment))
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
			d = Dict([(TraverseIR.map(t[0],f,environment),TraverseIR.map(t[1],f,environment)) for t in ast.items])
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
			subscript = Subscript(TraverseIR.map(ast.expr,f,environment),ast.flags,[TraverseIR.map(n,f,environment) for n in ast.subs])
			return f(environment,subscript) if environment else f(subscript)
		elif isinstance(ast,Not):
			n = Not(TraverseIR.map(ast.expr,f,environment))
			return f(environment,n) if environment else f(n)

		#P1 Extension nodes
		elif isinstance(ast,Boolean):
			return f(environment,ast) if environment else f(ast)
		elif isinstance(ast,GetTag):
			gettag = GetTag(TraverseIR.map(ast.arg,f,environment))
			return f(environment,gettag) if environment else f(gettag)
		elif isinstance(ast,InjectFrom):
			injectfrom = InjectFrom(TraverseIR.map(ast.typ,f,environment),TraverseIR.map(ast.arg,f,environment))
			return f(environment,injectfrom) if environment else f(injectfrom)
		elif isinstance(ast,ProjectTo):
			projectto = ProjectTo(TraverseIR.map(ast.typ),TraverseIR.map(ast.arg,f,environment))
			return f(environment,projectto) if environment else f(projectto)
		elif isinstance(ast,Let):
			let = Let(TraverseIR.map(ast.var,f,environment),TraverseIR.map(ast.expr,f,environment),TraverseIR.map(ast.body,f,environment))
			return f(environment,let) if environment else f(let)
		elif isinstance(ast,IsTag):
			istag = IsTag(ast.typ,TraverseIR.map(ast.arg,f,environment))
			return f(environment,istag) if environment else f(istag)


		else: raise Exception("map does not currently support the " + ast.__class__.__name__ + " node. (" + str(ast) + ")")

	@staticmethod
	def foldPostOrderLeft(ast,f,acc,environment=None):
		#P0 nodes
		if isinstance(ast,Module): 
			subAcc = TraverseIR.foldPostOrderLeft(ast.node,f,acc,environment)
			return f(environment, ast,subAcc) if environment else f(ast,subAcc)
		elif isinstance(ast,Stmt):
			subAcc = acc
			for n in ast.nodes:
				subAcc = TraverseIR.foldPostOrderLeft(n,f,subAcc,environment)
			return f(environment,ast,subAcc) if environment else f(ast,subAcc)
		elif isinstance(ast,Printnl):
			subAcc = acc
			for n in ast.nodes:
				subAcc = TraverseIR.foldPostOrderLeft(n,f,subAcc,environment)
			return f(environment,ast,subAcc) if environment else f(ast,subAcc)
		elif isinstance(ast,Assign):
			nodesAcc = acc
			for n in ast.nodes:
				nodesAcc = TraverseIR.foldPostOrderLeft(n,f,nodesAcc,environment)
			exprAcc = TraverseIR.foldPostOrderLeft(ast.expr,f,nodesAcc,environment)
			return f(environment,ast,exprAcc) if environment else f(ast,exprAcc)
		elif isinstance(ast,Discard):
			discardAcc = TraverseIR.foldPostOrderLeft(ast.expr,f,acc,environment)
			return f(environment,ast,discardAcc) if environment else f(ast,discardAcc)
		elif isinstance(ast,Add):
			lhsAcc = TraverseIR.foldPostOrderLeft(ast.left,f,acc,environment)
			rhsAcc = TraverseIR.foldPostOrderLeft(ast.right,f,lhsAcc,environment)
			return f(environment,ast,rhsAcc) if environment else f(ast,rhsAcc)
		elif isinstance(ast,UnarySub):
			exprAcc = TraverseIR.foldPostOrderLeft(ast.expr,f,acc,environment)
			return f(environment,ast,exprAcc) if environment else f(ast,exprAcc)
		elif isinstance(ast,CallFunc):
			nodeAcc = TraverseIR.foldPostOrderLeft(ast.node,f,acc,environment)
			argsAcc = nodeAcc
			for n in ast.args:
				argsAcc = TraverseIR.foldPostOrderLeft(n,f,argsAcc,environment)
			return f(environment,callfunc,argsAcc) if environment else f(callfunc,argsAcc)
		elif isinstance(ast,Const):
			return f(environment,ast,acc) if environment else f(ast,acc)
		elif isinstance(ast,AssName):
			return f(environment,ast,acc) if environment else f(ast,acc)
		elif isinstance(ast,Name):
			return f(environment,ast,acc) if environment else f(ast,acc)

		#P1 nodes
		elif isinstance(ast,List):
			listAcc = acc
			for n in ast.nodes:
				listAcc = TraverseIR.foldPostOrderLeft(n,f,listAcc,environment)
			return f(environment,ast,listAcc) if environment else f(ast,listAcc)
		elif isinstance(ast,IfExp):
			testAcc = TraverseIR.foldPostOrderLeft(ast.test,f,acc,environment)
			thenAcc = TraverseIR.foldPostOrderLeft(ast.then,f,testAcc,environment)
			elseAcc = TraverseIR.foldPostOrderLeft(ast.else_,f,thenAcc,environment)
			return f(environment,ast,elseAcc) if environment else f(ast,elseAcc)
		elif isinstance(ast,Dict):
			dictAcc = acc
			for t in ast.items:
				valueAcc = TraverseIR.foldPostOrderLeft(t[1],f,dictAcc,environment)
				keyAcc = TraverseIR.foldPostOrderLeft(t[0],f,valueAcc,environment)
				dictAcc = keyAcc
			return f(environment,ast,dictAcc) if environment else f(ast,dictAcc)
		elif isinstance(ast,Or):
			orAcc = acc
			for n in ast.nodes:
				orAcc = TraverseIR.foldPostOrderLeft(n,f,orAcc,environment)
			return f(environment,ast,orAcc) if environment else f(ast,orAcc)
		elif isinstance(ast,And):
			andAcc = acc
			for n in ast.nodes:
				andAcc = TraverseIR.foldPostOrderLeft(n,f,andAcc,environment)
			return f(environment,ast,andAcc) if environment else f(ast,andAcc)
		elif isinstance(ast,Compare):
			compare0Acc = TraverseIR.foldPostOrderLeft(ast.expr,f,acc,environment)
			compareNAcc = compare0Acc
			for t in ast.ops:
				compareNAcc = TraverseIR.foldPostOrderLeft(t[1],f,compareNAcc,environment)
			return f(environment,ast,compareNAcc) if environment else f(ast,compareNAcc)
		elif isinstance(ast,Subscript):
			exprAcc = TraverseIR.foldPostOrderLeft(ast.expr,f,acc,environment)
			subsAcc = exprAcc
			for n in ast.subs:
				subsAcc = TraverseIR.foldPostOrderLeft(n,f,subsAcc,environment)
			return f(environment,ast,subsAcc) if environment else f(ast,subsAcc)
		elif isinstance(ast,Not):
			notAcc = TraverseIR.foldPostOrderLeft(ast.expr,f,acc,environment)
			return f(environment,ast,notAcc) if environment else f(ast,notAcc)

		#P1 Extension nodes
		elif isinstance(ast,Boolean):
			return f(environment,ast,acc) if environment else f(ast,acc)
		elif isinstance(ast,GetTag):
			argAcc = TraverseIR.foldPostOrderLeft(ast.arg,f,acc,environment)
			return f(environment,ast,argAcc) if environment else f(ast,argAcc)
		elif isinstance(ast,InjectFrom):
			argAcc = TraverseIR.foldPostOrderLeft(ast.arg,f,acc,environment)
			return f(environment,ast,argAcc) if environment else f(ast,argAcc)
		elif isinstance(ast,ProjectTo):
			argAcc = TraverseIR.foldPostOrderLeft(ast.arg,f,acc,environment)
			return f(environment,ast,argAcc) if environment else f(ast,argAcc)
		elif isinstance(ast,Let):
			varAcc = TraverseIR.foldPostOrderLeft(ast.var,f,acc,environment)
			exprAcc = TraverseIR.foldPostOrderLeft(ast.expr,f,varAcc,environment)
			bodyAcc = TraverseIR.foldPostOrderLeft(ast.body,f,exprAcc,environment)
			return f(environment,ast,bodyAcc) if environment else f(ast,bodyAcc)
		elif isinstance(ast,IsTag):
			argAcc = TraverseIR.foldPostOrderLeft(ast.arg,f,acc,environment)
			return f(environment,ast,argAcc) if environment else f(ast,argAcc)
		else: raise Exception("foldPostOrderLeft does not currently support the " + ast.__class__.__name__ + " node.")
