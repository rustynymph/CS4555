#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
import math
from PythonASTExtension import *
from TraverseIR import *

class FlattenTracker():
	def __init__(self,prefix,count=0):
		self.prefix = prefix
		self.count = count

	def getName(self):
		return self.prefix + "$" + str(self.count)

	def getNameAndIncrementCounter(self):
		name = self.getName()
		self.count += 1
		return name

class ArithmeticFlattener():

	def __init__(self):
		self.getTagTracker = FlattenTracker("getTag")

	def flattenArithmetic(self,ast,name,isInitial=True):
		if isinstance(ast,UnarySub):
			if not isPythonASTLeaf(ast.expr):
				flattenedExpression = [self.flattenArithmetic(ast.expr,name,isInitial)]
				assign = Assign([AssName(name,'OP_ASSIGN')],UnarySub(Name(name))) 
			else:
				flattenedExpression = [Assign([AssName(name,'OP_ASSIGN')],ast.expr)]
				assign = Assign([AssName(name,'OP_ASSIGN')],UnarySub(Name(name)))
			return Stmt(flattenedExpression + [assign])

		elif isinstance(ast,Add):
			#Flattens left sub tree
			#Checks to see if left subtree is a leaf
			if not isPythonASTLeaf(ast.left):
				#Recurses down the left subtree and returns a Stmt
				leftFlattenedExpression = self.flattenArithmetic(ast.left,name,isInitial)
			else:
				#Checks to see if name has been assigned its initial value and responses accordingly
				if isInitial: leftFlattenedExpression = Assign([AssName(name,'OP_ASSIGN')],ast.left)
				else: leftFlattenedExpression = AugAssign(Name(name),'+=',ast.left)
				# else: leftFlattenedExpression = Assign([AssName(name,'OP_ASSIGN')],Add((Name(name),ast.left)))

			#Assigning value for right name
			#Initially assigns rightName = name
			rightName = name
			#If both the right and left subtree are not leafs then append a value to avoid name clashing
			if not (isPythonASTLeaf(ast.left) or isPythonASTLeaf(ast.right)) or isinstance(ast.right,CallFunc):
				rightName = name+"$AddRight"

			#Final assignment for the tree
			assign = None
			#Checks if the tree is a leaf
			if not isPythonASTLeaf(ast.right):
				#Recurses down the right subtree and returns a Stmt
				rightFlattenedExpression = self.flattenArithmetic(ast.right,rightName,False)
				#Adds the right and left subtrees and sets it equal to name
				# assign = Assign([AssName(name,'OP_ASSIGN')],Add((Name(name),Name(rightName))))
				assign = AugAssign(Name(name),'+=',Name(rightName))
			else:
				#Adds the right leaf with name
				# rightFlattenedExpression = Assign([AssName(name,'OP_ASSIGN')],Add((Name(name),ast.right)))
				rightFlattenedExpression = AugAssign(Name(name),'+=',ast.right)

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
					stmtArray += [self.flattenArithmetic(parameter,parameterName)]
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
					stmtArray += [self.flattenArithmetic(parameter,parameterName)]
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
					stmtArray += [self.flattenArithmetic(value,valueParameterName)]
				else: valueName = value

				if not isPythonASTLeaf(key):
					keyParameterName = keyParameterPrefixName + "$" + str(i)
					keyName = Name(keyParameterName)
					stmtArray += [self.flattenArithmetic(key,keyParameterName)]
				else: keyName = key

				dictParameters += [(keyName,valueName)]

			dictionary = Dict(dictParameters)
			assign = Assign([AssName(name,'OP_ASSIGN')],dictionary)
			return Stmt(stmtArray + [assign])
		elif isinstance(ast,Subscript):
			stmtArray = []

			exprName = None
			subName = None
			if not isPythonASTLeaf(ast.expr):
				# exprStringName = name + "$sub-expr"
				exprStringName = name
				exprName = Name(exprStringName)
				stmtArray += [self.flattenArithmetic(ast.expr,exprStringName)]
			else: exprName = ast.expr

			if not isPythonASTLeaf(ast.subs[0]):
				subStringName = name + "$sub-0"
				subName = Name(subStringName)
				stmtArray += [self.flattenArithmetic(ast.subs[0],subStringName)]
			else: subName = ast.subs[0]

			subscription = Subscript(exprName,ast.flags,[subName])
			assign = Assign([AssName(name,'OP_ASSIGN')],subscription)
			return Stmt(stmtArray + [assign])
		elif isinstance(ast,IfExp):
			testName = Name(name+"$test")
			if not isinstance(ast.test,Compare):

				testExpr = self.flattenArithmetic(ast.test,name+"$test")
				isTrue = CallFunc(Name("is_true"),[testName],None,None)
				assignTest = Assign([AssName(testName.name,'OP_ASSIGN')],isTrue)
				testExpr = Stmt([testExpr,assignTest])
			else:
				exprName = Name(name+"$test$Compare$0")
				opName = Name(name+"$test$Compare$1")
				flattenExpr = self.flattenArithmetic(ast.test.expr,exprName.name)
				flattenOp = self.flattenArithmetic(ast.test.ops[0][1],opName.name)
				testExpr = Stmt([flattenExpr,flattenOp])
				testName = Compare(exprName,[('==',opName)])
			

			thenExpr = None
			if not isPythonASTLeaf(ast.then):
				thenExpr = self.flattenArithmetic(ast.then,name)
			else:
				thenExpr = Stmt([Assign([AssName(name,'OP_ASSIGN')],ast.then)])

			elseExpr = None
			if not isPythonASTLeaf(ast.else_):
				elseExpr = self.flattenArithmetic(ast.else_,name)
			else:
				elseExpr = Stmt([Assign([AssName(name,'OP_ASSIGN')],ast.else_)])

			stmtArray = []

			ifexpr = None
			if testName: 
				ifexpr = IfExp(testName,thenExpr,elseExpr)
				stmtArray += [testExpr]

			else: ifexpr = IfExp(testExpr,thenExpr,elseExpr)
			stmtArray += [ifexpr]
			return Stmt(stmtArray)


		elif isinstance(ast,Compare):
			compareNamePrefix = name + "$compare$"

			stmtArray = []

			initialComarisionExprName = Name(compareNamePrefix+str(0))
			initialComarisionExpr = ast.expr if isPythonASTLeaf(ast.expr) else self.flattenArithmetic(ast.expr,initialComarisionExprName.name)


			if not isPythonASTLeaf(initialComarisionExpr): stmtArray += [initialComarisionExpr]

			compareArray = []
			for i in range(len(ast.ops)):
				compareType = ast.ops[i][0]

				compareName = Name(compareNamePrefix + str(i+1))
				compareExpr = ast.ops[i][1] if isPythonASTLeaf(ast.ops[i][1]) else self.flattenArithmetic(ast.ops[i][1],compareName.name)

				if not isPythonASTLeaf(compareExpr):
					stmtArray += [compareExpr]
					compareArray += [(compareType,compareName)]
				else:
					compareArray += [(compareType,compareExpr)]

			compare = Compare(initialComarisionExpr if isPythonASTLeaf(initialComarisionExpr) else initialComarisionExprName, compareArray)
			assign = Assign([AssName(name,'OP_ASSIGN')],compare)
			stmtArray += [assign]
			return Stmt(stmtArray)

		elif isinstance(ast,Lambda):
			stmt = []
			if isinstance(ast.code,Stmt):
				stmt += [self.flattenArithmetic(i,name) for i in ast.code.nodes]
			else: stmt = self.flattenArithmetic(ast.code,name)
			return Lambda(ast.argnames,ast.defaults,ast.flags,stmt)
		
		elif isinstance(ast,Return): 
			
			return Return(self.flattenArithmetic(ast.value,name))	

		elif isinstance(ast,Let):
			if isinstance(ast.var,Name):
				expr = self.flattenArithmetic(ast.expr,ast.var.name)
			else:
				expr = self.flattenArithmetic(ast.expr,ast.var.expr.name)
			body = self.flattenArithmetic(ast.body,name)
			return Stmt([expr,body])

		elif isinstance(ast,InjectFrom):

			stmtArray = []

			if not isPythonASTLeaf(ast.arg):
				flattenedArg = self.flattenArithmetic(ast.arg,name)
				inject = InjectFrom(ast.typ,Name(name))
				assign = Assign([AssName(name,'OP_ASSIGN')],inject)
				stmtArray += [flattenedArg,assign]
			else:
				flattenedArg = Assign([AssName(name,'OP_ASSIGN')],ast.arg)
				inject = InjectFrom(ast.typ,Name(name))
				assign = Assign([AssName(name,'OP_ASSIGN')],inject)
				stmtArray += [flattenedArg,assign]

			return Stmt(stmtArray)

		elif isinstance(ast,ProjectTo):

			stmtArray = []
			if not isPythonASTLeaf(ast.arg):
				flattenArg = self.flattenArithmetic(ast.arg,name)
				project = ProjectTo(ast.typ,Name(name))
				assign = Assign([AssName(name,'OP_ASSIGN')],project)
				stmtArray += [flattenArg,assign]
			else:
				flattenArg = Assign([AssName(name,'OP_ASSIGN')],ast.arg)
				project = ProjectTo(ast.typ,Name(name))
				assign = Assign([AssName(name,'OP_ASSIGN')],project)
				stmtArray += [flattenArg,assign]
			return Stmt(stmtArray)

		elif isinstance(ast,Not):

			if not isPythonASTLeaf(ast.expr):
				expr = self.flattenArithmetic(ast.expr,name)
				n = Not(Name(name))
				assign = Assign([AssName(name,'OP_ASSIGN')],n)
				return Stmt([expr,assign])
			else:
				expr = Assign([AssName(name,'OP_ASSIGN')],ast.expr)
				n = Not(Name(name))
				assign = Assign([AssName(name,'OP_ASSIGN')],n)
				return Stmt([expr,assign])
		elif isinstance(ast,GetTag):
			stmtArray = []
			nameNode = Name(name)
			assign = Assign([AssName(name,'OP_ASSIGN')],ast.arg)
			getTag = GetTag(nameNode)
			return Stmt([assign,getTag])
			
		elif isinstance(ast,CreateClosure):
			fvs_stmt = self.flattenArithmetic(ast.fvs,name+"$fvs")
			nameNode = Name(name+"$fvs")
			assign1 = Assign([AssName(name,'OP_ASSIGN')],nameNode)
			return Stmt([fvs_stmt]+[assign1])

		elif isinstance(ast,GetClosure):
			fptrname = ast.name.name + '$fptr'
			fvsname = ast.name.name + '$fvs'
			assign1 = Assign([AssName(fptrname,'OP_ASSIGN')],CallFunc(Name("get_fun_ptr"),[ast.name]))
			assign2 = Assign([AssName(fvsname,'OP_ASSIGN')],CallFunc(Name("get_free_vars"),[ast.name]))
			assign3 = Assign([AssName(name,'OP_ASSIGN')],IndirectFuncCall(Name(fptrname),ast.args,Name(fvsname)))
			return Stmt([assign1,assign2,assign3])
			

		else: return Assign([AssName(name,'OP_ASSIGN')],ast)


