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

		elif isinstance(ast,Add):
			rln = Optimizer.negation(ast.left);
			rrn = Optimizer.negation(ast.right);
			return Add((rln,rrn));
		elif isinstance(ast,Mul):
			rln = Optimizer.negation(ast.left);
			rrn = Optimizer.negation(ast.right);
			return Mul((rln,rrn));
		elif isinstance(ast,UnarySub):
			e = Optimizer.negation(ast.expr);
			if isinstance(e,UnarySub): return e.expr
			else: return UnarySub(e);
		elif isinstance(ast,CallFunc): return CallFunc(ast.node,[Optimizer.negation(n) for n in ast.args]);
		elif isinstance(ast,Const) or isinstance(ast,AssName) or isinstance(ast,Name): return ast;
		else: raise Exception("AST reduction does not work on " + str(ast) + "node.");
		
