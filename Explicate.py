#!/usr/bin/python

class Explicate:
	
	def explicateName(ast):
		if(ast.name == "True"):
			return InjectFrom(BOOL_t, Const(1))
		elif(ast.name == "False"):
			return InjectFrom(BOOL_t, Const(0))
		else: return Name(n.name)
