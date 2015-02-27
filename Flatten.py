#!/usr/bin/python

from compiler.ast import *
import compiler
import sys
import string
import math
from PythonASTExtension import *

class flat_stmt(Stmt):
	def __init__(self, nodes):
		Stmt.__init__(self, nodes)

class save_nodes(Stmt):
	def __init__(self, nodes):
		Stmt.__init__(self, nodes)

class python_compiler:
    
	flat_stmt.nodes = []
	save_nodes.nodes = []
    
	@staticmethod
	def yesAppend(tmp_num,new_stmt):
		if isinstance(new_stmt,Assign) or isinstance(new_stmt,Name) or isinstance(new_stmt,Const) or isinstance(new_stmt,Boolean) or isinstance(new_stmt,IfExp) or isinstance(new_stmt,And) or isinstance(new_stmt,Or) or isinstance(new_stmt,Compare) or isinstance(new_stmt,Subscript) or isinstance(new_stmt,List) or isinstance(new_stmt,Dict) or isinstance(new_stmt,CallFunc) or isinstance(new_stmt,Add) or isinstance(new_stmt,UnarySub):
			flat_stmt.nodes.append(new_stmt)
			return (tmp_num,new_stmt)
		else:		
			flat_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return tmp_num
		
	@staticmethod
	def noAppend(tmp_num,new_stmt):
		if isinstance(new_stmt,Assign) or isinstance(new_stmt,Name) or isinstance(new_stmt,Const) or isinstance(new_stmt,Boolean) or isinstance(new_stmt,IfExp) or isinstance(new_stmt,And) or isinstance(new_stmt,Or) or isinstance(new_stmt,Compare) or isinstance(new_stmt,Subscript) or isinstance(new_stmt,List) or isinstance(new_stmt,Dict) or isinstance(new_stmt,CallFunc) or isinstance(new_stmt,Add) or isinstance(new_stmt,UnarySub):
			return (tmp_num,new_stmt)
		else:
			new_stmt = compiler.parse(new_stmt).node.nodes[0]
			save_nodes.nodes.append(new_stmt)			
			return (tmp_num,new_stmt)					
    
	@staticmethod
	def treeFlatten(ast):
		python_compiler.treeFlatten_helper(ast, 0)
		ast2 = Module(None, Stmt(flat_stmt.nodes))
		return ast2

	@staticmethod
	def treeFlatten_helper(ast, tmp_num,append=True):
        
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
			if (append == True): return python_compiler.yesAppend(right_val,new_stmt)
			else: return python_compiler.noAppend(rightval,new_stmt)

		elif isinstance(ast, Add):
			left_val = python_compiler.treeFlatten_helper(ast.left, tmp_num)
			right_val = python_compiler.treeFlatten_helper(ast.right, left_val + 1)
			new_stmt = 'tmp' + str(right_val + 1) + ' = tmp' + str(left_val) + ' + tmp' + str(right_val)
			if (append == True): return python_compiler.yesAppend(right_val+1,new_stmt)
			else: return python_compiler.noAppend(right_val+1,new_stmt)		

		elif isinstance(ast, UnarySub):
			neg_var = python_compiler.treeFlatten_helper(ast.expr, tmp_num)
			new_stmt = 'tmp' + str(neg_var + 1) + ' = -tmp' + str(neg_var)
			if (append == True): return python_compiler.yesAppend(neg_var+1,new_stmt)
			else: return python_compiler.noAppend(neg_var+1,new_stmt)
			
		elif isinstance(ast, CallFunc):
			temp = 'tmp' + str(tmp_num)
			name_func = Name(ast.node)
			new_stmt = Assign([AssName(temp, 'OP_ASSIGN')], CallFunc(name_func,[],None,None))
			if (append == True): return python_compiler.yesAppend(tmp_num,new_stmt)
			else: return python_compiler.noAppend(tmp_num,new_stmt)				
                
		elif isinstance(ast, Name):
			ast.name = "__"+ast.name
			new_stmt = 'tmp' + str(tmp_num) + ' = ' + ast.name
			if (append == True): return python_compiler.yesAppend(tmp_num,new_stmt)
			else: return python_compiler.noAppend(tmp_num,new_stmt)	

		elif isinstance(ast, Const):
			new_stmt = 'tmp' + str(tmp_num) + ' = ' + str(ast.value)
			if (append == True): return python_compiler.yesAppend(tmp_num,new_stmt)
			else: return python_compiler.noAppend(tmp_num,new_stmt)

		elif isinstance(ast,Compare):
			expr_val = python_compiler.treeFlatten_helper(ast.expr,tmp_num)
			op_val = python_compiler.treeFlatten_helper(ast.ops[1],expr_val+1)
			new_stmt = 'tmp'+str(op_val+1) + ' = ' 'tmp'+str(expr_val) + ' ' + str(ast.ops[0]) + ' ' + 'tmp'+str(op_val)		
			if (append==True): return python_compiler.yesAppend(op_val+1,new_stmt)
			else: return python_compiler.noAppend(op_val+1,new_stmt)

		elif isinstance(ast,Or):
			left = python_compiler.treeFlatten_helper(ast.nodes[0],tmp_num)
			right = python_compiler.treeFlatten_helper(ast.nodes[1],left+1)
			new_stmt = 'tmp'+str(right+1) + ' = ' + 'tmp'+str(left) + ' or ' + 'tmp'+str(right)		
			if (append==True): return python_compiler.yesAppend(right+1,new_stmt)
			else: return python_compiler.noAppend(right+1,new_stmt)			
		
		elif isinstance(ast,And):
			left = python_compiler.treeFlatten_helper(ast.nodes[0],tmp_num)
			right = python_compiler.treeFlatten_helper(ast.nodes[1],left+1)
			new_stmt = 'tmp'+str(right+1) + ' = ' + 'tmp'+str(left) + ' and ' + 'tmp'+str(right)
			if (append==True): return python_compiler.yesAppend(right+1,new_stmt)
			else: return python_compiler.noAppend(right+1,new_stmt)

		elif isinstance(ast,Not):
			not_var = python_compiler.treeFlatten_helper(ast.expr, tmp_num)
			new_stmt = 'tmp' + str(not_var + 1) + ' = not(tmp' + str(not_var)+')'			
			if (append==True): return python_compiler.yesAppend(not_var+1,new_stmt)
			else: return python_compiler.noAppend(not_var+1,new_stmt)

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
			if (append==True): return python_compiler.yesAppend(tmp_num,new_stmt)
			else: return python_compiler.noAppend(tmp_num,new_stmt)
			
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
				if(append==True): return python_compiler.yesAppend(new_val+1,new_stmt)
				else: return python_compiler.noAppend(new_val+1,new_stmt)
			else:
				new_val = python_compiler.treeFlatten_helper(ast.items[length-1][1],tmp_num)
				if isinstance(ast.items[length-1][0],Const):
					new_stmt += str(ast.items[length-1][0].value) + ':' + 'tmp'+str(new_val) + '}'
				if isinstance(ast.items[length-1][0],Name):
					new_stmt += str(ast.items[length-1][0].name) + ':' + 'tmp'+str(new_val) + '}'
				if(append==True): return python_compiler.yesAppend(new_val+1,new_stmt)
				else: return python_compiler.noAppend(new_val+1,new_stmt)
			
		elif isinstance(ast,Subscript):
			new_tmp = 'tmp'+str(tmp_num)
			if(append==True):
				flat_stmt.nodes.append(Assign([AssName(new_tmp, 'OP_ASSIGN')], Subscript(ast.expr, ast.flags, [ast.subs[0]])))
				return tmp_num+1
			else:
				new_stmt = Assign([AssName(new_tmp, 'OP_ASSIGN')], Subscript(ast.expr, ast.flags, [ast.subs[0]]))
				return (tmp_num+1,new_stmt)
		
			
		elif isinstance(ast,IfExp):

			def IfExpRecursion(ast,tmp_number):			
				test_var = python_compiler.treeFlatten_helper(ast.test, tmp_num,True)
				test_tmp = 'tmp'+str(test_var)
				
				print ast.then
				new_then = python_compiler.treeFlatten_helper(ast.then,test_var+1,False)
				then_exp = new_then[1]
				save_nodes.nodes +=then_exp	
				print then_exp

				if isinstance(ast.else_,IfExp):
					return IfExp(Name(test_tmp),[i for i in save_nodes.nodes],IfExpRecursion(ast.else_, test_var+1))
				else:
					new_else = python_compiler.treeFlatten_helper(ast.else_,test_var+1,False)
					else_exp = new_else[1]
					return IfExp(Name(test_tmp),then_exp,else_exp)


		
			result = IfExpRecursion(ast,tmp_num)
			print("result is:")
			print result
			#new_stmt = 	result[0]
			#num = result[1]
			return num


		elif isinstance(ast,InjectFrom):
			tmp = 'tmp'+str(tmp_num)
			new_stmt = Assign([AssName(tmp, 'OP_ASSIGN')], ast)
			save_nodes.nodes.append(new_stmt)
			if(append==True):
				flat_stmt.nodes.append(new_stmt)		
				return tmp_num
			else:
				return (tmp_num,new_stmt)
        
		elif isinstance(ast,ProjectTo):
			tmp = 'tmp'+str(tmp_num)
			new_stmt = Assign([AssName(tmp, 'OP_ASSIGN')], ast)
			save_nodes.nodes.append(new_stmt)
			if(append==True):
				flat_stmt.nodes.append(new_stmt)		
				return tmp_num
			else:
				return (tmp_num,new_stmt)
		
		elif isinstance(ast,GetTag):
			tmp = 'tmp'+str(tmp_num)
			new_stmt = Assign([AssName(tmp, 'OP_ASSIGN')], ast)
			save_nodes.nodes.append(new_stmt)
			if(append==True):
				flat_stmt.nodes.append(new_stmt)		
				return tmp_num
			else:
				return (tmp_num,new_stmt)
		
		elif isinstance(ast,IsTag):
			tmp = 'tmp'+str(tmp_num)
			new_stmt = Assign([AssName(tmp, 'OP_ASSIGN')], ast)
			save_nodes.nodes.append(new_stmt)
			if(append==True):
				flat_stmt.nodes.append(new_stmt)		
				return tmp_num
			else:
				return (tmp_num,new_stmt)
        
            
		else:
			raise Exception("Error: Unrecognized node type")
			
