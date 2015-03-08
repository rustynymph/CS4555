from X86Instructions import *

class AddIntegerInstruction(BinaryInstruction):
	def __init__(self,fromOperand,toOperand):
		BinaryInstruction(fromOperand,toOperand)

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("add",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class SubtractIntegerInstruction(BinaryInstruction):
	def __init__(self,fromOperand,toOperand):
		BinaryInstruction(fromOperand,toOperand)

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("sub",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class NegativeInstruction(UnaryInstruction):
	def __init__(self,operand):
		if isinstance(operand,ConstantOperand):
			raise Exception("NegativeInstruction cannot perform negation on " + operand.__class__.__name__)
		self.operand = operand

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def printInstruction(self):
		size = self.operand.size
		return printUnaryX86Instruction("neg",self.operand,OperandSize.sizeToString(size))

class AndInstruction(BinaryInstruction):
	def __init__(self,fromOperand,toOperand):
		BinaryInstruction(fromOperand,toOperand)

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("and",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class OrInstruction(BinaryInstruction):
	def __init__(self,fromOperand,toOperand):
		BinaryInstruction(fromOperand,toOperand)

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("or",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class NotInstruction(UnaryInstruction):
	def __init__(self,operand):
		self.operand = operand

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("not",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class ShiftInstruction(BinaryInstruction):
	__metaclass__ = ABCMeta

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

class ShiftRightInstruction(ShiftInstruction):
	def __init__(self,fromOperand,toOperand):
		ShiftInstruction(fromOperand,toOperand)

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("shr",self.fromOperand.self.toOperand,OperandSize.sizeToString(size))

class ShiftArithmeticRightInstruction(ShiftRightInstruction):
	def __init__(self,fromOperand,toOperand):
		ShiftRightInstruction(fromOperand,toOperand)

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("sar",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class ShiftLeftInstruction(ShiftInstruction):
	def __init__(self,fromOperand,toOperand):
		ShiftInstruction(fromOperand,toOperand)

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("shl",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class ShiftArithmeticLeftInstruction(ShiftLeftInstruction):
	def __init__(self,fromOperand,toOperand):
		ShiftLeftInstruction(fromOperand,toOperand)

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("sal",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))