from abc import ABCMeta, abstractmethod
from X86Operands import *

class Instruction():
	__metaclass__ = ABCMeta

	def __init__(self):
		raise Exception("Cannot instantiate " + self.__class__.__name__ + " because it is an abstract class.")

	def __repr__(self):
		pass

	def __str__(self):
		pass

	def printInstruction(self):
		pass

class NoOperandInstruction(Instruction):
	__metaclass__ = ABCMeta

class UnaryInstruction(Instruction):
	__metaclass__ = ABCMeta

	def __init__(self,operand):
		pass

class BinaryInstruction(Instruction):
	__metaclass__ = ABCMeta

	def __init__(self,fromOperand,toOperand):
		if isinstance(fromOperand,MemoryOperand) and isinstance(toOperand,MemoryOperand):
			raise Exception("BinaryInstruction can only take in one memory location at a time.")
		if isinstance(fromOperand,ConstantOperand) and isinstance(toOperand,ConstantOperand):
			raise Exception("Cannot perform binary instruction with two constants.")
		if isinstance(toOperand,ConstantOperand):
			raise Exception("toOperand cannot be a ConstantOperand.")

		self.fromOperand = fromOperand
		self.toOperand = toOperand

def getMinSizeFromOperands(operand1,operand2):
	size = operand1.size if operand1.size < operand2.size else operand2.size
	return size

def x86InstructionToString(name,args):
	instructionString = name + "("

	for i in range(len(args)-1):
		a = args[i]
		instructionString += str(a) + ","

	if len(args) > 0: instructionString += str(args[len(args)-1])
	instructionString += ")"
	return instructionString

def printNoOperandX86Instruction(name):
	return name + "\n"

def printUnaryX86Instruction(name,operand,size=""):
	return name + size + " " + operand.printOperand() + "\n"

def printBinaryX86Instruction(name,fromOperand,toOperand,size=""):
	return name + size + " " + fromOperand.printOperand() + ", " + toOperand.printOperand() + "\n"
