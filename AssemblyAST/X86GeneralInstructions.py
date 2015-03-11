from X86Instructions import *

class AssemblyProgram(Instruction):
	def __init__(self,entryPoint,instructions):
		if not isinstance(entryPoint,EntryPointInstruction):
			raise Exception("entryPoint must be an EntryPointInstruction.")
		if not isinstance(instructions,ClusteredInstruction):
			raise Exception("instructions must be a ClusteredInstruction.")
		self.entryPoint = entryPoint
		self.instructions = instructions

		self.align = AlignInstruction(ConstantOperand(DecimalValue(4)),ConstantOperand(HexaDecimalValue("90")))

		self.program = ClusteredInstruction([entryPoint,self.align,instructions])

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.entryPoint,self.instructions])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.entryPoint,self.instructions])

	def printInstruction(self):
		return self.program.printInstruction()

class ClusteredInstruction(Instruction):
	def __init__(self,nodes=[]):
		self.nodes = nodes

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.nodes])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.nodes])

	def printInstruction(self):
		instructionString = ""
		for n in self.nodes:
			instructionString += n.printInstruction()
		return instructionString

class AlignInstruction(BinaryInstruction):
	def __init__(self,fromOperand,toOperand):
		if not isinstance(fromOperand,ConstantOperand) or not isinstance(toOperand,ConstantOperand):
			raise Exception("operands for AlignInstruction must be ConstantOperand's")
		self.fromOperand = fromOperand
		self.toOperand = toOperand

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def printInstruction(self):
		return printBinaryX86Instruction(".align", self.fromOperand, self.toOperand)

class EntryPointInstruction(UnaryInstruction):
	def __init__(self,operand):
		if not isinstance(operand,NameOperand):
			raise Exception("operand must be of type NameOperand.")
		self.operand = operand

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def printInstruction(self):
		return printUnaryX86Instruction(".globl",self.operand)

class CallInstruction(UnaryInstruction):
	def __init__(self,operand):
		if not isinstance(operand,NameOperand): 
			raise Exception(operand.__class__.__name__ + " is an unsupported class. operand must be of type NameOperand.")
		self.operand = operand

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def printInstruction(self):
		size = self.operand.size
		return printUnaryX86Instruction("call",self.operand,"")

class MoveInstruction(BinaryInstruction):
	def __init__(self,fromOperand,toOperand):
		BinaryInstruction(fromOperand,toOperand)
		self.fromOperand = fromOperand
		self.toOperand = toOperand

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("mov",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class PushInstruction(UnaryInstruction):
	def __init__(self,operand):
		self.operand = operand

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def printInstruction(self):
		size = self.operand.size
		return printUnaryX86Instruction("push",self.operand,OperandSize.sizeToString(size))

class PopInstruction(UnaryInstruction):
	def __init__(self,operand):
		if isinstance(operand,ConstantOperand):
			raise Exception("Cannot pop to a " + operand.__class__.__name__)
		self.operand = operand

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.operand])

	def printInstruction(self):
		size = self.operand.size
		return printUnaryX86Instruction("pop",self.operand,OperandSize.sizeToString(size))

class ReturnInstruction(NoOperandInstruction):
	def __init__(self):
		pass

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[])

	def printInstruction(self):
		return printNoOperandX86Instruction("ret")

class LeaveInstruction(NoOperandInstruction):
	def __init__(self):
		pass

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[])

	def printInstruction(self):
		return printNoOperandX86Instruction("leave")
