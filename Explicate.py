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
		if isinstance(ast,Const): return InjectFrom(INT_t,ast)
		elif isinstance(ast,Boolean): return InjectFrom(BOOL_t,Const(int(ast.value)))
		elif isinstance(ast,List): return InjectFrom(BIG_t,ast)
		elif isinstance(ast,Dict): return InjectFrom(BIG_t,ast)

		elif isinstance(ast,Add):
			leftName = Name("letAdd"+str(self.getAndIncrement()))
			rightName = Name("letAdd"+str(self.getAndIncrement()))
			#Checks if the left subtree is an int or bool
			leftPredicate = Or([IsTag(INT_t,leftName),IsTag(BOOL_t,leftName)])
			#Checks if the right subtree is an int or bool
			rightPredicate = Or([IsTag(INT_t,rightName),IsTag(BOOL_t,rightName)])
			#Checks if both subtrees are an int or a bool
			predicate = And([leftPredicate,rightPredicate])
			#Adds ints and bools
			addIntsAndBools = InjectFrom(INT_t,Add((ProjectTo(INT_t,leftName),ProjectTo(INT_t,rightName))))
			#Adds bigs
			add = CallFunc(Name("add"),[ProjectTo(BIG_t,leftName),ProjectTo(BIG_t,rightName)],None,None)
			addBig = InjectFrom(BIG_t,add)
			#Explicated add tree
			explicatedAdd = IfExp(predicate,addIntsAndBools,addBig)

			return Let(leftName,ast.left,Let(rightName,ast.right,explicatedAdd))
		elif isinstance(ast,UnarySub):
			return InjectFrom(INT_t,UnarySub(ProjectTo(INT_t,ast.expr)))
		elif isinstance(ast,CallFunc):
			#Not sure if we have to do anything here
			return ast
		elif isinstance(ast,Not):
			notexp = ProjectTo(BOOL_t,ast)
			return notexp

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
	def removeIsTagMap(ast):
		if isinstance(ast,IsTag):
			return Compare(GetTag(ast.arg),[('==',Const(ast.typ))])
		else: return ast