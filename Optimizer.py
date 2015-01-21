class Optimizer:
	#Reduces running time by precomputing constant expressions
	@staticmethod
	def reduce(ast):
		if isinstance(ast, Module): return Module(ast.doc,Parser.reduce(ast.node));
		elif isinstance(ast,Stmt): return Stmt([Parser.reduce(n) for n in ast.nodes]);
		elif isinstance(ast,Printnl): return Printnl([Parser.reduce(n) for n in ast.nodes],ast.dest);
		elif isinstance(ast,Assign): return Assign(ast.nodes,Parser.reduce(ast.expr));
		elif isinstance(ast,Discard): return Discard(Parser.reduce(ast.expr));

		elif isinstance(ast,Add):
			rln = Parser.reduce(ast.left);
			rrn = Parser.reduce(ast.right);
			if isinstance(rln,Const) and isinstance(rrn,Const): return Const(rln.value + rrn.value);
			else: return Add((rln,rrn));
		elif isinstance(ast,Mul):
			rln = Parser.reduce(ast.left);
			rrn = Parser.reduce(ast.right);
			if isinstance(rln,Const) and isinstance(rrn,Const): return Const(rln.value * rrn.value);
			else: return Mul((rln,rrn));
		elif isinstance(ast,UnarySub):
			e = Parser.reduce(ast.expr);
			if isinstance(e,Const): return Const(-e.value);
			else: return UnarySub(e);
		elif isinstance(ast,CallFunc): return CallFunc(ast.node,[Parser.reduce(n) for n in ast.args]);
		elif isinstance(ast,Const) or isinstance(ast,AssName) or isinstance(ast,Name): return ast;
		else: raise Exception("AST reduction does not work on " + str(ast) + "node.");