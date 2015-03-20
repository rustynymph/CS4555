from compiler.ast import *
from PythonASTExtension import *
from AssemblyAST import *

class ClosureConversion:

		def __init__(self,varmap,lammap):
			self.variableMapping = varmap
			self.reservedFunctions = ['input','input_int','print_any','add','set_subscript','create_list','create_dict','get_fun_ptr','get_free_vars','main']
			self.assignToLambdaMap = lammap

		def createClosure(self,node):
			if isinstance(node,Lambda):
				captured_vars = [var for var in node.argnames if var in self.variableMapping[node.uniquename]]
				func_name = [self.assignToLambdaMap[node.uniquename]]
				closure_args = func_name + captured_vars
				return InjectFrom(BIG_t, CallFunc('create_closure',closure_args))
			elif isinstance(node,CallFunc):
				if node.node in self.reservedFunctions: return node
				else:
					return Stmt([CallFunc('get_fun_ptr',[node.node]),CallFunc('get_free_vars',[node.node])])
			else: return node
