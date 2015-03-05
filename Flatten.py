#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
import math
from PythonASTExtension import *
from TraverseIR import *

class ArithmeticFlattener():

	@staticmethod
	def isFlattenedLeaf(ast):
		return isPythonASTLeaf(ast)

	@staticmethod
	def flattenArithmetic(ast,name,isInitial=True):
		# if ArithmeticFlattener.isFlattenedLeaf(ast):
		# 	if isInitial: return Stmt([Assign([AssName(name,'OP_ASSIGN')],ast)])
		# 	else: return Stmt([Assign([AssName(name,'OP_ASSIGN')],)])
		if isinstance(ast,UnarySub):
			if not ArithmeticFlattener.isFlattenedLeaf(ast.expr):
				flattenedExpression = [ArithmeticFlattener.flattenArithmetic(ast.expr,name,isInitial)]
				assign = Assign([AssName(name,'OP_ASSIGN')],UnarySub(Name(name))) 
			else:
				flattenedExpression = []
				assign = Assign([AssName(name,'OP_ASSIGN')],UnarySub(ast.expr))
			return Stmt(flattenedExpression + [assign])

		elif isinstance(ast,Add):
			#Flattens left sub tree
			#Checks to see if left subtree is a leaf
			if not ArithmeticFlattener.isFlattenedLeaf(ast.left):
				#Recurses down the left subtree and returns a Stmt
				leftFlattenedExpression = ArithmeticFlattener.flattenArithmetic(ast.left,name,isInitial)
			else:
				#Checks to see if name has been assigned its initial value and responses accordingly
				if isInitial: leftFlattenedExpression = Assign([AssName(name,'OP_ASSIGN')],ast.left)
				else: leftFlattenedExpression = Assign([AssName(name,'OP_ASSIGN')],Add((Name(name),ast.left)))

			#Assigning value for right name
			#Initially assigns rightName = name
			rightName = name
			#If both the right and left subtree are not leafs then append a value to avoid name clashing
			if not (ArithmeticFlattener.isFlattenedLeaf(ast.left) or ArithmeticFlattener.isFlattenedLeaf(ast.right)):
				rightName = name+"$AddRight"

			#Final assignment for the tree
			assign = None
			#Checks if the tree is a leaf
			if not ArithmeticFlattener.isFlattenedLeaf(ast.right):
				#Recurses down the right subtree and returns a Stmt
				rightFlattenedExpression = ArithmeticFlattener.flattenArithmetic(ast.right,rightName,False)
				#Adds the right and left subtrees and sets it equal to name
				assign = Assign([AssName(name,'OP_ASSIGN')],Add((Name(name),Name(rightName))))
			else:
				#Adds the right leaf with name
				rightFlattenedExpression = Assign([AssName(name,'OP_ASSIGN')],Add((Name(name),ast.right)))

			#Creates a list for a Stmt node
			stmtArray = [leftFlattenedExpression,rightFlattenedExpression]
			#If assign was assigned add it to the stmtArray
			if assign: stmtArray += [assign]
			#Return Stmt
			return Stmt(stmtArray)
		elif isinstance(ast,CallFunc):
			stmtArray = []
			functionParameters = []

			parameterPrefixName = name + "$" + ast.node.name
			for i in range(len(ast.args)):
				parameter = ast.args[i]
				if not isPythonASTLeaf(parameter):
					parameterName = parameterPrefixName + "$" +str(i)
					functionParameters += [Name(parameterName)]
					stmtArray += [ArithmeticFlattener.flattenArithmetic(parameter,parameterName)]
				else: functionParameters += [parameter]
			assign = Assign([AssName(name,'OP_ASSIGN')],CallFunc(ast.node,functionParameters))
			return Stmt(stmtArray + [assign])

		elif isinstance(ast,List):
			stmtArray = []
			listParameters = []

			parameterPrefixName = name
			for i in range(len(ast.nodes)):
				parameter = ast.nodes[i]
				if not isPythonASTLeaf(parameter):
					parameterName = parameterPrefixName + "$" + str(i)
					listParameters += [Name(parameterName)]
					stmtArray += [ArithmeticFlattener.flattenArithmetic(parameter,parameterName)]
				else: listParameters += [parameter]

			assign = Assign([AssName(name,'OP_ASSIGN')],List(listParameters))
			return Stmt(stmtArray + [assign])

		elif isinstance(ast,Dict):
			stmtArray = []
			dictParameters = []

			parameterPrefixName = name
			valueParameterPrefixName = parameterPrefixName + "$value"
			keyParameterPrefixName = parameterPrefixName + "$key"
			for i in range(len(ast.items)):
				keyValuePair = ast.items[i]
				key = keyValuePair[0]
				value = keyValuePair[1]

				valueName = None
				keyName = None
				if not isPythonASTLeaf(value):
					valueParameterName = valueParameterPrefixName + "$" + str(i)
					valueName = Name(valueParameterName)
					stmtArray += [ArithmeticFlattener.flattenArithmetic(value,valueParameterName)]
				else: valueName = value

				if not isPythonASTLeaf(key):
					keyParameterName = keyParameterPrefixName + "$" + str(i)
					keyName = Name(keyParameterName)
					stmtArray += [ArithmeticFlattener.flattenArithmetic(key,keyParameterName)]
				else: keyName = key

				dictParameters += [(keyName,valueName)]
			dictionary = Dict(dictParameters)
			return Stmt(stmtArray + [dictionary])

		else: return ast

class PrintFlattener():
	def __init__(self,name,count=0):
		self.name = name
		self.count = count


class Flatten():
	def __init__(self):
		self.count = 0

	def getAndIncrement(self):
		count = self.count
		self.count += 1
		return count

	def flattenMap(self,ast):
		if isinstance(ast,Assign):
			return ArithmeticFlattener.flattenArithmetic(ast.expr,ast.nodes[0].name)
		elif isinstance(ast,Printnl):
			print "hello"
		else: return ast