from compiler.ast import *
class Optimizer:
	#Reduces running time by precomputing constant expressions
	@staticmethod
	def reduce(ast):
		if isinstance(ast, Module): return Module(ast.doc,Optimizer.reduce(ast.node));
		elif isinstance(ast,Stmt): return Stmt([Optimizer.reduce(n) for n in ast.nodes]);
		elif isinstance(ast,Printnl): return Printnl([Optimizer.reduce(n) for n in ast.nodes],ast.dest);
		elif isinstance(ast,Assign): return Assign(ast.nodes,Optimizer.reduce(ast.expr));
		elif isinstance(ast,Discard): return Discard(Optimizer.reduce(ast.expr));
		elif isinstance(ast,List): return List([Optimizer.reduce(n) for n in ast.nodes]);
		elif isinstance(ast,IfExp): return IfExp(Optimizer.reduce(ast.test),Optimizer.reduce(ast.then),Optimizer.reduce(ast.else_));
		elif isinstance(ast,Dict): return Dict([(Optimizer.reduce(n[0]),Optimizer.reduce(n[1])) for n in ast.items]);
		elif isinstance(ast,Or): return Or([Optimizer.reduce(n) for n in ast.nodes]);
		elif isinstance(ast,And): return And([Optimizer.reduce(n) for n in ast.nodes]);
		elif isinstance(ast,Compare): return Compare(Optimizer.reduce(ast.expr),[(n[0],Optimizer.reduce(n[1])) for n in ast.ops]);
		elif isinstance(ast,Subscript): return Subscript(Optimizer.reduce(ast.expr),ast.flags,ast.subs);

		elif isinstance(ast,Add):
			rln = Optimizer.reduce(ast.left);
			rrn = Optimizer.reduce(ast.right);
			if isinstance(rln,Const) and isinstance(rrn,Const): return Const(rln.value + rrn.value);
			else: return Add((rln,rrn));
		elif isinstance(ast,Mul):
			rln = Optimizer.reduce(ast.left);
			rrn = Optimizer.reduce(ast.right);
			if isinstance(rln,Const) and isinstance(rrn,Const): return Const(rln.value * rrn.value);
			else: return Mul((rln,rrn));
		elif isinstance(ast,UnarySub):
			e = Optimizer.reduce(ast.expr);
			if isinstance(e,Const): return Const(-e.value);
			else: return UnarySub(e);
		elif isinstance(ast,Not):
			e = Optimizer.reduce(ast.expr);
			if isinstance(e,Not): return e.expr
			else: return Not(e);
		elif isinstance(ast,CallFunc): return CallFunc(ast.node,[Optimizer.reduce(n) for n in ast.args]);
		elif isinstance(ast,Const) or isinstance(ast,AssName) or isinstance(ast,Name): return ast;
		else: raise Exception("AST reduction does not work on " + str(ast) + "node.");

	@staticmethod
	def negation(ast):
		if isinstance(ast, Module): return Module(ast.doc,Optimizer.negation(ast.node));
		elif isinstance(ast,Stmt): return Stmt([Optimizer.negation(n) for n in ast.nodes]);
		elif isinstance(ast,Printnl): return Printnl([Optimizer.negation(n) for n in ast.nodes],ast.dest);
		elif isinstance(ast,Assign): return Assign(ast.nodes,Optimizer.negation(ast.expr));
		elif isinstance(ast,Discard): return Discard(Optimizer.negation(ast.expr));
		elif isinstance(ast,List): return List([Optimizer.negation(n) for n in ast.nodes]);
		elif isinstance(ast,IfExp): return IfExp(Optimizer.negation(ast.test),Optimizer.negation(ast.then),Optimizer.negation(ast.else_));
		elif isinstance(ast,Dict): return Dict([(Optimizer.negation(n[0]),Optimizer.negation(n[1])) for n in ast.items]);
		elif isinstance(ast,Or): return Or([Optimizer.negation(n) for n in ast.nodes]);
		elif isinstance(ast,And): return And([Optimizer.negation(n) for n in ast.nodes]);
		elif isinstance(ast,Compare): return Compare(Optimizer.negation(ast.expr),[(n[0],Optimizer.negation(n[1])) for n in ast.ops]);
		elif isinstance(ast,Subscript): return Subscript(Optimizer.negation(ast.expr),ast.flags,ast.subs);

		elif isinstance(ast,Add):
			rln = Optimizer.negation(ast.left);
			rrn = Optimizer.negation(ast.right);
			return Add((rln,rrn));
		elif isinstance(ast,Mul):
			rln = Optimizer.negation(ast.left);
			rrn = Optimizer.negation(ast.right);
			return Mul((rln,rrn));
		elif isinstance(ast,Not):
			e = Optimizer.negation(ast.expr);
			return Not(e);			
		elif isinstance(ast,UnarySub):
			e = Optimizer.negation(ast.expr);
			if isinstance(e,UnarySub): return e.expr
			else: return UnarySub(e);
		elif isinstance(ast,CallFunc): return CallFunc(ast.node,[Optimizer.negation(n) for n in ast.args]);
		elif isinstance(ast,Const) or isinstance(ast,AssName) or isinstance(ast,Name): return ast;
		else: raise Exception("AST reduction does not work on " + str(ast) + "node.");
		
