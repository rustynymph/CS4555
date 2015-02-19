from compiler.ast import *
import copy
import Queue


class LivenessAnalysis:
	
	__interference = {}
	__liveVariables = {}
	
	@staticmethod
	def livenessAnalysis(IR):
		
		ir = IR.node.nodes
		#print ir
		interference = {}
		liveVariables = {}
		numInstructions = len(ir)
		for i in range (numInstructions,-1,-1):
			liveVariables[i] = set()
		j = numInstructions-1
		for instructions in reversed(ir):
			if(isinstance(instructions,Assign)):
				varWritten = instructions.nodes[0].name
				remove = set((varWritten,))
				varRead = instructions.expr
				if(isinstance(varRead,Name)):
					liveVariables[j] = set((liveVariables[j+1] | set((varRead))) - remove)
				elif(isinstance(varRead,UnarySub)):
					if isinstance(varRead.expr,Name):
						varRead = varRead.expr.name
						liveVariables[j] = set((liveVariables[j+1] | set((varRead,))) - remove)
					elif isinstance(varRead.expr,Const):
						liveVariables[j] = set(liveVariables[j+1] - remove)
				elif(isinstance(varRead,Add)):
					leftnode = varRead.left
					rightnode = varRead.right
					if(isinstance(leftnode,Name) and isinstance(rightnode,Name)):
						liveVariables[j] = set((liveVariables[j+1] | set((leftnode)) | set((rightnode))) - remove)
					elif(isinstance(leftnode,Name) and not(isinstance(rightnode,Name))):
						liveVariables[j] = set((liveVariables[j+1] | set((leftnode))) - remove)
					elif(not(isinstance(leftnode,Name)) and isinstance(rightnode,Name)):
						liveVariables[j] = set((liveVariables[j+1] | set((rightnode))) - remove)
					else:
						liveVariables[j] = set((liveVariables[j+1]) - remove)
				else:
					liveVariables[j] = set((liveVariables[j+1]) - remove)
			else:
				if(isinstance(instructions,Printnl)):
					varRead = instructions.nodes[0]
					liveVariables[j] = set((set((varRead))|set(liveVariables[j+1])))
				else:
					varRead = instructions.nodes[0]
					raise Exception("Error: Unrecognized node type")
			j-=1
		#print liveVariables
		return [liveVariables[x] for x in liveVariables]	
		
	@staticmethod
	def createGraph(liveVariables):
		#lv = [liveVariables[i] for i in liveVariables]
		lv = liveVariables
		graph = {}
		for variableSet in lv:
			for variable in variableSet:
				edges = [x for x in (variableSet - set((variable,)))]
				if variable not in graph: graph[variable] = []
				graph[variable] += edges
		return graph

	@staticmethod
	def colorGraph(graph):
		queue = Queue.Queue()
		def saturation(graph):
			saturationGraph = {}
			for element in graph:
				length = len(graph[element])
				if length not in saturationGraph: saturationGraph[length] = []
				saturationGraph[length] += [element]
			return saturationGraph
		satGraph = saturation(graph)
		satkeys = [x for x in satGraph]
		colored = {}
		
		#if spill:
		#	for item in spill:
		#		queue.put(item)
				
		for key in reversed(satkeys):
			l = satGraph[key]
			for elem in l:
				queue.put(elem)
				
		while not(queue.empty()):
			colors = ["eax","ebx","ecx","edx","edi","esi"]
			item = queue.get()
			interfere_vars = graph[item]
			availColors = copy.copy(colors)
			for x in interfere_vars:
				if x in colored:
					if colored[x] in availColors:
						availColors.remove(colored[x])
			if len(availColors) > 0:
				colored[item] = availColors[0]
			else:
				colored[item] = "SPILL"		

		return colored
				
