from PythonASTExtension import *
import inspect
class TraverseIR():

	@staticmethod
	def transferAttributes(fromNode,toNode):
		fromAttributes = inspect.getmembers(fromNode)
		fromAttributes = [fromAttributes[i][0] for i in range(len(fromAttributes))]
		toAttributes = inspect.getmembers(toNode)
		toAttributes = [toAttributes[i][0] for i in range(len(toAttributes))]
		transferKeys = [k for k in fromAttributes if k not in toAttributes]

		for transfer in transferKeys:
			setattr(toNode,transfer,getattr(fromNode,transfer))

	@staticmethod
	def map(ast,f,environment=None):
		#P0 nodes
		if isinstance(ast,Module): 
			module = Module(ast.doc,TraverseIR.map(ast.node,f,environment))
			# if hasattr(ast,'liveness'): module.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,module)
			newmodule = f(environment, module) if environment else f(module)
			TraverseIR.transferAttributes(module,newmodule)
			return newmodule
		elif isinstance(ast,Stmt):
			#print ast
			stmt = Stmt([TraverseIR.map(n,f,environment) for n in ast.nodes])
			# if hasattr(ast,'liveness'): stmt.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,stmt)
			newstmt = f(environment,stmt) if environment else f(stmt)
			TraverseIR.transferAttributes(stmt,newstmt)
			return newstmt
		elif isinstance(ast,Printnl):
			printnl = Printnl([TraverseIR.map(n,f,environment) for n in ast.nodes],ast.dest)
			# if hasattr(ast,'liveness'): printnl.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,printnl)
			newprintnl = f(environment,printnl) if environment else f(printnl)
			TraverseIR.transferAttributes(printnl,newprintnl)
			return newprintnl
		elif isinstance(ast,Assign):
			nodes = [TraverseIR.map(n,f,environment) for n in ast.nodes]
			assign = Assign(nodes,TraverseIR.map(ast.expr,f,environment))
			# if hasattr(ast,'liveness'): assign.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,assign)
			newassign = f(environment,assign) if environment else f(assign)
			TraverseIR.transferAttributes(assign,newassign)
			return newassign
		elif isinstance(ast,Discard):
			discard = Discard(TraverseIR.map(ast.expr,f,environment))
			# if hasattr(ast,'liveness'): discard.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,discard)
			newdiscard = f(environment,discard) if environment else f(discard)
			TraverseIR.transferAttributes(discard,newdiscard)
			return newdiscard
		elif isinstance(ast,Add):
			lhs = TraverseIR.map(ast.left,f,environment)
			rhs = TraverseIR.map(ast.right,f,environment)
			add = Add((lhs,rhs))
			# if hasattr(ast,'liveness'): add.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,add)
			newadd = f(environment,add) if environment else f(add)
			TraverseIR.transferAttributes(add,newadd)
			return newadd
		elif isinstance(ast,UnarySub):
			unarysub = UnarySub(TraverseIR.map(ast.expr,f,environment))
			# if hasattr(ast,'liveness'): unarysub.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,unarysub)
			newunarysub = f(environment,unarysub) if environment else f(unarysub)
			TraverseIR.transferAttributes(unarysub,newunarysub)
			return newunarysub
		elif isinstance(ast,CallFunc):
			callfunc = CallFunc(TraverseIR.map(ast.node,f,environment),[TraverseIR.map(n,f,environment) for n in ast.args])
			# if hasattr(ast,'liveness'): callfunc.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,callfunc)
			newCallFunc =  f(environment,callfunc) if environment else f(callfunc)
			TraverseIR.transferAttributes(callfunc,newCallFunc)
			return newCallFunc
		elif isinstance(ast,Const):
			const = f(environment,ast) if environment else f(ast)
			TraverseIR.transferAttributes(ast,const)
			return const
		elif isinstance(ast,AssName):
			assname = f(environment,ast) if environment else f(ast)
			TraverseIR.transferAttributes(ast,assname)
			return assname
		elif isinstance(ast,Name):
			name = f(environment,ast) if environment else f(ast)
			TraverseIR.transferAttributes(ast,name)
			return name

		#P1 nodes
		elif isinstance(ast,List):
			l = List([TraverseIR.map(n,f,environment) for n in ast.nodes])
			# if hasattr(ast,'liveness'): l.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,l)
			newl = f(environment,l) if environment else f(l)
			TraverseIR.transferAttributes(l,newl)
			return newl
		elif isinstance(ast,IfExp):
			ifexp = IfExp(TraverseIR.map(ast.test,f,environment),TraverseIR.map(ast.then,f,environment),TraverseIR.map(ast.else_,f,environment))
			# if hasattr(ast,'liveness'): ifexp.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,ifexp)
			newifexp = f(environment,ifexp) if environment else f(ifexp)
			TraverseIR.transferAttributes(ifexp,newifexp)
			return newifexp
		elif isinstance(ast,Dict):
			d = Dict([(TraverseIR.map(t[0],f,environment),TraverseIR.map(t[1],f,environment)) for t in ast.items])
			# if hasattr(ast,'liveness'): d.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,d)
			newd = f(environment,d) if environment else f(d)
			TraverseIR.transferAttributes(d,newd)
			return newd
		elif isinstance(ast,Or):
			o = Or([TraverseIR.map(n,f,environment) for n in ast.nodes])
			# if hasattr(ast,'liveness'): o.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,o)
			newo = f(environment,o) if environment else f(o)
			TraverseIR.transferAttributes(o,newo)
			return newo
		elif isinstance(ast,And):
			a = And([TraverseIR.map(n,f,environment) for n in ast.nodes])
			# if hasattr(ast,'liveness'): a.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,a)
			newa = f(environment,a) if environment else f(a)
			TraverseIR.transferAttributes(a,newa)
			return newa
		elif isinstance(ast,Compare):
			compare = Compare(TraverseIR.map(ast.expr,f,environment),[(t[0],TraverseIR.map(t[1],f,environment)) for t in ast.ops])
			# if hasattr(ast,'liveness'): compare.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,compare)
			newCompare = f(environment,compare) if environment else f(compare)
			TraverseIR.transferAttributes(compare,newCompare)
			return newCompare
		elif isinstance(ast,Subscript):
			subscript = Subscript(TraverseIR.map(ast.expr,f,environment),ast.flags,[TraverseIR.map(n,f,environment) for n in ast.subs])
			# if hasattr(ast,'liveness'): subscript.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,subscript)
			newSubscript = f(environment,subscript) if environment else f(subscript)
			TraverseIR.transferAttributes(subscript,newSubscript)
			return newSubscript
		elif isinstance(ast,Not):
			n = Not(TraverseIR.map(ast.expr,f,environment))
			# if hasattr(ast,'liveness'): n.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,n)
			newn = f(environment,n) if environment else f(n)
			TraverseIR.transferAttributes(n,newn)
			return newn

		#P1 Extension nodes
		elif isinstance(ast,Boolean):
			boolean = f(environment,ast) if environment else f(ast)
			TraverseIR.transferAttributes(ast,boolean)
			return boolean
		elif isinstance(ast,GetTag):
			gettag = GetTag(TraverseIR.map(ast.arg,f,environment))
			# if hasattr(ast,'liveness'): gettag.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,gettag)
			newgettag = f(environment,gettag) if environment else f(gettag)
			TraverseIR.transferAttributes(gettag,newgettag)
			return newgettag
		elif isinstance(ast,InjectFrom):
			injectfrom = InjectFrom(TraverseIR.map(ast.typ,f,environment),TraverseIR.map(ast.arg,f,environment))
			# if hasattr(ast,'liveness'): injectfrom.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,injectfrom)
			newinjectfrom = f(environment,injectfrom) if environment else f(injectfrom)
			TraverseIR.transferAttributes(injectfrom,newinjectfrom)
			return newinjectfrom
		elif isinstance(ast,ProjectTo):
			projectto = ProjectTo(TraverseIR.map(ast.typ,f,environment),TraverseIR.map(ast.arg,f,environment))
			# if hasattr(ast,'liveness'): projectto.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,projectto)
			newprojectto = f(environment,projectto) if environment else f(projectto)
			TraverseIR.transferAttributes(projectto,newprojectto)
			return newprojectto
		elif isinstance(ast,Let):
			let = Let(TraverseIR.map(ast.var,f,environment),TraverseIR.map(ast.expr,f,environment),TraverseIR.map(ast.body,f,environment))
			# if hasattr(ast,'liveness'): let.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,let)
			newlet = f(environment,let) if environment else f(let)
			TraverseIR.transferAttributes(let,newlet)
			return newlet
		elif isinstance(ast,IsTag):
			istag = IsTag(ast.typ,TraverseIR.map(ast.arg,f,environment))
			# if hasattr(ast,'liveness'): istag.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,istag)
			newistag = f(environment,istag) if environment else f(istag)
			TraverseIR.transferAttributes(istag,newistag)
			return newistag

		#P2 nodes
		elif isinstance(ast,Function):
			func = Function(ast.decorators,ast.name,ast.argnames,ast.defaults,ast.flags,ast.doc,TraverseIR.map(ast.code,f,environment))
			# if hasattr(ast,'liveness'): func.liveness = ast.liveness
			# if hasattr(ast,'uniquename'): func.uniquename = ast.uniquename
			TraverseIR.transferAttributes(ast,func)
			newfunc = f(environment,func) if environment else f(func)
			TraverseIR.transferAttributes(func,newfunc)
			return newfunc
		elif isinstance(ast,Lambda):
			lamb = Lambda(ast.argnames,ast.defaults,ast.flags,TraverseIR.map(ast.code,f,environment))
			# if hasattr(ast,'liveness'): lamb.liveness = ast.liveness
			# if hasattr(ast,'uniquename'): lamb.uniquename = ast.uniquename
			TraverseIR.transferAttributes(ast,lamb)
			newlamb = f(environment,lamb) if environment else f(lamb)
			TraverseIR.transferAttributes(lamb,newlamb)
			return newlamb
		elif isinstance(ast,Return):
			ret = Return(TraverseIR.map(ast.value,f,environment))
			# if hasattr(ast,'liveness'): ret.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,ret)
			newret = f(environment,ret) if environment else f(ret)
			TraverseIR.transferAttributes(ret,newret)
			return newret
		elif isinstance(ast,AssignCallFunc):
			callfunc = AssignCallFunc(TraverseIR.map(ast.var,f,environment),TraverseIR.map(ast.name,f,environment),[TraverseIR.map(arg,f,environment) for arg in ast.args])
			# if hasattr(ast,'liveness'): callfunc.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,callfunc)
			newCallFunc = f(environment,callfunc) if environment else f(callfunc)
			TraverseIR.transferAttributes(callfunc,newCallFunc)
			return newCallFunc
		elif isinstance(ast,AugAssign):
			augassign = AugAssign(TraverseIR.map(ast.node,f,environment),ast.op,TraverseIR.map(ast.expr,f,environment))
			# if hasattr(ast,'liveness'): augassign.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,augassign)
			newaugassign = f(environment,augassign) if environment else f(augassign)
			TraverseIR.transferAttributes(augassign,newaugassign)
			return newaugassign
		elif isinstance(ast,CreateClosure):
			closure = CreateClosure(TraverseIR.map(ast.name,f,environment),List([TraverseIR.map(i,f,environment) for i in ast.fvs.nodes]))
			# if hasattr(ast,'liveness'): closure.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,closure)
			newClosure = f(environment,closure) if environment else f(closure)
			TraverseIR.transferAttributes(closure,newClosure)
			return newClosure
		elif isinstance(ast,GetClosure):
			closure = GetClosure(TraverseIR.map(ast.name,f,environment),[TraverseIR.map(i,f,environment) for i in ast.args])
			# if hasattr(ast,'liveness'): closure.liveness = ast.liveness
			TraverseIR.transferAttributes(ast,closure)
			newClosure = f(environment,closure) if environment else f(closure)
			TraverseIR.transferAttributes(closure,newClosure)
			return newClosure
		elif isinstance(ast,IndirectFuncCall):
			ifc = IndirectFuncCall(TraverseIR.map(ast.name,f,environment),[TraverseIR.map(i,f,environment) for i in ast.args],TraverseIR.map(ast.fvs,f,environment))
			TraverseIR.transferAttributes(ast,ifc)
			newIfc = f(environment,ifc) if environment else f(ifc)
			TraverseIR.transferAttributes(ifc,newIfc)
			return newIfc

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
			print ast
			for n in ast.nodes:
				print n
				nodesAcc = TraverseIR.foldPostOrderLeft(n,f,nodesAcc,environment)
			exprAcc = TraverseIR.foldPostOrderLeft(ast.expr,f,nodesAcc,environment)
			print
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
			return f(environment,ast,argsAcc) if environment else f(ast,argsAcc)
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
			print ast
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
			
		#P2 nodes
		elif isinstance(ast,Lambda):
			codeAcc = TraverseIR.foldPostOrderLeft(ast.code,f,acc,environment)
			return f(environment,ast,codeAcc) if environment else f(ast,codeAcc)
			
		elif isinstance(ast,Function):
			codeAcc = TraverseIR.foldPostOrderLeft(ast.code,f,acc,environment)
			return f(environment,ast,codeAcc) if environment else f(ast,codeAcc)
			
		elif isinstance(ast,Return):
			valAcc = TraverseIR.foldPostOrderLeft(ast.value,f,acc,environment)
			return f(environment,ast,valAcc) if environment else f(ast,valAcc)
			
		elif isinstance(ast,CreateClosure):
			nameAcc = TraverseIR.foldPostOrderLeft(ast.name,f,acc,environment)
			fvsAcc = nameAcc
			for n in ast.fvs:
				fvsAcc = TraverseIR.foldPostOrderLeft(n,f,fvsAcc,environment)
			return f(environment,ast,fvsAcc) if environment else f(ast,fvsAcc)
			
		elif isinstance(ast,GetClosure):
			nameAcc = TraverseIR.foldPostOrderLeft(ast.name,f,acc,environment)
			return f(environment,ast,nameAcc) if environment else f(ast,nameAcc)	
			
		else:
			print str(ast)
			raise Exception("foldPostOrderLeft does not currently support the " + ast.__class__.__name__ + " node.")
