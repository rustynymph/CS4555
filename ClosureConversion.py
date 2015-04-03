from PythonASTExtension import *
from AssemblyAST import *

BIG_t = Const(3)


class NameTracker():
	def __init__(self,prefix,count=0):
		self.prefix = prefix
		self.count = count

	def getName(self):
		return self.prefix + "$" + str(self.count)

	def getNameAndIncrementCounter(self):
		name = self.getName()
		self.count += 1
		return name

class ClosureConversion:

		def __init__(self,varmap):
			self.variableMapping = varmap
			self.reservedFunctions = ['input','input_int','print_any','add','set_subscript','create_list','create_dict','get_fun_ptr','get_free_vars','main']
			self.generateName = NameTracker('fvs')

		def createClosure(self,node):
			if isinstance(node,Assign):
				if isinstance(node.expr,Lambda):
					if isinstance(node.nodes[0],AssName): new_func_name = str(node.nodes[0].name) + '$function'
					elif isinstance(node.nodes[0],Subscript): new_func_name = str(node.nodes[0].expr.name) + '$function'
					captured_vars = [var for var in node.expr.argnames if var.name in self.variableMapping[node.expr.uniquename]]
					fvs_n = self.generateName.getNameAndIncrementCounter()
					fvs_name = Name(fvs_n)
					newArgnames = [node.expr.argnames.remove(i) for i in captured_vars] + [fvs_name]
					fvsAss = Assign([AssName(fvs_n,'OP_ASSIGN')],List(captured_vars))
					closure = CreateClosure(Name(new_func_name),[fvs_name])
					assign = Assign(node.nodes,closure)
					func_node = Function(None,new_func_name,newArgnames,(),0,None,node.expr.code)
					func_node.uniquename = node.expr.uniquename
					return Stmt([fvsAss,func_node,assign])
				else: return node
			elif isinstance(node,Return):
				if isinstance(node.value,Lambda):
					captured_vars = [var for var in node.value.argnames if var.name in self.variableMapping[node.value.uniquename]]
					fvs_n = self.generateName.getNameAndIncrementCounter()
					fvs_name = Name(fvs_n)
					closure = CreateClosure(Name(new_func_name),[fvs_name])
					fvsAss = Assign([AssName(fvs_n,'OP_ASSIGN')],List(captured_vars))
					newArgnames = [node.value.argnames.remove(i) for i in captured_vars] + [fvs_name]
					returN = Return(closure)
					func_node = Function(None,new_func_name,newArgnames,(),0,None,node.value.code)
					func_node.uniquename = node.value.uniquename
					return Stmt([fvsAss,func_node,returN])
				else: return node

			elif isinstance(node,CallFunc):
				if node.node.name in self.reservedFunctions: return node
				else:
					new_name = str(node.node.name)+ '$getclos'
					return GetClosure(node.node,node.args)
			else: return node


'''
        label_name = 'Q' + generate_name("SLambda")
        
        # Recurse on code body
        slambdas = []
        (code, rslambdas) = self.dispatch(n.code, False)
        slambdas += rslambdas
        # Setup fvs list
        fvs_n = generate_name("fvs")
        fvs = []
        # Setup each free variable
        stmts = []
        cnt = 0
        for var in n.free_vars:
            fvs += [Name(var)]
            stmt = make_assign(var, Subscript(Name(fvs_n),
                                              [InjectFrom(INT_t, Const(cnt))]))
            stmts += [stmt]
            cnt += 1
        # Setup list of stmts
        stmts += code.nodes
        # Setup params, appending fvs
        params = []
        params += [fvs_n]
        params += n.params
        #Create SLambdaLabel
        label = SLambdaLabel(label_name, len(params))
        # Create new closed slambda
        slambdas += [SLambda(params, StmtList(stmts), label_name)]
        # Return Call and list of SLambdas
        return (InjectFrom(BIG_t, CallCREATECLOSURE([label, List(fvs)])), slambdas)
'''