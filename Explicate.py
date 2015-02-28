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
counter = 1

class exp_stmt(Stmt):
	def __init__(self, nodes):
		Stmt.__init__(self, nodes)

class Explicate:

	exp_stmt.nodes = []
	
	@staticmethod
	def gen_count_number():
		global counter
		number = str(counter)
		counter += 1
		return number
	
	#helps us create new names for let	
	@staticmethod
	def create_new_name(name):
		new_name = "new" + "_" + Explicate.gen_count_number() + "_" + name
		return new_name

	@staticmethod	
	def dispatch(ast):
		if isinstance(ast,Name): return Explicate.visitName(ast)
		elif isinstance(ast,Const): return Explicate.visitConst(ast)
		elif isinstance(ast,Boolean): return Explicate.visitBoolean(ast)
		elif isinstance(ast,Add): return Explicate.explicateBinary(ast)
		elif isinstance(ast,And): return Explicate.explicateAnd(ast)
		elif isinstance(ast,Not): return Explicate.explicateNot(ast)
		elif isinstance(ast,Printnl): return exp_stmt.nodes.append(Printnl([Explicate.dispatch(ast.nodes[0])],None))
		elif isinstance(ast,Discard): return exp_stmt.nodes.append(Discard(Explicate.dispatch(ast.expr)))
		elif isinstance(ast,Assign): return Assign([AssName(ast.nodes[0].name,'OP_ASSIGN')], Explicate.dispatch(ast.expr))
		elif isinstance(ast, CallFunc): return Explicate.visitCallFunc(ast)
		elif isinstance(ast, Name): return Explicate.visitName(ast)
		elif isinstance(ast, Const): return Explicate.visitConst(ast)
		elif isinstance(ast, Boolean): return Explicate.visitBoolean(ast)
		elif isinstance(ast, UnarySub): return Explicate.explicateUnary(ast)
		elif isinstance(ast,Compare): return Explicate.explicateBinary(ast)
		elif isinstance(ast,Or): return Explicate.visitOr(ast)
		elif isinstance(ast, List): return Explicate.visitList(ast)
		elif isinstance(ast,Dict): return Explicate.visitDict(ast)
		elif isinstance(ast,Subscript): return Explicate.visitSubscript(ast)
		elif isinstance(ast,IfExp): return Explicate.explicateIfExp(ast)
		else: raise Exception("Error: Unrecognized node type")			
		
	@staticmethod		
	def visitName(ast): return Name(ast.name)

	@staticmethod
	def visitBoolean(ast): return InjectFrom(BOOL_t, Const(int(ast.value)))

	@staticmethod	
	def explicateNot(ast): return IfExp(InjectFrom(BOOL_t,Explicate.dispatch(ast.expr)), InjectFrom(BOOL_t, Const(0)), InjectFrom(BOOL_t, Const(1)))

	@staticmethod	
	def explicateAnd(ast):
		short = Explicate.create_new_name('let_and1')
		short_name = Name(short)
		
		return Let(short_name,Explicate.dispatch(ast.nodes[0]),IfExp(short_name,Explicate.dispatch(ast.nodes[1]),short_name))
		
	@staticmethod	
	def explicateOr(ast):
		short = Explicate.create_new_name('let_or1')
		short_name = Name(short)
		
		return Let(short_name,Explicate.dispatch(ast.nodes[0]),IfExp(short_name,short_name,Explicate.dispatch(ast.nodes[1])))				
	
	@staticmethod
	def explicateIfExp(ast): return IfExpr(Explicate.dispatch(ast.test),Explicate.dispatch(ast.then),Explicate.dispatch(ast.else_))
		
	@staticmethod   
	def visitSubscript(ast): return Subscript(Explicate.dispatch(ast.expr), ast.flags, Explicate.dispatch(ast.subs[0]))
	
	@staticmethod
	def visitList(ast): return List([Explicate.dispatch(node) for node in ast.nodes])
	
	@staticmethod
	def visitDict(ast): return Dict([(Explicate.dispatch(item[0]),Explicate.dispatch(item[1])) for item in ast.items])	
	
	@staticmethod
	def explicateUnary(ast):
		if isinstance(ast,UnarySub):
			usub = Explicate.create_new_name('let_us1')
			usub_name = Name(usub)
			explicated = Let(usub_name,Explicate.dispatch(ast.expr),
			IfExp(IsTag(INT_t, usub_name),InjectFrom(INT_t, UnarySub(ProjectTo(INT_t, usub_name))),
			IfExp(IsTag(BOOL_t, usub_name),InjectFrom(INT_t, UnarySub(ProjectTo(BOOL_t, usub_name))),
			CallFunc('error',[],None,None))))
		return explicated	
		
	@staticmethod			
	def explicateBinary(ast):
		if isinstance(ast,Add):		
			lhsname = Explicate.create_new_name('let_add_lhs')
			rhsname = Explicate.create_new_name('let_add_rhs')
			lhsvar = Name(lhsname)
			rhsvar = Name(rhsname)
			explicated = Let(lhsvar,Explicate.dispatch(ast.left),Let(rhsvar,Explicate.dispatch(ast.right),IfExp(And([Or([IsTag(INT_t,lhsvar),IsTag(BOOL_t, lhsvar)]),
							Or([IsTag(INT_t, rhsvar),IsTag(BOOL_t, rhsvar)])]),
					   Add((InjectFrom(GetTag(lhsvar),ProjectTo(INT_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(INT_t,rhsvar)))),
					   IfExp(And([IsTag(BIG_t, lhsvar),IsTag(BIG_t, rhsvar)]),
					   CallFunc('add_big', [InjectFrom(GetTag(lhsvar),ProjectTo(BIG_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(BIG_t,rhsvar))], None, None),
					   CallFunc('error',[],None,None)))))
					   
			explicated = Let(lhsvar,Explicate.dispatch(ast.left),Let(rhsvar,Explicate.dispatch(ast.right),IfExp(And([Or([IsTag(INT_t,lhsvar),IsTag(BOOL_t, lhsvar)]),
							Or([IsTag(INT_t, rhsvar),IsTag(BOOL_t, rhsvar)])]),
					   Add((InjectFrom(GetTag(lhsvar),ProjectTo(INT_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(INT_t,rhsvar)))),
					   IfExp(And([IsTag(BIG_t, lhsvar),IsTag(BIG_t, rhsvar)]),
					   CallFunc('add_big', [InjectFrom(GetTag(lhsvar),ProjectTo(BIG_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(BIG_t,rhsvar))], None, None),
					   CallFunc('error',[],None,None)))))					   
		elif isinstance(ast,Compare):
			lhsname = Explicate.create_new_name('let_comp_lhs')
			rhsname = Explicate.create_new_name('let_comp_rhs')
			lhsvar = Name(lhsname)
			rhsvar = Name(rhsname)
			explicated = Let(lhsvar,Explicate.dispatch(ast.expr),Let(rhsvar,Explicate.dispatch(ast.ops[1]),IfExp(And([Or([IsTag(INT_t,lhsvar),IsTag(BOOL_t, lhsvar)]),
							Or([IsTag(INT_t, rhsvar),IsTag(BOOL_t, rhsvar)])]),
					   Compare(InjectFrom(GetTag(lhsvar),ProjectTo(INT_t,lhsvar)),[ast.ops[0],InjectFrom(GetTag(rhsvar),ProjectTo(INT_t,rhsvar))]),
					   IfExp(And([IsTag(BIG_t, lhsvar),IsTag(BIG_t, rhsvar)]),
					   CallFunc('compare_big', [InjectFrom(GetTag(lhsvar),ProjectTo(BIG_t,lhsvar)),InjectFrom(GetTag(rhsvar),ProjectTo(BIG_t,rhsvar))], None, None),
					   CallFunc('error',[],None,None)))))
		return explicated

	@staticmethod	
	def visitConst(ast): return InjectFrom(INT_t,Const(ast.value))

	@staticmethod
	def visitCallFunc(ast): 
		if ast.node.name == 'input': return InjectFrom(INT_t, CallFunc('input', ast.args))

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
				Explicate.dispatch(node)
			return 0
            
		else:
			raise Exception("Error: Unrecognized node type")	
