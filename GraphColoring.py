from compiler.ast import *
import copy
import Queue
from PythonASTExtension import *
from AssemblyAST import *

class GraphColoring:

	def __init__(self,ignore):
		self.ignore = ignore

	@staticmethod
	def createGraph(liveVariables):
		lv = liveVariables
		print "hello"
		print lv
		graph = {}
		for variableSet in lv:
			for variable in variableSet:
				edges = [x for x in (variableSet - set((variable,)))]
				if variable not in graph: graph[variable] = []
				graph[variable] += set(edges)
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
			colors = [Registers32.EAX,Registers32.EBX,Registers32.ECX,Registers32.EDX,Registers32.EDI,Registers32.ESI]
			colors = [RegisterOperand(r) for r in colors]
			item = queue.get()
			interfere_vars = graph[item]
			availColors = copy.copy(colors)
			for x in interfere_vars:
				if x in colored:
					if colored[x] in availColors:
						availColors.remove(colored[x])
			if len(availColors) > 0: colored[item] = availColors[0]
			else: colored[item] = None	

		return colored

	@staticmethod
	def getRuntimeFunctions():
		runtime = []


	def createGraphFolding(self,ast,acc):
		liveVariables = set([x for x in ast.liveness if x not in self.ignore])
		graph = acc
		for variable in liveVariables:

			if variable not in self.ignore:
				edges = [x for x in (liveVariables - set([variable]))]
				if variable not in graph: graph[variable] = set([])
				graph[variable] = graph[variable] | set(edges)

		return graph