class Flatten():
	def __init__(self):
		self.count = 0
		self.printTracker = FlattenTracker("print")
		self.returnTracker = FlattenTracker("return")
		self.subscriptionAssignTracker = FlattenTracker("subscription")
		self.arithmeticFlattener = ArithmeticFlattener()

	@staticmethod
	def removeNestedStmtMap(ast):
		if isinstance(ast,Stmt):
			stmtArray = []
			for expr in ast.nodes:
				stmtArray += expr.nodes if isinstance(expr,Stmt) else [expr]
			return Stmt(stmtArray)
		else: return ast

	def flattenMap(self,ast):
		if isinstance(ast,Assign) and isinstance(ast.nodes[0],AssName):
			return self.arithmeticFlattener.flattenArithmetic(ast.expr,ast.nodes[0].name)
		elif isinstance(ast,Assign) and isinstance(ast.nodes[0],Subscript):
			subscription = ast.nodes[0]
			subscriptionPrefix = self.subscriptionAssignTracker.getNameAndIncrementCounter()
			subscriptStmtArray = []
			if not isPythonASTLeaf(subscription.expr):
				pyobjName = Name(subscriptionPrefix+"$pyobj")
				pyobjStmt = self.arithmeticFlattener.flattenArithmetic(subscription.expr,pyobjName.name)
				subscriptStmtArray += [pyobjStmt]
			else: pyobjName = subscription.expr

			if not isPythonASTLeaf(subscription.subs[0]):
				subName = Name(subscriptionPrefix+"$sub-0")
				subStmt = self.arithmeticFlattener.flattenArithmetic(subscription.subs[0],subName.name)
				subscriptStmtArray += [subStmt]
			else: subName = subscription.subs[0]

			newSubscription = Subscript(pyobjName,subscription.flags,[subName])

			assignStmtArray = []
			if not isPythonASTLeaf(ast.expr):
				assignExprName = Name(subscriptionPrefix+"$value")
				assignStmt = self.arithmeticFlattener.flattenArithmetic(ast.expr,assignExprName.name)
				assignStmtArray += [assignStmt]
			else: assignExprName = ast.expr

			assign = Assign([newSubscription],assignExprName)
			stmtArray = subscriptStmtArray + assignStmtArray + [assign]

			return Stmt(stmtArray)

		elif isinstance(ast,Printnl):
			name = self.printTracker.getNameAndIncrementCounter()
			if not isPythonASTLeaf(ast.nodes[0]):
				printStmt = self.arithmeticFlattener.flattenArithmetic(ast.nodes[0],name)
				assign = Printnl([Name(name)],None)
				cluster = [printStmt,assign]
			else: cluster = [Printnl([ast.nodes[0]],None)]
			return Stmt(cluster)
			
		elif isinstance(ast,Return):
			name = self.returnTracker.getNameAndIncrementCounter()
			if not isPythonASTLeaf(ast.value):
				returnStmt = self.arithmeticFlattener.flattenArithmetic(ast.value,name)
				assign = Return(Name(name))
				cluster = [returnStmt,assign]
			else: cluster = [Return(ast.value)]
			return Stmt(cluster)
		

			
		#elif isinstance(ast,Function):
		
		else: return ast

	@staticmethod
	def removeUnnecessaryStmt(ast):
		if isinstance(ast,Module):
			if not isinstance(ast.node,Stmt):
				return Module(ast.doc,Stmt([ast.node]))
			else: return ast
		elif isinstance(ast,Stmt) and len(ast.nodes) == 1: return ast.nodes[0]

		else: return ast






