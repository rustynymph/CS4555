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
	
counter = 1
tmp_nummy = 0
	
class python_compiler:
    
	flat_stmt.nodes = []
	save_nodes.nodes = []
	environment = {}

	@staticmethod
	def gen_count_number():
		global counter
		number = str(counter)
		counter += 1
		return number
	
	@staticmethod
	def create_new_name(name):
		new_name = "new" + "_" + python_compiler.gen_count_number() + "_" + name
		return new_name

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
		ast2 = (Module(None, Stmt(flat_stmt.nodes)),python_compiler.environment)
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
			if isinstance(print_var,Name):
				new_stmt = Printnl([print_var],None)
				flat_stmt.nodes.append(new_stmt)
				return print_var
			else:
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
					
			varName = ast.nodes[0].name
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
			ast.name = ast.name
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
			save_nodes.nodes.append(compiler.parse(new_stmt).node.nodes[0])		
			if (append==True): return python_compiler.yesAppend(right+1,new_stmt)
			else: return python_compiler.noAppend(right+1,new_stmt)			
		
		elif isinstance(ast,And):
			left = python_compiler.treeFlatten_helper(ast.nodes[0],tmp_num)
			right = python_compiler.treeFlatten_helper(ast.nodes[1],left+1)
			new_stmt = 'tmp'+str(right+1) + ' = ' + 'tmp'+str(left) + ' and ' + 'tmp'+str(right)
			save_nodes.nodes.append(compiler.parse(new_stmt).node.nodes[0])			
			if (append==True): return python_compiler.yesAppend(right+1,new_stmt)
			else: return python_compiler.noAppend(right+1,new_stmt)

		elif isinstance(ast,Not):
			not_var = python_compiler.treeFlatten_helper(ast.expr, tmp_num)
			new_stmt = 'tmp' + str(not_var + 1) + ' = not(tmp' + str(not_var)+')'
			save_nodes.nodes.append(compiler.parse(new_stmt).node.nodes[0])						
			if (append==True): return python_compiler.yesAppend(not_var+1,new_stmt)
			else: return python_compiler.noAppend(not_var+1,new_stmt)

		elif isinstance(ast, List):
			str_nodes = ''
			length = len(ast.nodes)
			if length > 1:
				for x in range(0,length-1):
					lala = python_compiler.treeFlatten_helper(ast.nodes[x],tmp_num)
					str_nodes += 'tmp'+str(lala)
					str_nodes += ','
					tmp_num = lala+1
				lala = python_compiler.treeFlatten_helper(ast.nodes[length-1],tmp_num)
				str_nodes += 'tmp'+str(lala)
			else:
				str_nodes = str(ast.nodes[0])

			#new_stmt = 'tmp'+str(tmp_num) + ' = ' + '[' + str(str_nodes) + ']'
			new_tmp = 'tmp'+str(tmp_num+1)
			new_stmt = Assign([AssName(new_tmp, 'OP_ASSIGN')], List([str_nodes]))
			#if (append==True): return python_compiler.yesAppend(tmp_num,new_stmt)
			#else: return python_compiler.noAppend(tmp_num,new_stmt)
			if (append==True):
				flat_stmt.nodes.append(new_stmt)
				return tmp_num+1
			else: return (tmp_num+1,new_stmt)
			
			
		elif isinstance(ast,Dict):
			new_dict = {}
			for item in ast.items:
				new_val = python_compiler.treeFlatten_helper(item[1],tmp_num)
				new_key = python_compiler.treeFlatten_helper(item[0],new_val+1)
				tmp_num = new_key+1
				tmp_key = 'tmp'+str(new_key)
				tmp_val = 'tmp'+str(new_val)
				new_dict[tmp_key]=tmp_val
			new_stmt = 'tmp'+str(tmp_num) + ' = ' + str(new_dict)
			if(append==True):
				return python_compiler.yesAppend(new_val+1,new_stmt)
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
			final_tmp = Name(python_compiler.create_new_name('temp'))			
			if isinstance(ast.test,Name):
				test_name = ast.test
			else:
				test_name_var = python_compiler.treeFlatten_helper(ast.test,tmp_num,True)
				test_name = 'tmp'+str(test_name_var)
				tmp_num = test_name_var+1
			
			save_nodes.nodes = []
			then_tuple = python_compiler.treeFlatten_helper(ast.then,tmp_num,False)
			then_var = then_tuple[0]
			then_tmp = 'tmp'+str(then_var)
			save_nodes.nodes += Assign([AssName(final_tmp, 'OP_ASSIGN')],Name(then_tmp))
			
			if isinstance(ast.else_,IfExp):
				IfExpRecursion()
			else:
				if isinstance(ast.else_,Name):
					final_assign = [Assign([AssName(final_tmp, 'OP_ASSIGN')],ast.else_)]
					result = IfExp(test_name,save_nodes.nodes,final_assign)
					flat_stmt.nodes.append(result)	
				else:
					save_then_nodes = save_nodes.nodes
					save_nodes.nodes = []
					else_tuple = python_compiler.treeFlatten_helper(ast.else_,tmp_num,False)
					else_var = else_tuple[0]
					else_tmp = 'tmp'+str(else_var)
					save_nodes.nodes += Assign([AssName(final_tmp, 'OP_ASSIGN')],Name(else_tmp))
					result = IfExp(test_name,save_then_nodes,save_nodes.nodes)
					flat_stmt.nodes.append(result)
			return final_tmp
			
			
			#print("made it")

			def IfExpRecursion(ast,tmp_number):			
				test_var = python_compiler.treeFlatten_helper(ast.test, tmp_num,True)
				test_tmp = 'tmp'+str(test_var)
				
				new_then = python_compiler.treeFlatten_helper(ast.then,test_var+1,False)
				then_exp = new_then[1]
				print then_exp
				ast.then = then_exp
				save_nodes.nodes +=then_exp	

				if isinstance(ast.else_,IfExp):
					if_exp_recur = IfExp(Name(test_tmp),ast.then,IfExpRecursion(ast.else_, test_var+1))
				else:
					new_else = python_compiler.treeFlatten_helper(ast.else_,test_var+1,False)
					else_exp = new_else[1]
					tmp_nummy = new_else[0]
					return flat_stmt.nodes.append(IfExp(Name(test_tmp),ast.then,else_exp))
			
			#if isinstance(ast.test,Name):
			#	test_tmp = ast.test
			#else:
			#	test_var = python_compiler.treeFlatten_helper(ast.test, tmp_num,True)
			#	tmp_num = test_var
			#	test_tmp = 'tmp'+str(tmp_num)
			#	test_tmp = Name(test_tmp)
			#save_nodes.nodes=[]
			#new_then = python_compiler.treeFlatten_helper(ast.then,tmp_num+1,False)
			#result = IfExp(test_tmp,save_nodes.nodes,IfExpRecursion(ast,tmp_num))
			#print("=====result=====")
			#print result
			#return tmp_nummy+1

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
        
		elif isinstance(ast,Let):
			let_name = ast.var
			let_value = ast.rhs
			if isinstance(ast.rhs,Let):
				let_var = python_compiler.treeFlatten_helper(ast.rhs,tmp_num,True)
				let_tmp = 'tmp'+str(let_var)
				#new_stmt = Assign([AssName(ast.var, 'OP_ASSIGN')],let_tmp)
				new_body = python_compiler.treeFlatten_helper(ast.rhs.body,let_var+1,True)
				new_let_tmp = 'tmp'+str(let_var+1)
				if isinstance(new_body,Name):
					new_stmt2 = Assign([AssName(Name(new_let_tmp), 'OP_ASSIGN')],new_body)
					save_nodes.nodes.append(new_stmt2)
					if append==True:
						flat_stmt.nodes.append(new_stmt2)
						return new_body
					else:
						return (new_body,new_stmt2)
				else:
					body_tmp = 'tmp'+str(new_body)
					new_stmt2 = Assign([AssName(Name(new_let_tmp), 'OP_ASSIGN')],Name(body_tmp))
					save_nodes.nodes.append(new_stmt2)
					if append==True:
						flat_stmt.nodes.append(new_stmt2)
						return new_body
					else:
						return (new_body,new_stmt2)
			else:
				python_compiler.environment[let_name] = let_value
				let_var = python_compiler.treeFlatten_helper(let_value,tmp_num,True)
				let_tmp = 'tmp'+str(let_var)			
				new_stmt = Assign([AssName(let_name, 'OP_ASSIGN')],let_tmp)
				save_nodes.nodes.append(new_stmt)
				if append==True:
					flat_stmt.nodes.append(new_stmt)
					return let_var
				else:
					return (let_var,new_stmt)				

			#if isinstance(ast.body,Let):
			#	new_let_body = python_compiler.treeFlatten_helper(ast.body,let_var,False)
			#body = python_compiler.treeFlatten_helper(ast.body,let_var+1,True)
			#name_var = python_compiler.treeFlatten_helper(let_name,tmp_num,True)

			#print("hey")
			#new_stmt = Assign([AssName(let_name, 'OP_ASSIGN')],let_tmp)
			#if append==True:
			#	flat_stmt.nodes.append(new_stmt)
			#	return let_var
			#else:
			#	return (let_var,new_stmt)
			
			#python_compiler.environment[let_name] = let_value #keeps a mapping from all names to values
			#body_tmp =  python_compiler.treeFlatten_helper(ast.body,tmp_num,True)
			#print("poop")
			#print body		
			
		else:
			raise Exception("Error: Unrecognized node type")
			
