from compiler.ast import *
import copy
import Queue
from PythonASTExtension import *

class GraphColoring:

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
