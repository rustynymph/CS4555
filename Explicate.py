#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
import math
from AssemblyAST import *
from PythonASTExtension import *

INT_t = 0		#00
BOOL_t = 1		#01
BIG_t = 2		#10
MASK = 3		#11

class exp_stmt(Stmt):
	def __init__(self, nodes):
		Stmt.__init__(self, nodes)

class Explicate:
	
	exp_stmt.nodes = []
	
	#for name nodes, which includes variable names AND booleans
	@staticmethod
	def explicateName(ast): return Name(ast.name)

	@staticmethod
	def explicateBoolean(ast): return InjectFrom(BOOL_t, Const(int(ast.value)))
			
	@staticmethod
	def explicateBinary(ast):
		if isinstance(ast,Add):
			lhsvar = ast.left
			rhsvar = ast.right			

			explicated = IfExp(And([Or([IsTag(INT_t,lhsvar),IsTag(BOOL_t, lhsvar)]),
							Or([IsTag(INT_t, rhsvar),IsTag(BOOL_t, rhsvar)])]),
					   Add((InjectFrom(GetTag(lhsvar),ProjectTo(INT_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(INT_t,rhsvar)))),
					   IfExp(And([IsTag(BIG_t, lhsvar),IsTag(BIG_t, rhsvar)]),
					   CallFunc('add_big', [InjectFrom(GetTag(lhsvar),ProjectTo(BIG_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(BIG_t,rhsvar))], None, None),
					   CallFunc('error',[],None,None)))		
		return explicated
	
	#@staticmethod
	#def explicateCallFunc(ast):
	#	explicated = InjectFrom(GetTag(CallFunc('input', [], None, None)),ProjectTo(INT_t,)		
	#	return explicated		
	
	@staticmethod	
	def visitConst(ast): return InjectFrom(INT_t,Const(ast.value))

	@staticmethod
	def explicate(ast):
		Explicate.explicate_helper(ast)
		explicated_ast = Module(None, Stmt(exp_stmt.nodes))
		return explicated_ast
	
	@staticmethod
	def explicate_helper(ast,discard=False):    
		if isinstance(ast, Module):	return Explicate.explicate_helper(ast.node)

		elif isinstance(ast, Stmt):
			for node in ast.nodes:
				Explicate.explicate_helper(node)
			return 0
			
		elif isinstance(ast, Printnl):
			print_var = ast.nodes[0]
			print_exp = Explicate.explicate_helper(print_var)
			return exp_stmt.nodes.append(Printnl([print_exp],None))

		elif isinstance(ast, Discard):
			discard_exp = Explicate.explicate_helper(ast.expr)
			return exp_stmt.nodes.append(Discard(discard_exp))

		elif isinstance(ast, Assign):
			right = ast.expr
			if isinstance(right,Name):
				right_exp = Explicate.explicateName(right)
			elif isinstance(right,Const):
				right_exp = Explicate.visitConst(right)
			elif isinstance(right,Add):
				right_exp = Explicate.explicateBinary(right)
			#elif isinstance(right,List):
			#elif isinstance(right,Dict):
			#elif isinstance(right,And):
			#elif isinstance(right,Or):
			#elif isinstance(right,Compare):
			#elif isinstance(right,IfExp):
			#elif isinstance(right,Subscript):
			assname = str(ast.nodes[0].name)
			new_stmt = Assign([AssName(assname,'OP_ASSIGN')], right_exp)
			#return exp_stmt.nodes.append(new_stmt)
			return new_stmt

		elif isinstance(ast, Add): return Explicate.explicateBinary(ast)

		#elif isinstance(ast, UnarySub):

		elif isinstance(ast, CallFunc): return Explicate.explicateCallFunc(ast)
                
		elif isinstance(ast, Name): return Explicate.explicateName(ast)

		elif isinstance(ast, Const): return Explicate.visitConst(ast)
		
		elif isinstance(ast, Boolean): return Explicate.explicateBoolean(ast)
		
		#elif isinstance(ast,Compare):

		#elif isinstance(ast,Or):
	
		#elif isinstance(ast,And):

		#elif isinstance(ast,Not):

		#elif isinstance(ast, List):

		#elif isinstance(ast,Dict):

		#elif isinstance(ast,Subscript):

		#elif isinstance(ast,IfExp):
            
		else:
			raise Exception("Error: Unrecognized node type")	
