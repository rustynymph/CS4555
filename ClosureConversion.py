from compiler.ast import *
from PythonASTExtension import *
from AssemblyAST import *

BIG_t = Const(3)

class ClosureConversion:

		def __init__(self,varmap,lammap):
			self.variableMapping = varmap
			self.reservedFunctions = ['input','input_int','print_any','add','set_subscript','create_list','create_dict','get_fun_ptr','get_free_vars','main']
			self.assignToLambdaMap = lammap

		def createClosure(self,node):
			if isinstance(node,Assign):
				if isinstance(node.expr,Lambda):
					captured_vars = [Name(var) for var in node.expr.argnames if var in self.variableMapping[node.expr.uniquename]]
					func_name = self.assignToLambdaMap[node.expr.uniquename]
					closure = CreateClosure(func_name,captured_vars)
					assign = Assign(node.nodes,closure)
					return Stmt([node.expr,assign])
				else: return node
			elif isinstance(node,CallFunc):
				if node.node.name in self.reservedFunctions: return node
				else: return GetClosure(node.node)
			else: return node
