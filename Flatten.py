#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
import math

class flat_stmt(Stmt):
	def __init__(self, nodes):
		Stmt.__init__(self, nodes)

class python_compiler:
    
	flat_stmt.nodes = []
    
	@staticmethod
	def treeFlatten(ast):
		python_compiler.treeFlatten_helper(ast, 0)
		ast2 = Module(None, Stmt(flat_stmt.nodes))
		return ast2

	@staticmethod
	def treeFlatten_helper(ast, tmp_num):
        
		if isinstance(ast, Module):
			python_compiler.treeFlatten_helper(ast.node, tmp_num)
			return 0

		elif isinstance(ast, Stmt):
			for node in ast.nodes:
				length = len(flat_stmt.nodes)
				tmp_num = length
				python_compiler.treeFlatten_helper(node, tmp_num)
			return tmp_num
			
		elif isinstance(ast, Printnl):
			print_var = python_compiler.treeFlatten_helper(ast.nodes[0], tmp_num)
			new_stmt = 'print tmp' + str(print_var)
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return print_var

		elif isinstance(ast, Discard):
			python_compiler.treeFlatten_helper(ast.expr, tmp_num)
			return tmp_num

		elif isinstance(ast, Assign):
			if isinstance(ast.expr,Name):
				if ast.nodes[0].name == ast.expr.name:
					return tmp_num
					
			varName = "__"+ast.nodes[0].name
			right_val = python_compiler.treeFlatten_helper(ast.expr, tmp_num)

			new_stmt = varName + ' = tmp' + str(right_val)
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return right_val

		elif isinstance(ast, Add):
			# recurse down BOTH sides of tree
			left_val = python_compiler.treeFlatten_helper(ast.left, tmp_num)
			right_val = python_compiler.treeFlatten_helper(ast.right, left_val + 1)
			new_stmt = 'tmp' + str(right_val + 1) + ' = tmp' + str(left_val) + ' + tmp' + str(right_val)
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return right_val + 1

		elif isinstance(ast, UnarySub):
			neg_var = python_compiler.treeFlatten_helper(ast.expr, tmp_num)
			new_stmt = 'tmp' + str(neg_var + 1) + ' = -tmp' + str(neg_var)
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return neg_var + 1
			
        # CallFunc, Name, and Const are base cases
		elif isinstance(ast, CallFunc):
			new_stmt = 'tmp' + str(tmp_num) + ' = input()'
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return tmp_num
                
		elif isinstance(ast, Name):
			ast.name = "__"+ast.name
			new_stmt = 'tmp' + str(tmp_num) + ' = ' + ast.name
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return tmp_num

		elif isinstance(ast, Const):
			new_stmt = 'tmp' + str(tmp_num) + ' = ' + str(ast.value)
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return tmp_num

		elif isinstance(ast,Compare):
			length = len(ast.ops)
			expr_val = python_compiler.treeFlatten_helper(ast.expr,tmp_num)
			new_stmt = 'tmp'+str(tmp_num) + ' = ' + 'tmp'+str(expr_val) + ' '
			for x in ast.ops:
				new_val = python_compiler.treeFlatten_helper(x[1],tmp_num)
				tmp_num = new_val+1
				new_stmt += str(x[0]) + ' ' + 'tmp'+str(new_val)
			flat_stmt.nodes.append(compiler.parse(new_stmt))
			return new_val + 1

		elif isinstance(ast,Or):
			length = len(ast.nodes)
			new_stmt = ''
			if length>2:
				for x in range (0,length-1):
					new_val = python_compiler.treeFlatten_helper(ast.nodes[x],tmp_num)
					tmp_num=new_val+1
					new_stmt += 'tmp'+str(new_val) + ' or '
				new_val = python_compiler.treeFlatten_helper(ast.nodes[length-1],tmp_num)
				new_stmt += 'tmp'+str(new_val)
				flat_stmt.nodes.append(compiler.parse(new_stmt))
				return new_val+1
			else:			
				left = python_compiler.treeFlatten_helper(ast.nodes[0],tmp_num)
				right = python_compiler.treeFlatten_helper(ast.nodes[1],left+1)
				new_stmt = 'tmp'+str(left) + ' or ' + 'tmp'+str(right) 
				flat_stmt.nodes.append(compiler.parse(new_stmt))
				return right + 1
		
		elif isinstance(ast,And):
			length = len(ast.nodes)
			new_stmt = ''
			if length>2:
				for x in range (0,length-1):
					new_val = python_compiler.treeFlatten_helper(ast.nodes[x],tmp_num)
					tmp_num=new_val+1
					new_stmt += 'tmp'+str(new_val) + ' and '
				new_val = python_compiler.treeFlatten_helper(ast.nodes[length-1],tmp_num)
				new_stmt += 'tmp'+str(new_val)
				flat_stmt.nodes.append(compiler.parse(new_stmt))
				return new_val+1
			else:			
				left = python_compiler.treeFlatten_helper(ast.nodes[0],tmp_num)
				right = python_compiler.treeFlatten_helper(ast.nodes[1],left+1)
				new_stmt = 'tmp'+str(left) + ' and ' + 'tmp'+str(right) 
				flat_stmt.nodes.append(compiler.parse(new_stmt))
				return right + 1

		elif isinstance(ast,Not):
			not_var = python_compiler.treeFlatten_helper(ast.expr, tmp_num)
			new_stmt = 'tmp' + str(not_var + 1) + ' = not(tmp' + str(not_var)+')'
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return not_var + 1

		elif isinstance(ast, List):
			str_nodes = ''
			length = len(ast.nodes)
			if length > 1:
				for x in range(0,length-1):
					str_nodes += str(ast.nodes[x].value)
					str_nodes += ','
				str_nodes += str(ast.nodes[length-1].value)
			else:
				str_nodes = str(ast.nodes[0].value)

			new_stmt = 'tmp'+str(tmp_num) + ' = ' + '[' + str(str_nodes) + ']'
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0].expr)
			return tmp_num
			
		elif isinstance(ast,Dict):
			values = []
			new_stmt = 'tmp'+str(tmp_num)+ ' = ' + '{'
			length = len(ast.items)
			if length > 1:
				for x in range (0,length-1):
					new_val = python_compiler.treeFlatten_helper(ast.items[x][1],tmp_num)
					tmp_num += 1
					if isinstance(ast.items[x][0], Const):
						new_stmt += str(ast.items[x][0].value) + ':' + 'tmp'+str(new_val) + ','
					if isinstance(ast.items[x][0], Name):
						new_stmt += str(ast.items[x][0].name) + ':' + 'tmp'+str(new_val) + ','
				new_val = python_compiler.treeFlatten_helper(ast.items[length-1][1],tmp_num)
				if isinstance(ast.items[length-1][0], Const):
					new_stmt += str(ast.items[length-1][0].value) + ':' + 'tmp'+str(new_val) + '}'
				if isinstance(ast.items[length-1][0], Name):
					new_stmt += str(ast.items[length-1][0].name) + ':' + 'tmp'+str(new_val) + '}'
				flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0].expr)
				return new_val+1
			else:
				new_val = python_compiler.treeFlatten_helper(ast.items[length-1][1],tmp_num)
				if isinstance(ast.items[length-1][0],Const):
					new_stmt += str(ast.items[length-1][0].value) + ':' + 'tmp'+str(new_val) + '}'
				if isinstance(ast.items[length-1][0],Name):
					new_stmt += str(ast.items[length-1][0].name) + ':' + 'tmp'+str(new_val) + '}'
				flat_stmt.nodes.append(compiler.parse(new_stmt).expr)
				return new_val+1
			
		elif isinstance(ast,Subscript):
			list_val = python_compiler.treeFlatten_helper(ast.expr)
			new_list = 'tmp'+str(list_val)
			length = len(ast.subs)
			if length>1:
				sub = Subscript(new_list, ast.subs[0])
				for x in range(1,length):
					new_sub = Subscript(sub,ast.subs[x])
					sub = new_sub
				flat_stmt.nodes.append(Assign([AssName(new_tmp, 'OP_ASSIGN')], new_sub))
			else:
				flat_stmt.nodes.append(Assign([AssName(new_tmp, 'OP_ASSIGN')], Subscript(new_list, 'OP_APPLY', [ast.subs[0]])))
			return list_val+1
			
		elif isinstance(ast,IfExp):
			test_var = python_compiler.treeFlatten_helper(ast.test, tmp_num)
			new_var = test_var + 1
			then_var = python_compiler.treeFlatten_helper(ast.then, new_var + 1)
			else_var = python_compiler.treeFlatten_helper(ast.else_, then_var + 1)
			
			new_tmp = 'tmp'+str(new_var)
			test_tmp = 'tmp'+str(test_var)
			then_tmp = 'tmp'+str(then_var)
			else_tmp = 'tmp'+str(else_var)
			
			new_stmt = IfExp(Name(test_tmp),Assign([AssName(new_tmp, 'OP_ASSIGN')], then_tmp), Assign([AssName(new_tmp, 'OP_ASSIGN')], else_tmp))
			
			flat_stmt.nodes.append(new_stmt)
			return else_var
            
		else:
			raise Exception("Error: Unrecognized node type")
			
