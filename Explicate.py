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
		
		
	def explicateIfExp(ast):
		
