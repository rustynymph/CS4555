from PythonASTExtension import *
from AssemblyAST import *

class SeparateFunctions:
	
	@staticmethod
	def move(x86):
		separated = {}
		i = 0 
		instructions = []
		for node in x86.instructions.nodes[0].clusteredInstruction.nodes:
			if isinstance(node,AssemblyFunction):
				if not(node.sectionHeader.name == "main"):
					separated[i] = node
					i += 1
					continue
				else: instructions.append(node)
			else: instructions.append(node)
		for removed in separated:
			instructions.append(separated[removed])
		x86.instructions.nodes[0].clusteredInstruction = ClusteredInstruction(instructions)	
		return AssemblyProgram(x86.entryPoint,x86.instructions)


