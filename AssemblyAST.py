from abc import ABCMeta, abstractmethod

class Instruction(object):
	__metaclass__ = ABCMeta

	def printInstruction(self):
		pass

class AssemblyProgram(Instruction):
	def __init__(self,functions):
		self.functions = functions

	def printInstruction(self):
		globl = ".globl main\n"
		align = ".align	4, 0x90\n"
		body = ""
		for f in self.functions:
			body += f.printInstruction();
		return globl + align + body

	def __str__(self):
		string = self.__class__.__name__ + "(["
		for f in self.functions:
			string += str(f) + ","
		string += "])"
		return string

class AssemblyFunction(Instruction):
	def __init__(self,name,instructions):
		self.name = name
		self.instructions = instructions

	def printInstruction(self):
		functionName = self.name+":\n"
		functionSetup = PushInstruction(RegisterOperand("ebp"),"l").printInstruction() + MoveInstruction(RegisterOperand("esp"),RegisterOperand("ebp"),"l").printInstruction()
		functionCleanup = MoveInstruction(ConstantOperand(0),RegisterOperand("eax"),"l").printInstruction() + LeaveInstruction().printInstruction() + ReturnInstruction().printInstruction()
		body = ""
		for i in self.instructions:
			body += i.printInstruction()
		return functionName + functionSetup + body + functionCleanup

	def __str__(self):
		string = self.__class__.__name__ + "(" + str(self.name) + ",["
		for i in self.instructions:
			string += str(i) + ","
		string += "])"
		return string

class Operand(object):
	__metaclass__ = ABCMeta

class RegisterOperand(Operand):
	def __init__(self,name):
		self.name = name

	def printInstruction(self):
		return "%" + self.name

	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.name) + ")"

class ConstantOperand(Operand):
	def __init__(self,constant):
		self.constant = constant

	def printInstruction(self):
		return "$" + str(self.constant)

	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.constant) + ")"

class MemoryOperand(Operand):
	def __init__(self,register,offset=0):
		self.register = register
		self.offset = offset

	def printInstruction(self):
		o = ""
		if self.offset != 0: o = str(self.offset)

		return o + "(" + self.register.printInstruction() + ")"

	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.register) + "," + str(self.offset) + ")"

class FunctionCallOperand(Operand):
	def __init__(self,name):
		self.name = name

	def printInstruction(self):
		return self.name

	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.name) + ")"


class UnaryInstruction(Instruction):
	__metaclass__ = ABCMeta

	def __init__(self,operand):
		self.operand = operand

class CallInstruction(UnaryInstruction):
	def printInstruction(self):
		return "call " + self.operand.printInstruction() + "\n"

	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.operand) + ")"



class SpecifiedUnaryInstruction(UnaryInstruction):
	__metaclass__ = ABCMeta

	def __init__(self,operand,length):
		UnaryInstruction.__init__(self,operand)
		self.length = length

	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.operand) + "," + str(self.length) + ")"

class PushInstruction(SpecifiedUnaryInstruction):
	def printInstruction(self):
		push = "push"
		if self.length != None: push += self.length
		push += " " + self.operand.printInstruction() + "\n"
		return push

class NegativeInstruction(SpecifiedUnaryInstruction):
	def printInstruction(self):
		return "neg" + self.length + " " + self.operand.printInstruction() + "\n"

class BinaryInstruction(Instruction):
	__metaclass__ = ABCMeta

	def __init__(self,fromOperand,toOperand):
		self.fromOperand = fromOperand
		self.toOperand = toOperand

	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.fromOperand) + "," + str(self.toOperand) + ")"

class SpecifiedBinaryInstruction(BinaryInstruction):
	__metaclass__ = ABCMeta

	def __init__(self,fromOperand,toOperand,length):
		BinaryInstruction.__init__(self,fromOperand, toOperand)
		self.length = length
		self.instruction = ""

	def printInstruction(self):
		return self.instruction + self.length + " " + self.fromOperand.printInstruction() + ", " + self.toOperand.printInstruction() + "\n"

	def __str__(self):
		return self.__class__.__name__ + "(" + str(self.fromOperand) + "," + str(self.toOperand) + "," + str(self.length) + ")"

class MoveInstruction(SpecifiedBinaryInstruction):
	def __init__(self,fromOperand,toOperand,length):
		SpecifiedBinaryInstruction.__init__(self,fromOperand, toOperand, length)
		self.instruction = "mov"

class SubtractInstruction(SpecifiedBinaryInstruction):
	def __init__(self,fromOperand,toOperand,length):
		SpecifiedBinaryInstruction.__init__(self,fromOperand, toOperand, length)
		self.instruction = "sub"

class AddInstruction(SpecifiedBinaryInstruction):
	def __init__(self,fromOperand,toOperand,length):
		SpecifiedBinaryInstruction.__init__(self,fromOperand, toOperand, length)
		self.instruction = "add"


class NoOperandInstruction(Instruction):
	__metaclass__ = ABCMeta

	def __str__(self):
		return self.__class__.__name__

class LeaveInstruction(NoOperandInstruction):
	def printInstruction(self):
		return "leave\n"

class ReturnInstruction(NoOperandInstruction):
	def printInstruction(self):
		return "ret\n"


