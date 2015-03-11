from compiler.ast import *
import copy
import Queue
from PythonASTExtension import *

class LivenessAnalysis:
	
	liveVariables = {}
	
	@staticmethod
	def ifExpLiveness(ast,savenodes):
		#savenodes = saveSet
		#print ast
		#savenodes = savenodes | set((ast.test.name,))
		
	
				
		if isinstance(ast,Assign):
			if isinstance(ast.nodes[0],AssName): remove = set((ast.nodes[0].name))
			elif isinstance(ast.nodes[0],Subscript): remove = (set((ast.nodes[0].expr.name)) | set((ast.nodes[0].subs[0].name)))
			if isinstance(ast.expr,Name): (savenodes - remove) | set((ast.expr.name))
			elif isinstance(ast.expr,Const): (savenodes - remove)
			elif isinstance(ast.expr,CallFunc): (savenodes - remove) | LivenessAnalysis.callFuncLiveness(ast.expr)
			elif isinstance(ast.expr,UnarySub): (savenodes - remove) | set((ast.expr.expr.name))
			elif isinstance(ast.expr,Add): (savenodes - remove) | set((ast.expr.left.name)) | set((ast.expr.right.name))
			elif isinstance(ast.expr,Subscript): (savenodes - remove) | set((ast.expr.expr.name)) | set((ast.expr.subs[0].name))
			elif isinstance(ast.expr,Dict): (savenodes - remove) | set([x.name for x in ast.expr.items])
			elif isinstance(ast.expr,List): (savenodes - remove) | set([x.name for x in ast.expr.nodes])
			elif isinstance(ast.expr,Not): (savenodes - remove) | set((ast.expr.expr.name))
			elif isinstance(ast.expr,And): (savenodes - remove) | set([x.name for x in ast.expr.nodes])
			elif isinstance(ast.expr,Or): (savenodes - remove) | set([x.name for x in ast.expr.nodes])
			elif isinstance(ast.expr,Compare):
				savevar = set()
				savevar2 = set()
				if isinstance(ast.expr.ops[0][1],Name): savevar2 = set((ast.expr.ops[0][1].name,))
				if isinstance(ast.expr.expr,Name): savevar = set((ast.expr.expr.name,))
				(savenodes - remove) | savevar | savevar2
			elif isinstance(ast.expr,InjectFrom): (savenodes - remove) | set((ast.expr.arg))
			elif isinstance(ast.expr,ProjectTo): (savenodes - remove) | set((ast.expr.arg))				
			else: raise Exception("Error: Unrecognized node type")										
		elif isinstance(ast,CallFunc): savenodes | LivenessAnalysis.callFuncLiveness(ast)
		elif isinstance(ast,GetTag): savenodes
		elif isinstance(ast,IfExp):
			savenodes = savenodes | set((ast.test.name,))			
			if isinstance(ast.then,Stmt):
				for node in ast.then.nodes:
					savenodes = savenodes | LivenessAnalysis.ifExpLiveness(node,savenodes)
			else: savenodes = savenodes | LivenessAnalysis.ifExpLiveness(ast.then,savenodes)
				
			if isinstance(ast.else_,Stmt):
				for node in ast.else_.nodes:
					savenodes = savenodes | LivenessAnalysis.ifExpLiveness(node,savenodes)
			else: savenodes = savenodes | LivenessAnalysis.ifExpLiveness(ast.else_,savenodes)	

		elif isinstance(ast,Printnl): savenodes | set((ast.nodes[0]))
		else: raise Exception("Error: Unrecognized node type")		
		return savenodes
				

	@staticmethod
	def callFuncLiveness(ast):
		saveVars = set()
		for x in ast.args:
			if isinstance(x,Name):
				saveVars = saveVars | set((x.name,))
			else:
				saveVars = saveVars
		return saveVars		
	
	@staticmethod
	def determineLiveVariables(ast,j):
		if isinstance(ast,Assign):
			if isinstance(ast.nodes[0],AssName): remove = set((ast.nodes[0].name))
			elif isinstance(ast.nodes[0],Subscript): remove = (set((ast.nodes[0].expr.name)) | set((ast.nodes[0].subs[0].name)))
			if isinstance(ast.expr,Name): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.name))
			elif isinstance(ast.expr,Const): return (LivenessAnalysis.liveVariables[j+1] - remove)
			elif isinstance(ast.expr,CallFunc): return (LivenessAnalysis.liveVariables[j+1] - remove) | LivenessAnalysis.callFuncLiveness(ast.expr)
			elif isinstance(ast.expr,UnarySub): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.expr.name))
			elif isinstance(ast.expr,Add): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.left.name)) | set((ast.expr.right.name))
			elif isinstance(ast.expr,Subscript): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.expr.name)) | set((ast.expr.subs[0].name))
			elif isinstance(ast.expr,Dict): return (LivenessAnalysis.liveVariables[j+1] - remove) | set([x.name for x in ast.expr.items])
			elif isinstance(ast.expr,List): return (LivenessAnalysis.liveVariables[j+1] - remove) | set([x.name for x in ast.expr.nodes])
			elif isinstance(ast.expr,Not): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.expr.name))
			elif isinstance(ast.expr,And): return (LivenessAnalysis.liveVariables[j+1] - remove) | set([x.name for x in ast.expr.nodes])
			elif isinstance(ast.expr,Or): return (LivenessAnalysis.liveVariables[j+1] - remove) | set([x.name for x in ast.expr.nodes])
			elif isinstance(ast.expr,Compare):
				savevar = set()
				savevar2 = set()
				if isinstance(ast.expr.ops[0][1],Name): savevar2 = set((ast.expr.ops[0][1].name,))
				if isinstance(ast.expr.expr,Name): savevar = set((ast.expr.expr.name,))				
				return (LivenessAnalysis.liveVariables[j+1] - remove) | savevar | savevar2
			elif isinstance(ast.expr,InjectFrom):
				if isinstance(ast.expr.arg,Name): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.arg.name,))
				else: return (LivenessAnalysis.liveVariables[j+1] - remove)
			elif isinstance(ast.expr,ProjectTo): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.arg))				
			else: raise Exception("Error: Unrecognized node type")										
		elif isinstance(ast,CallFunc): return LivenessAnalysis.liveVariables[j+1] | LivenessAnalysis.callFuncLiveness(ast)
		elif isinstance(ast,GetTag): return LivenessAnalysis.liveVariables[j+1]
		elif isinstance(ast,IfExp):
			savenodes = set()
			return LivenessAnalysis.liveVariables[j+1] | LivenessAnalysis.ifExpLiveness(ast,savenodes)
		elif isinstance(ast,Printnl): return LivenessAnalysis.liveVariables[j+1] | set((ast.nodes[0]))
		else: raise Exception("Error: Unrecognized node type")
	
	@staticmethod
	def livenessAnalysis(IR):
		ir = IR.node.nodes
		numInstructions = len(ir)
		for i in range (numInstructions,-1,-1):
			LivenessAnalysis.liveVariables[i] = set()
		j = numInstructions-1
		for instructions in reversed(ir):
			LivenessAnalysis.liveVariables[j] = LivenessAnalysis.determineLiveVariables(instructions,j)	
			j-=1

		return [LivenessAnalysis.liveVariables[x] for x in LivenessAnalysis.liveVariables]				
