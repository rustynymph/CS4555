from compiler.ast import *
import copy
import Queue
from PythonASTExtension import *

class LivenessAnalysis:
	
	liveVariables = {}
	
	@staticmethod
	def assignAnalysis(ast,setname):
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
		
	@staticmethod
	def callFuncAnalysis(ast,setname):
		saveVars = set()
		for x in ast.args:
			if isinstance(x,Name):
				saveVars = saveVars | set((x.name,))
			else:
				saveVars = saveVars
		return setname | saveVars		
	
	@staticmethod
	def getTagAnalysis(ast,setname): return setname
	
	@staticmethod
	def ifExpAnalysis(ast,savenodes):
		if isinstance(ast,IfExp):
			savenodes = savenodes | set((ast.test.name,))			
			if isinstance(ast.then,Stmt):
				for node in ast.then.nodes:
					savenodes = savenodes | LivenessAnalysis.ifExpAnalysis(node,savenodes)
			else: savenodes = savenodes | LivenessAnalysis.ifExpAnalysis(ast.then,savenodes)
				
			if isinstance(ast.else_,Stmt):
				for node in ast.else_.nodes:
					savenodes = savenodes | LivenessAnalysis.ifExpAnalysis(node,savenodes)
			else: savenodes = savenodes | LivenessAnalysis.ifExpAnalysis(ast.else_,savenodes)			
		
		else: savenodes = savenodes | LivenessAnalysis.ifExpdispatch(ast,savenodes)		
		return savenodes								
	
	@staticmethod
	def ifExpdispatch(ast,setname):
		if isinstance(ast,Assign): return LivenessAnalysis.assignAnalysis(ast,setname)
		elif isinstance(ast,CallFunc): return LivenessAnalysis.callFuncAnalysis(ast,setname)
		elif isinstance(ast,GetTag): return LivenessAnalysis.getTagAnalysis(ast,setname)
		elif isinstance(ast,IfExp): return LivenessAnalysis.ifExpAnalysis(ast,setname)
		else: raise Exception("Error: Unrecognized node type")		
	
	@staticmethod
	def dispatch(ast,setname):
		if isinstance(ast,Assign): return LivenessAnalysis.assignAnalysis(ast,setname)
		elif isinstance(ast,CallFunc): return LivenessAnalysis.callFuncAnalysis(ast,setname)
		elif isinstance(ast,GetTag): return LivenessAnalysis.getTagAnalysis(ast,setname)
		elif isinstance(ast,IfExp):
			savenodes = set()
			return LivenessAnalysis.ifExpAnalysis(ast,savenodes)
		else: raise Exception("Error: Unrecognized node type")
					
	@staticmethod
	def livenessAnalysis(IR):
		ir = IR.node.nodes
		numInstructions = len(ir)
		for i in range (numInstructions,-1,-1):
			LivenessAnalysis.liveVariables[i] = set()
		j = numInstructions-1
		for instructions in reversed(ir):
			print("\n")
			print instructions
			LivenessAnalysis.liveVariables[j] = LivenessAnalysis.dispatch(instructions,LivenessAnalysis.liveVariables[j+1])	
			j-=1

		return [LivenessAnalysis.liveVariables[x] for x in LivenessAnalysis.liveVariables]				
