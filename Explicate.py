#!/usr/bin/python

class Explicate:
	
	#for name nodes, which includes variable names AND booleans
	def explicateName(ast):
		if(ast.name == "True"):
			return InjectFrom(BOOL_t, Const(1))
		elif(ast.name == "False"):
			return InjectFrom(BOOL_t, Const(0))
		else: return Name(ast.name)

	def explicateBinary(ast):
		if isinstance(ast,Add):
			lhsvar = ast.left
			rhsvar = ast.right			
			explicated = Let(lhsvar,Let(rhsvar,IfExp(And([Or([IsTag(INT_t, lhsvar),
				   IsTag(BOOL_t, lhsvar)]),
			   Or([IsTag(INT_t, rhsvar),
				   IsTag(BOOL_t, rhsvar)])]),
			   Add(InjectFrom(GetTag(lhs),ProjectTo(INT_t)),InjectFrom(GetTag(rhs),ProjectTo(INT_t))),
			   IfExp(And([IsTag(BIG_t, lhsvar),
					   IsTag(BIG_t, rhsvar)]),
					   CallFunc(Name('add_big'), [InjectFrom(GetTag(lhsvar),ProjectTo(BIG_t)),InjectFrom(GetTag(rhsvar),ProjectTo(BIG_t))], None, None)))))
		return explicated
		
	def explicateIfExp(ast):
		
	def visitConst(ast):
		return InjectFrom(INT_t,Const(ast.value))

	def explicateLogical(ast):
		if isinstance(ast,And):
			lhsvar = ast.nodes[0]
			rhscar = ast.nodes[1]
			explicated = Let(lhsvar,Let(rhsvar,If
		elif isinstance(ast,Or):
		return explicated
	
