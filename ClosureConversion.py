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
					captured_vars = [var for var in node.expr.argnames if var in self.variableMapping[node.expr.uniquename]]
					fvs_n = node.expr.fvsname
					newArgnames = node.expr.argnames + [fvs_n]
					fvsAss = node.expr.fvsList
					closure = InjectFrom(BIG_t,CreateClosure(Name(new_func_name),[Name(fvs_n)]))
					assign = Assign(node.nodes,closure)
					func_node = Function(None,new_func_name,newArgnames,(),0,None,node.expr.code)
					func_node.uniquename = node.expr.uniquename
					return Stmt([fvsAss,func_node,assign])
				else: return node
			elif isinstance(node,Return):
				if isinstance(node.value,Lambda):
					captured_vars = [var for var in node.value.argnames if var.name in self.variableMapping[node.value.uniquename]]
					fvs_n = node.value.fvsname
					closure = InjectFrom(BIG_t,CreateClosure(Name(new_func_name),[Name(fvs_n)]))
					fvsAss = node.value.fvsList
					newArgnames = node.value.argnames + [fvs_n]
					returN = Return(closure)
					func_node = Function(None,new_func_name,newArgnames,(),0,None,node.value.code)
					func_node.uniquename = node.value.uniquename
					return Stmt([fvsAss,func_node,returN])
				else: return node

			elif isinstance(node,CallFunc):
				if node.node.name in self.reservedFunctions: return node
				else: return GetClosure(node.node,node.args)
			else: return node

