from PythonASTExtension import *
from AssemblyAST import *

BIG_t = Const(3)

class ClosureConversion:

		def __init__(self,varmap):
			self.variableMapping = varmap
			self.reservedFunctions = ['input','input_int','print_any','add','set_subscript','create_list','create_dict','get_fun_ptr','get_free_vars','main']

		def createClosure(self,node):
			if isinstance(node,Assign):
				if isinstance(node.expr,Lambda):
					if isinstance(node.nodes[0],AssName): new_func_name = str(node.nodes[0].name) + '$function'
					elif isinstance(node.nodes[0],Subscript): new_func_name = str(node.nodes[0].expr.name) + '$function' 
									
					captured_vars = [Name(var) for var in node.expr.argnames if var in self.variableMapping[node.expr.uniquename]]
					closure = CreateClosure(Name(new_func_name),List(captured_vars))
					assign = Assign(node.nodes,closure)
					func_node = Function(None,new_func_name,node.expr.argnames,(),0,None,node.expr.code)
					func_node.uniquename = node.expr.uniquename
					return Stmt([func_node,assign])
				else: return node
			elif isinstance(node,CallFunc):
				if node.node.name in self.reservedFunctions: return node
				else:
					new_name = str(node.node.name)+ '$getclos'
					return GetClosure(node.node,node.args)
			else: return node
