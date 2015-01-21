import compiler
from compiler.ast import *

class Parser:
	@staticmethod
	def parseFile(path):
		return compiler.parseFile(path);

	@staticmethod
	def parse(source):
		return compiler.parse(source);