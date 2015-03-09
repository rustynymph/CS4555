from abc import ABCMeta, abstractmethod
from X86Registers import *

class OperandSize:
	SixtyFourBits = 64
	ThirtyTwoBits = 32
	SixteenBits = 16
	EightBits = 8

	@staticmethod
	def sizeToString(size):
		if OperandSize.SixtyFourBits == size: return "qw"
		elif OperandSize.ThirtyTwoBits == size: return "l"
		elif OperandSize.SixteenBits == size: return "w"
		elif OperandSize.EightBits == size: return "b"
		elif None == size: return ""
		else: raise Exception(str(size) + " is not a valid operand size.")

class Operand(object):
	__metaclass__ = ABCMeta

	def __init__(self,size=None):
		self.size = size

	def __repr__(self):
		pass

	def __str__(self):
		pass

	def printOperand(self):
		pass


class RegisterOperand(Operand):

	def __init__(self,register,size=None):
		if not isinstance(register,Register): raise Exception(register.__class__.__name__ + " is unsupported node. register parameter must be of type Register.")
		self.register = register
		self.size = size if size else register.size

	def __repr__(self):
		return self.__class__.__name__ + "(" + self.register.name + "," + OperandSize.sizeToString(self.size) + ")"

	def __str__(self):
		return self.__class__.__name__ + "(" + self.register.name + "," + OperandSize.sizeToString(self.size) + ")"

	def __eq__(self,other):
		return self.register == other.register and self.size == other.size

	def __hash__(self):
		return hash(str(self))

	def printOperand(self):
		return self.register.printRegister()

class MemoryOperand(Operand):

	def __init__(self,register,offset=0,size=OperandSize.ThirtyTwoBits):
		if not isinstance(register,Register): raise Exception(register.__class__.__name__ + " is unsupported node. register parameter must be of type Register.")
		self.register = register
		self.offset = offset
		self.size = size

	def __repr__(self):
		return self.__class__.__name__ + "(" + self.register.name + "," + str(offset) + "," + OperandSize.sizeToString(self.size) + ")"

	def __str__(self):
		return self.__class__.__name__ + "(" + self.register.name + "," + str(offset) + "," + OperandSize.sizeToString(self.size) + ")"

	def __eq__(self,other):
		return self.register == other.register and self.offset == other.offset and self.size == other.size

	def __hash__(self):
		return hash(str(self))

	def printOperand(self):
			if self.offset == 0: return "(" + self.register.printRegister() + ")"
			else: return str(self.offset) + "(" + self.register.printRegister() + ")"

class ConstantValue():
	__metaclass__ = ABCMeta

	def __init__(self,value):
		self.value = value

	def __eq__(self,other):
		return self.value == other.value

	def __hash__(self):
		return hash(str(self))

	def printValue(self):
		pass

class DecimalValue(ConstantValue):
	def __init__(self,value):
		ConstantValue(value)
		self.value = value

	def printValue(self):
		return str(self.value)

class HexaDecimalValue(ConstantValue):
	def __init__(self,value):
		ConstantValue(value)
		self.value = value

	def printValue(self):
		return "0x" + str(self.value)

class ConstantOperand(Operand):

	def __init__(self,value,size=OperandSize.ThirtyTwoBits):
		if not isinstance(value,ConstantValue):
			raise Exception("value must be of type ConstantValue.")
		self.value = value
		self.size = size

	def __repr__(self):
		return self.__class__.__name__ + "(" + self.value + "," + OperandSize.sizeToString(self.size) + ")"

	def __str__(self):
		return self.__class__.__name__ + "(" + self.value + "," + OperandSize.sizeToString(self.size) + ")"

	def __eq__(self,other):
		return self.value == other.value

	def __hash__(self):
		return hash(str(self))

	def printOperand(self):
		return "$" + self.value.printValue()

class NameOperand(Operand):

	def __init__(self,name,size=OperandSize.ThirtyTwoBits):
		self.name = name
		self.size = size

	def __repr__(self):
		return self.__class__.__name__ + "(" + self.name + "," + OperandSize.sizeToString(self.size) + ")"

	def __str__(self):
		return self.__class__.__name__ + "(" + self.name + "," + OperandSize.sizeToString(self.size) + ")"

	def __eq__(self,other):
		return self.name == other.name and self.size == other.size

	def __hash__(self):
		return hash(str(self))

	def printOperand(self):
		return self.name