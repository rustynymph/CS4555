from compiler.ast import *
import copy
import Queue
from PythonASTExtension import *

class LivenessAnalysis():
	def __init__(self,IR):
		self.liveVariables = {}
		self.IR = IR.node.nodes
	
	def assignAnalysis(self,ast,setname):
		if isinstance(ast.nodes[0],AssName): remove = set((ast.nodes[0].name,))
		elif isinstance(ast.nodes[0],Subscript): remove = (set((ast.nodes[0].expr.name,)) | set((ast.nodes[0].subs[0].name,)))
		if isinstance(ast.expr,Name): return (setname - remove) | set((ast.expr.name,))
		elif isinstance(ast.expr,Const): return (setname - remove)
		elif isinstance(ast.expr,CallFunc): return (setname - remove) | LivenessAnalysis.callFuncAnalysis(ast.expr,setname)
		elif isinstance(ast.expr,UnarySub): return (setname - remove) | set((ast.expr.expr.name))
		elif isinstance(ast.expr,Add): return (setname - remove) | set((ast.expr.left.name,)) | set((ast.expr.right.name,))
		elif isinstance(ast.expr,Subscript): return (setname - remove) | set((ast.expr.expr.name,)) | set((ast.expr.subs[0].name,))
		elif isinstance(ast.expr,Dict): return (setname - remove) | set([x.name for x in ast.expr.items])
		elif isinstance(ast.expr,List): return (setname - remove) | set([x.name for x in ast.expr.nodes])
		elif isinstance(ast.expr,Not): return (setname - remove) | set((ast.expr.expr.name,))
		elif isinstance(ast.expr,And): return (setname - remove) | set([x.name for x in ast.expr.nodes])
		elif isinstance(ast.expr,Or): return (setname - remove) | set([x.name for x in ast.expr.nodes])
		elif isinstance(ast.expr,Compare):
			savevar = set()
			savevar2 = set()
			if isinstance(ast.expr.expr,Name): savevar = set((ast.expr.expr.name,))
			if isinstance(ast.expr.ops[0][1],Name): savevar2 = set((ast.expr.ops[0][1].name,))				
			return (setname - remove) | savevar | savevar2
		elif isinstance(ast.expr,InjectFrom):
			if isinstance(ast.expr.arg,Name): return (setname - remove) | set((ast.expr.arg.name,))
			else: return (setname - remove)
		elif isinstance(ast.expr,ProjectTo): return (setname - remove) | set((ast.expr.arg))				
		else: raise Exception("Error: Unrecognized node type")												
		
	def callFuncAnalysis(self,ast,setname):
		saveVars = set()
		for x in ast.args:
			if isinstance(x,Name):
				saveVars = saveVars | set((x.name,))
			else:
				saveVars = saveVars
		return setname | saveVars		
	
	def getTagAnalysis(self,ast,setname): return setname
	
	def ifExpAnalysis(self,ast,savenodes):
		if isinstance(ast,IfExp):
			savenodes = savenodes | set((ast.test.name,))			
			if isinstance(ast.then,Stmt):
				for node in ast.then.nodes:
					savenodes = savenodes | self.ifExpAnalysis(node,savenodes)
			else: savenodes = savenodes | self.ifExpAnalysis(ast.then,savenodes)
				
			if isinstance(ast.else_,Stmt):
				for node in ast.else_.nodes:
					savenodes = savenodes | self.ifExpAnalysis(node,savenodes)
			else: savenodes = savenodes | self.ifExpAnalysis(ast.else_,savenodes)			
		
		else: savenodes = savenodes | self.dispatch(ast,savenodes,True)		
		return savenodes								

	def dispatch(self,ast,setname,recursion=False):
		if isinstance(ast,Assign): return self.assignAnalysis(ast,setname)
		elif isinstance(ast,CallFunc): return self.callFuncAnalysis(ast,setname)
		elif isinstance(ast,GetTag): return self.getTagAnalysis(ast,setname)
		elif isinstance(ast,IfExp):
			if recursion: return self.ifExpAnalysis(ast,setname)
			else: return self.ifExpAnalysis(ast,savenodes = set())
		else: raise Exception("Error: Unrecognized node type")
					
	def livenessAnalysis(self):
		ir = self.IR
		numInstructions = len(ir)
		for i in range (numInstructions,-1,-1):
			self.liveVariables[i] = set()
		j = numInstructions-1
		for instructions in reversed(ir):
			self.liveVariables[j] = self.dispatch(instructions,self.liveVariables[j+1])	
			j-=1

		return [self.liveVariables[x] for x in self.liveVariables]				
