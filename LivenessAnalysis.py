from compiler.ast import *
import copy
import Queue


class LivenessAnalysis:
	
	__interference = {}
	__liveVariables = {}
	
	@staticmethod
	def livenessAnalysis(IR):
		
		ir = IR.node.nodes

		interference = {}
		liveVariables = {}
		numInstructions = len(ir)
		for i in range (numInstructions,-1,-1):
			liveVariables[i] = set()
		j = numInstructions-1
		for instructions in reversed(ir):
			#print instructions
			if(isinstance(instructions,Assign)):
				varWritten = instructions.nodes[0].name
				remove = set((varWritten,))
				varRead = instructions.expr
				if(isinstance(varRead,Name)):
					liveVariables[j] = set((liveVariables[j+1] - remove) | set((varRead)))
				elif(isinstance(varRead,Or)):
					if isinstance(varRead.nodes[0],Name) and isinstance(varRead.nodes[1],Name):
						varRead1 = set((varRead.nodes[0].name,))
						varRead2 = set((varRead.nodes[1].name,))
						liveVariables[j] = set(((liveVariables[j+1] - remove)|varRead1)|varRead2)
					elif isinstance(varRead.nodes[0],Name) and not(isinstance(varRead.nodes[1],Name)):
						varRead1 = set((varRead.nodes[0].name,))
						liveVariables[j] = set((liveVariables[j+1] - remove)|varRead1)
					elif not(isinstance(varRead.nodes[0],Name)) and isinstance(varRead.nodes[1],Name):
						varRead2 = set((varRead.nodes[1].name,))
						liveVariables[j] = set((liveVariables[j+1] - remove)|varRead2)	
					else:
						liveVariables[j] = set(liveVariables[j+1] - remove)
				elif(isinstance(varRead,And)):
					if isinstance(varRead.nodes[0],Name) and isinstance(varRead.nodes[1],Name):
						varRead1 = set((varRead.nodes[0].name,))
						varRead2 = set((varRead.nodes[1].name,))
						liveVariables[j] = set(((liveVariables[j+1] - remove)|varRead1)|varRead2)
					elif isinstance(varRead.nodes[0],Name) and not(isinstance(varRead.nodes[1],Name)):
						varRead1 = set((varRead.nodes[0].name,))
						liveVariables[j] = set((liveVariables[j+1] - remove)|varRead1)
					elif not(isinstance(varRead.nodes[0],Name)) and isinstance(varRead.nodes[1],Name):
						varRead2 = set((varRead.nodes[1].name,))
						liveVariables[j] = set((liveVariables[j+1] - remove)|varRead2)	
					else:
						liveVariables[j] = set(liveVariables[j+1] - remove)					
				elif(isinstance(varRead,Compare)):
					if isinstance(varRead.expr,Name) and isinstance(varRead.ops[1],Name):
						varRead1 = set((varRead.expr.name,))
						varRead2 = set((varRead.ops[1].name,))
						liveVariables[j] = set(((liveVariables[j+1]-remove)|varRead1)|varRead2)
					elif isinstance(varRead.expr,Name) and not(isinstance(varRead.ops[1],Name)):
						varRead1 = set((varRead.expr.name,))
						liveVariables[j] = set((liveVariables[j+1]-remove)|varRead1)
					elif not(isinstance(varRead.expr,Name)) and isinstance(varRead.ops[1],Name):
						varRead2 = set((varRead.ops[1].name,))
						liveVariables[j] = set((liveVariables[j+1]-remove)|varRead2)
					else:
						liveVariables[j] = set(liveVariables[j+1]-remove)						
				elif(isinstance(varRead,Subscript)):
					liveVariables[j] = set(liveVariables[j+1]-remove)
				elif(isinstance(varRead,List)):
					liveVariables[j] = set(liveVariables[j+1]-remove)
				elif(isinstance(varRead,Dict)):
					liveVariables[j] = set(liveVariables[j+1]-remove)				
				elif(isinstance(varRead,Not)):
					if isinstance(varRead.expr,Name):
						varRead = varRead.expr.name
						liveVariables[j] = set((liveVariables[j+1] - remove) | set((varRead,)))
					elif isinstance(varRead.expr,Const):
						liveVariables[j] = set(liveVariables[j+1] - remove)
				elif(isinstance(varRead,UnarySub)):
					if isinstance(varRead.expr,Name):
						varRead = varRead.expr.name
						liveVariables[j] = set((liveVariables[j+1] - remove) | set((varRead,)))
					elif isinstance(varRead.expr,Const):
						liveVariables[j] = set(liveVariables[j+1] - remove)
				elif(isinstance(varRead,Add)):
					leftnode = varRead.left
					rightnode = varRead.right
					if(isinstance(leftnode,Name) and isinstance(rightnode,Name)):
						liveVariables[j] = set((liveVariables[j+1] - remove) | set((leftnode.name,)) | set((rightnode.name,)))
					elif(isinstance(leftnode,Name) and not(isinstance(rightnode,Name))):
						liveVariables[j] = set((liveVariables[j+1] - remove) | set((leftnode.name,)))
					elif(not(isinstance(leftnode,Name)) and isinstance(rightnode,Name)):
						liveVariables[j] = set((liveVariables[j+1] - remove) | set((rightnode.name,)))
					else:
						liveVariables[j] = set((liveVariables[j+1]) - remove)
				elif(isinstance(varRead,Const)):
					liveVariables[j] = set(liveVariables[j+1] - remove)
				else:
					liveVariables[j] = set((liveVariables[j+1]) - remove)
			elif isinstance(instructions,Printnl):
				varRead = instructions.nodes[0]
				liveVariables[j] = set(set((varRead))|set(liveVariables[j+1]))
			elif isinstance(instructions,IfExp):
				if isinstance(instructions.test,Name):
					varRead1 = set((instructions.test.name,))
					#liveVariables[j] = set((set((varRead,))|set(liveVariables[j+1])))
				if isinstance(instructions.then,Assign):
					varWritten = instructions.then.nodes[0].name
					remove1 = set((varWritten,))
					if isinstance(instructions.then.expr,Name):
						varRead2 = set((instructions.then.expr.name,))
					else:
						varRead2 = set()
					#liveVariables[j] = set((liveVariables[j+1] - remove) |set((varRead,))) 
				if isinstance(instructions.else_,Assign):
					varWritten = instructions.else_.nodes[0].name
					remove2 = set((varWritten,))
					if isinstance(instructions.else_.expr,Name):
						varRead3 = set((instructions.else_.expr.name,))
					else:
						varRead3 = set()
				liveVariables[j] = set(((((liveVariables[j+1] - remove1) - remove2) |varRead1)|varRead2)|varRead3)
			else:
				varRead = instructions.nodes[0]
				raise Exception("Error: Unrecognized node type")
			j-=1

		return [liveVariables[x] for x in liveVariables]	
		
	@staticmethod
	def createGraph(liveVariables):
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
				
