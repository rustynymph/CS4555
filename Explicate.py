#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
import math
from AssemblyAST import *

INT_t = 0
BOOL_t = 1
BIG_t = 2
MASK = 3

class exp_stmt(Stmt):
	def __init__(self, nodes):
		Stmt.__init__(self, nodes)

class Explicate:
	
	exp_stmt.nodes = []
	
	#for name nodes, which includes variable names AND booleans
	@staticmethod
	def explicateName(ast): return Name(ast.name)

	@staticmethod
	def explicateBoolean(ast):
		if(ast.value == "True"):
			return InjectFrom(BOOL_t, Const(1))
		elif(ast.value == "False"):
			return InjectFrom(BOOL_t, Const(0))
		else:
			raise Exception("Error: Unrecognized node type")	
			
	@staticmethod
	def explicateBinary(ast):
		if isinstance(ast,Add):
			print("poop")
			lhsvar = ast.left
			rhsvar = ast.right			
			#explicated = Let(lhsvar,Let(rhsvar,IfExp(And([Or([IsTag(INT_t,lhsvar),
			#	   IsTag(BOOL_t, lhsvar)]),
			 #  Or([IsTag(INT_t, rhsvar),
				#   IsTag(BOOL_t, rhsvar)])]),
			   #Add((InjectFrom(GetTag(lhsvar),ProjectTo(INT_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(INT_t,rhsvar)))),
			   #IfExp(And([IsTag(BIG_t, lhsvar),
				#	   IsTag(BIG_t, rhsvar)]),
				#	   CallFunc(Name('add_big'), [InjectFrom(GetTag(lhsvar),ProjectTo(BIG_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(BIG_t,rhsvar))], None, None)))))
		
			explicated = IfExp(And([Or([IsTag(INT_t,lhsvar),IsTag(BOOL_t, lhsvar)]),
									Or([IsTag(INT_t, rhsvar),IsTag(BOOL_t, rhsvar)])]),
							   Add((InjectFrom(GetTag(lhsvar),ProjectTo(INT_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(INT_t,rhsvar)))),
							   IfExp(And([IsTag(BIG_t, lhsvar),IsTag(BIG_t, rhsvar)]),
							   CallFunc(Name('add_big'), [InjectFrom(GetTag(lhsvar),ProjectTo(BIG_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(BIG_t,rhsvar))], None, None),
							   CallFunc(Name('error'),[],None,None)))		
		print explicated
		return explicated
	
	#@staticmethod	
	#def explicateIfExp(ast): 
	
	@staticmethod	
	def visitConst(ast): return InjectFrom(INT_t,Const(ast.value))

	#def explicateLogical(ast):
	#	if isinstance(ast,And):
	#		lhsvar = ast.nodes[0]
	#		rhscar = ast.nodes[1]
	#		explicated = Let(lhsvar,Let(rhsvar,If
	#	elif isinstance(ast,Or):
	#	return explicated
	
	@staticmethod
	def explicate(ast):
		Explicate.explicate_helper(ast)
		print exp_stmt.nodes
		explicated_ast = Module(None, Stmt(exp_stmt.nodes))
		return explicated_ast
	
	@staticmethod
	def explicate_helper(ast,discard=False):
        
		if isinstance(ast, Module):
			print("hi")
			Explicate.explicate_helper(ast.node)
			return 0

		elif isinstance(ast, Stmt):
			print("hi2")
			for node in ast.nodes:
				Explicate.explicate_helper(node)
			return 0
			
		elif isinstance(ast, Printnl):
			print_var = ast.nodes[0]
			if isinstance(print_var,Add):
				print_exp = Explicate.explicate_helper(print_var)
			new_stmt = Printnl([print_exp], None)

		#elif isinstance(ast, Discard):

		elif isinstance(ast, Assign):
			print("yo")
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
			return exp_stmt.nodes.append(new_stmt)

		elif isinstance(ast, Add): return exp_stmt.nodes.append(Explicate.explicateBinary(ast))

		#elif isinstance(ast, UnarySub):

		#elif isinstance(ast, CallFunc):
                
		#elif isinstance(ast, Name):

		#elif isinstance(ast, Const):

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
