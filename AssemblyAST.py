from abc import ABCMeta, abstractmethod

class Instruction(object):
	__metaclass__ = ABCMeta

	def printInstruction(self):
		pass

class AssemblyProgram(Instruction):
	def __init__(self,functions):
		self.functions = functions

	def printInstruction(self):
		section = ".section	__TEXT,__text,regular,pure_instructions\n"
		globl = ".globl main\n"
		align = ".align	4, 0x90\n"
		body = ""
		for f in self.functions:
			body += f.printInstruction();
		return section + globl + align + body

class AssemblyFunction(Instruction):
	def __init__(self,name,instructions):
		self.name = name
		self.instructions = instructions

	def printInstruction(self):
		functionName = self.name+":\n"
		functionSetup = PushInstruction("ebp").printInstruction() + MoveInstruction(RegisterOperand("esp"),RegisterOperand("ebp"),"l").printInstruction()
		functionCleanup = MoveInstruction(ConstantOperand(0),RegisterOperand("eax"),"l").printInstruction() + LeaveInstruction().printInstruction() + ReturnInstruction().printInstruction()
		body = ""
		for i in self.instructions:
			body += i.printInstruction()
		return functionName + functionSetup + body + functionCleanup

class Operand(object):
	__metaclass__ = ABCMeta

class RegisterOperand(Operand):
	def __init__(self,name):
		self.name = name

	def printInstruction(self):
		return "%" + self.name

class ConstantOperand(Operand):
	def __init__(self,constant):
		self.constant = constant

	def printInstruction(self):
		return "$" + str(self.constant)

class MemoryOperand(Operand):
	def __init__(self,register,offset=0):
		self.register = register
		self.offset = offset

	def printInstruction(self):
		o = ""
		if self.offset != 0: o = str(self.offset)

		return o + "(" + self.register.printInstruction() + ")"

class FunctionCallOperand(Operand):
	def __init__(self,name):
		self.name = name

	def printInstruction(self):
		return self.name

class UnaryInstruction(Instruction):
	__metaclass__ = ABCMeta

	def __init__(self,operand):
		self.operand = operand

class CallInstruction(UnaryInstruction):
	def printInstruction(self):
		return "call " + self.operand.printInstruction() + "\n"

class PushInstruction(UnaryInstruction):
	def __init__(self,operand,length=None):
		UnaryInstruction.__init__(self,operand)
		self.length = length

	def printInstruction(self):
		push = "push"
		if self.length != None: push += self.length
		push += " " + self.operand.printInstruction() + "\n"
		return push

class SpecifiedUnaryInstruction(UnaryInstruction):
	__metaclass__ = ABCMeta

	def __init__(self,operand,length):
		UnaryInstruction.__init__(self,operand)
		self.length = length

class NegativeInstruction(SpecifiedUnaryInstruction):
	def printInstruction(self):
		return "neg" + self.length + " " + self.operand.printInstruction() + "\n"

class BinaryInstruction(Instruction):
	__metaclass__ = ABCMeta

	def __init__(self,fromOperand,toOperand):
		self.fromOperand = fromOperand
		self.toOperand = toOperand

class SpecifiedBinaryInstruction(BinaryInstruction):
	__metaclass__ = ABCMeta

	def __init__(self,fromOperand,toOperand,length):
		BinaryInstruction.__init__(self,fromOperand, toOperand)
		self.length = length
		self.instruction = ""

	def printInstruction(self):
		return self.instruction + self.length + " " + self.fromOperand.printInstruction() + ", " + self.toOperand.printInstruction() + "\n"

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

class LeaveInstruction(NoOperandInstruction):
	def printInstruction(self):
		return "leave\n"

class ReturnInstruction(NoOperandInstruction):
	def printInstruction(self):
		return "ret\n"


