from compiler.ast import *
import copy
import Queue
from PythonASTExtension import *
from IfExpLivenessAnalysis import *

class LivenessAnalysis:
	
	liveVariables = {}
	
	@staticmethod
	def ifExpLiveness(ast):

		def recursion(ast):
			if isinstance(ast.then,stmt):
				save1 = [determineLiveVariables(node,j) for node in ast.then.nodes]
			if isinstance(ast.else_,stmt):
				save2 = [determineLiveVariables(node,j) for node in ast.else_.nodes]
				

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
			elif isinstance(ast.expr,Compare): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.expr.name)) | set((ast.expr.ops[1].name))
			#elif isinstance(ast.expr,IfExp): return (LivenessAnalysis.liveVariables[j+1] - remove) | LivenessAnalysis.ifExpLiveness(ast.expr)
			elif isinstance(ast.expr,InjectFrom): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.arg))
			elif isinstance(ast.expr,ProjectTo): return (LivenessAnalysis.liveVariables[j+1] - remove) | set((ast.expr.arg))				
			else: raise Exception("Error: Unrecognized node type")										
		elif isinstance(ast,CallFunc): return LivenessAnalysis.liveVariables[j+1] | LivenessAnalysis.callFuncLiveness(ast)
		elif isinstance(ast,GetTag): return LivenessAnalysis.liveVariables[j+1]
		elif isinstance(ast,IfExp): return LivenessAnalysis.liveVariables[j+1] | LivenessAnalysis.ifExpLiveness(ast.expr)
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
