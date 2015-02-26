from compiler.ast import *

class Boolean(Node):
	def __init__(self,value):
		self.value = value

	def __str__(self):
		return "Boolean(" + str(self.value) + ")"

	def __repr__(self):
		return "Boolean(" + str(self.value) + ")"