from compiler.ast import *

class Boolean(Node):
	def __init__(self,value):
		self.value = value

	def __str__(self):
		return "Boolean(" + str(self.value) + ")"

	def __repr__(self):
		return "Boolean(" + str(self.value) + ")"
		
class GetTag(Node):
	def __init__(self,arg):
		self.arg = arg

	def __repr__(self):
		return self.__class__.__name__ + "(" + str(self.arg) + ")"
		
	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.arg) + ")"
			
class IsTag(Node):
	def __init__(self,typ,arg):
		self.typ = typ
		self.arg = arg

	def __repr__(self):
		return self.__class__.__name__ + "(" + str(self.typ) + "," + str(self.arg) + ")"
		
	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.typ) + "," + str(self.arg) + ")"
		
class InjectFrom(Node):
	def __init__(self,typ,arg):
		self.typ = typ
		self.arg = arg
	
	def __repr__(self):
		return self.__class__.__name__ + "(" + str(self.typ) + "," + str(self.arg) + ")"
		
	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.typ) + "," + str(self.arg) + ")"
	
class ProjectTo(Node):
	def __init__(self,typ,arg):
		self.typ = typ
		self.arg = arg

	def __repr__(self):
		return self.__class__.__name__ + "(" + str(self.typ) + "," + str(self.arg) + ")"
		
	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.typ) + "," + str(self.arg) + ")"		
		
	
class Let(Node):
	def __init__(self,var,expr,body):
		self.var = var
		self.expr = expr
		self.body = body
		
	def __repr__(self):
		return self.__class__.__name__ + "(" + str(self.var) + "," + str(self.expr) + "," + str(self.body) + ")"
		
	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.var) + "," + str(self.expr) + "," + str(self.body) + ")"
		
class AssignCallFunc(Node):
	def __init__(self,var,name,args):
		self.var = var
		self.name = name
		self.args = args
	
	def __repr__(self):
		return self.__class__.__name__ + "(" + str(self.var) + "," + str(self.name) + str(self.args) + ")"
		
	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.var) + "," + str(self.name) + str(self.args) + ")"

class CreateClosure(Node):
	def __init__(self,name,fvs):
		self.name = name
		self.fvs = fvs
		
	def __repr__(self):
		return self.__class__.__name__ + "(" + str(self.name) + "," + str(self.fvs) + ")"
		
	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.name) + "," + str(self.fvs) + ")"

class GetClosure(Node):
	def __init__(self,name):
		self.name = name
		self.args = args
		
	def __repr__(self):
		return self.__class__.__name__ + "(" + str(self.name) + "," + str(self.args) + ")"
		
	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.name) +  "," + str(self.args) + ")"
	
def isPythonASTLeaf(ast):
	return isinstance(ast,Const) or isinstance(ast,Boolean) or isinstance(ast,Name) or isinstance(ast,AssName)
