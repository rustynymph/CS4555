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
BIG_t = 3		#11
MASK = 3		#11
counter = 1

class Explicate:

	def __init__(self):
		self.counter = 0

	def getAndIncrement(self):
		counter = self.counter
		self.counter += 1
		return counter

	def explicateMap(self,ast):
		#Creates pyobj's
		if isinstance(ast,Const): return InjectFrom(Const(INT_t),ast)
		elif isinstance(ast,Boolean): return InjectFrom(Const(BOOL_t),Const(int(ast.value)))
		# elif isinstance(ast,List): return InjectFrom(Const(BIG_t),ast)
		# elif isinstance(ast,Dict): return InjectFrom(Const(BIG_t),ast)

		elif isinstance(ast,Add):
			leftName = Name("letAdd"+str(self.getAndIncrement()))
			rightName = Name("letAdd"+str(self.getAndIncrement()))
			#Checks if the left subtree is an int or bool
			leftPredicate = Or([IsTag(Const(INT_t),leftName),IsTag(Const(BOOL_t),leftName)])
			#Checks if the right subtree is an int or bool
			rightPredicate = Or([IsTag(Const(INT_t),rightName),IsTag(Const(BOOL_t),rightName)])
			#Checks if both subtrees are an int or a bool
			predicate = And([leftPredicate,rightPredicate])
			#Adds ints and bools
			addIntsAndBools = InjectFrom(Const(INT_t),Add((ProjectTo(Const(INT_t),leftName),ProjectTo(Const(INT_t),rightName))))
			#Adds bigs
			add = CallFunc(Name("add"),[ProjectTo(Const(BIG_t),leftName),ProjectTo(Const(BIG_t),rightName)],None,None)
			addBig = InjectFrom(Const(BIG_t),add)
			#Explicated add tree
			explicatedAdd = IfExp(predicate,addIntsAndBools,addBig)

			return Let(leftName,ast.left,Let(rightName,ast.right,explicatedAdd))
		elif isinstance(ast,Compare):
			leftName = Name("letCompare"+str(self.getAndIncrement()))
			rightName = Name("letCompare"+str(self.getAndIncrement()))

			leftIntAndBoolPredicate = Or([IsTag(Const(INT_t),leftName),IsTag(Const(INT_t),rightName)])
			rightIntAndBoolPredicate = Or([IsTag(Const(INT_t),rightName),IsTag(Const(BOOL_t),rightName)])
			intAndBoolPredicate = And([leftIntAndBoolPredicate,rightIntAndBoolPredicate])

			intAndBoolCompare = InjectFrom( Const(BOOL_t), Compare(ProjectTo(Const(BOOL_t),leftName), [('==',ProjectTo(Const(BOOL_t),rightName))]))

			bigPredicate = And([IsTag(Const(BIG_t),leftName),IsTag(Const(INT_t),rightName)])

			bigCompare = InjectFrom(Const(BOOL_t),CallFunc(Name("equal"),[leftName,rightName],None,None))

			bigIf = IfExp(bigPredicate,bigCompare,InjectFrom(Const(BOOL_t),Const(0)))

			intAndBoolIf = IfExp(intAndBoolPredicate,intAndBoolCompare,bigIf)

			letRight = Let(rightName,ast.ops[0][1],intAndBoolIf)
			letLeft = Let(leftName,ast.expr,letRight)
			return letLeft
			return intAndBoolIf

		elif isinstance(ast,UnarySub):
			return InjectFrom(Const(INT_t),UnarySub(ProjectTo(Const(INT_t),ast.expr)))
		elif isinstance(ast,CallFunc):
			#Not sure if we have to do anything here
			return ast
		elif isinstance(ast,Not):
			notexp = ProjectTo(Const(BOOL_t),Not(CallFunc(Name("is_true"),[ast],None,None)))
			return notexp

		elif isinstance(ast,Function):
			newlambda = Lambda(ast.argnames,ast.defaults,ast.flags,ast.code)
			assign = Assign([AssName(ast.name,'OP_ASSIGN')],newlambda)
			return assign
		
		elif isinstance(ast,Lambda): return Lambda(ast.argnames,ast.defaults,ast.flags,Stmt([Return(ast.code)]))
		
		elif isinstance(ast,Return): return ast
			
		else: return ast

	def shortCircuitMap(self,ast):
		if isinstance(ast,Or):
			previous = ast.nodes[len(ast.nodes)-1]
			orNamePrefix ="letOr$"+str(self.getAndIncrement())+"$"
			i = len(ast.nodes) - 1
			currentOrName = None
			for current in reversed(ast.nodes[:len(ast.nodes)-1]):
				currentOrName = Name(orNamePrefix + str(i))
				orexp = Let(currentOrName,current,IfExp(currentOrName,currentOrName,previous))

				previous = orexp
				i -= 1
			return previous

		elif isinstance(ast,And):
			previous = ast.nodes[len(ast.nodes)-1]
			andNamePrefix = "letAnd$"+str(self.getAndIncrement())+"$"
			i = len(ast.nodes) - 1
			for current in reversed(ast.nodes[:len(ast.nodes)-1]):
				currentAndName = Name(andNamePrefix+str(i))
				andexp = Let(currentAndName,current,IfExp(currentAndName,previous,currentAndName))

				previous = andexp
				i -= 1
			return previous
		else: return ast

	@staticmethod
	def explicateCompareMap(ast):
		if isinstance(ast,Compare):
			return IfExp(ast,Const(5),Const(1))
		else: return ast


	@staticmethod
	def removeIsTagMap(ast):
		if isinstance(ast,IsTag):
			return Compare(GetTag(ast.arg),[('==',ast.typ)])
		else: return ast
