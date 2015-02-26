#!/usr/bin/python
class exp_stmt(Stmt):
	def __init__(self, nodes):
		Stmt.__init__(self, nodes)

class Explicate:
	
	exp_stmt.nodes = []
	
	#for name nodes, which includes variable names AND booleans
	def explicateName(ast):
		if(ast.name == "True"):
			return InjectFrom(BOOL_t, Const(1))
		elif(ast.name == "False"):
			return InjectFrom(BOOL_t, Const(0))
		else: return Name(ast.name)

	@staticmethod
	def explicateBinary(ast):
		if isinstance(ast,Add):
			lhsvar = ast.left
			rhsvar = ast.right			
			explicated = Let(lhsvar,Let(rhsvar,IfExp(And([Or([IsTag(INT_t,lhsvar),
				   IsTag(BOOL_t, lhsvar)]),
			   Or([IsTag(INT_t, rhsvar),
				   IsTag(BOOL_t, rhsvar)])]),
			   Add(InjectFrom(GetTag(lhsvar),ProjectTo(INT_t)),InjectFrom(GetTag(rhsvar),ProjectTo(INT_t))),
			   IfExp(And([IsTag(BIG_t, lhsvar),
					   IsTag(BIG_t, rhsvar)]),
					   CallFunc(Name('add_big'), [InjectFrom(GetTag(lhsvar),ProjectTo(BIG_t)),InjectFrom(GetTag(rhsvar),ProjectTo(BIG_t))], None, None)))))
		elif isinstance(ast,And):
			
		return explicated
		
	def explicateIfExp(ast):
		
	def visitConst(ast):
		return InjectFrom(INT_t,Const(ast.value))

	def explicateLogical(ast):
		if isinstance(ast,And):
			lhsvar = ast.nodes[0]
			rhscar = ast.nodes[1]
			explicated = Let(lhsvar,Let(rhsvar,If
		elif isinstance(ast,Or):
		return explicated
	
	
	
	@staticmethod
	def explicate(ast):
		Explicate.explicate_helper(ast)
		explicated_ast = Module(None, Stmt(exp_stmt.nodes))
		return explicated_ast
	
	@staticmethod
	def explicate_helper(ast):
        
		if isinstance(ast, Module):
			python_compiler.explicate_helper(ast.node)
			return 0

		elif isinstance(ast, Stmt):
			for node in ast.nodes:
				length = len(exp_stmt.nodes)
				tmp_num = length
				python_compiler.explicate_helper(node)
			return tmp_num
			
		elif isinstance(ast, Printnl):
			print_var = python_compiler.explicate_helper(ast.nodes[0], tmp_num)
			new_stmt = 'print tmp' + str(print_var)
			exp_stmt.nodes.append(compiler.parse(new_stmt).node.nodes[0])
			return print_var

		elif isinstance(ast, Discard):
			python_compiler.explicate_helper(ast.expr, tmp_num)
			return tmp_num

		elif isinstance(ast, Assign):
			if isinstance(ast.expr,Name):
				if ast.nodes[0].name == ast.expr.name:
					return tmp_num
					
			varName = "__"+ast.nodes[0].name
			right_val = python_compiler.explicate_helper(ast.expr, tmp_num)

			new_stmt = varName + ' = tmp' + str(right_val)
			if (append == True): return python_compiler.yesAppend(right_val,new_stmt)
			else: return python_compiler.noAppend(rightval,new_stmt)

		elif isinstance(ast, Add):
			return exp_stmt.append(explicateBinary(ast))

		elif isinstance(ast, UnarySub):
			neg_var = python_compiler.explicate_helper(ast.expr, tmp_num)
			new_stmt = 'tmp' + str(neg_var + 1) + ' = -tmp' + str(neg_var)
			if (append == True): return python_compiler.yesAppend(neg_var+1,new_stmt)
			else: return python_compiler.noAppend(neg_var+1,new_stmt)
			
		elif isinstance(ast, CallFunc):
			new_stmt = 'tmp' + str(tmp_num) + ' = input()'
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
			expr_val = python_compiler.explicate_helper(ast.expr,tmp_num)
			op_val = python_compiler.explicate_helper(ast.ops[1],expr_val+1)
			new_stmt = 'tmp'+str(op_val+1) + ' = ' 'tmp'+str(expr_val) + ' ' + str(ast.ops[0]) + ' ' + 'tmp'+str(op_val)
			if (append==True): return python_compiler.yesAppend(op_val+1,new_stmt)
			else: return python_compiler.noAppend(op_val+1,new_stmt)

		elif isinstance(ast,Or):
			left = python_compiler.explicate_helper(ast.nodes[0],tmp_num)
			right = python_compiler.explicate_helper(ast.nodes[1],left+1)
			new_stmt = 'tmp'+str(right+1) + ' = ' + 'tmp'+str(left) + ' or ' + 'tmp'+str(right)
			if (append==True): return python_compiler.yesAppend(right+1,new_stmt)
			else: return python_compiler.noAppend(right+1,new_stmt)			
		
		elif isinstance(ast,And):
			left = python_compiler.explicate_helper(ast.nodes[0],tmp_num)
			right = python_compiler.explicate_helper(ast.nodes[1],left+1)
			new_stmt = 'tmp'+str(right+1) + ' = ' + 'tmp'+str(left) + ' and ' + 'tmp'+str(right)
			if (append==True): return python_compiler.yesAppend(right+1,new_stmt)
			else: return python_compiler.noAppend(right+1,new_stmt)

		elif isinstance(ast,Not):
			not_var = python_compiler.explicate_helper(ast.expr, tmp_num)
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
					new_val = python_compiler.explicate_helper(ast.items[x][1],tmp_num)
					tmp_num += 1
					if isinstance(ast.items[x][0], Const):
						new_stmt += str(ast.items[x][0].value) + ':' + 'tmp'+str(new_val) + ','
					if isinstance(ast.items[x][0], Name):
						new_stmt += str(ast.items[x][0].name) + ':' + 'tmp'+str(new_val) + ','
				new_val = python_compiler.explicate_helper(ast.items[length-1][1],tmp_num)
				if isinstance(ast.items[length-1][0], Const):
					new_stmt += str(ast.items[length-1][0].value) + ':' + 'tmp'+str(new_val) + '}'
				if isinstance(ast.items[length-1][0], Name):
					new_stmt += str(ast.items[length-1][0].name) + ':' + 'tmp'+str(new_val) + '}'
				if(append==True): return python_compiler.yesAppend(new_val+1,new_stmt)
				else: return python_compiler.noAppend(new_val+1,new_stmt)
			else:
				new_val = python_compiler.explicate_helper(ast.items[length-1][1],tmp_num)
				if isinstance(ast.items[length-1][0],Const):
					new_stmt += str(ast.items[length-1][0].value) + ':' + 'tmp'+str(new_val) + '}'
				if isinstance(ast.items[length-1][0],Name):
					new_stmt += str(ast.items[length-1][0].name) + ':' + 'tmp'+str(new_val) + '}'
				if(append==True): return python_compiler.yesAppend(new_val+1,new_stmt)
				else: return python_compiler.noAppend(new_val+1,new_stmt)
			
		elif isinstance(ast,Subscript):
			new_tmp = 'tmp'+str(tmp_num)
			if(append==True):
				exp_stmt.nodes.append(Assign([AssName(new_tmp, 'OP_ASSIGN')], Subscript(ast.expr, ast.flags, [ast.subs[0]])))
				return tmp_num+1
			else:
				new_stmt = Assign([AssName(new_tmp, 'OP_ASSIGN')], Subscript(ast.expr, ast.flags, [ast.subs[0]]))
				return (tmp_num+1,new_stmt)
			
		elif isinstance(ast,IfExp):
			#yes this does work for cases like 4 if (2 if 3 else 1) else 0 :-)
			test_var = python_compiler.explicate_helper(ast.test, tmp_num,True)
			tuple_then = python_compiler.explicate_helper(ast.then,test_var+1,False) 
			then_var = tuple_then[1]
			tuple_else = python_compiler.explicate_helper(ast.else_,test_var+1,False) 
			else_var = tuple_else[1]
			else_tmp_num = tuple_else[0]
			
			test_tmp = 'tmp'+str(test_var)
			
			new_stmt = IfExp(Name(test_tmp),then_var,else_var)
			
			exp_stmt.nodes.append(new_stmt)
			return else_tmp_num
            
		else:
			raise Exception("Error: Unrecognized node type")	
