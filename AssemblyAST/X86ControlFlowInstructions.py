from X86Instructions import *
from X86JumpInstructions import *
from X86GeneralInstructions import *
from X86Registers import *

class CompareInstruction(BinaryInstruction):
	def __init__(self,fromOperand,toOperand):
		BinaryInstruction(fromOperand,toOperand)

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.fromOperand,self.toOperand])

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction("cmp",self.fromOperand,self.toOperand,OperandSize.sizeToString(size))

class SectionHeaderInstruction(NoOperandInstruction):
	def __init__(self,name):
		self.name = name

	def __repr__(self):
		return  x86InstructionToString(self.__class__.__name__,[self.name])

	def __str__(self):
		return  x86InstructionToString(self.__class__.__name__,[self.name])

	def printInstruction(self):
		return printNoOperandX86Instruction(self.name+":")

class AssemblySection(Instruction):
	def __init__(self,sectionHeader,clusteredInstruction):
		if not isinstance(sectionHeader,SectionHeaderInstruction):
			raise Exception("Unsupported node type. sectionHeader has to be of type SectionHeaderInstruction.")
		if not isinstance(clusteredInstruction,ClusteredInstruction):
			raise Exception("Unsupported node type. clusteredInstruction has to be of type ClusteredInstruction.")
		self.sectionHeader = sectionHeader
		self.clusteredInstruction = clusteredInstruction

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.clusteredInstruction])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.clusteredInstruction])

	def printInstruction(self):
		return self.sectionHeader.printInstruction() + self.clusteredInstruction.printInstruction()

class AssemblyFunction(AssemblySection):
	def __init__(self,sectionHeader,clusteredInstruction,activationRecordSize,returnOperand):
		if activationRecordSize > 0:
			raise Exception("activationRecordSize must be less than or equal to 0.")
		if not isinstance(returnOperand,Operand):
			raise Exception("returnOperand must be a type of Operand.")
		AssemblySection(sectionHeader,clusteredInstruction)
		self.activationRecordSize = activationRecordSize
		self.returnOperand = returnOperand

		pushEbp = PushInstruction(Registers32.EBP)
		moveEspIntoEbp = MoveInstruction(Registers32.ESP,Registers32.EBP)
		createActivationStack = SubtractIntegerInstruction(ConstantOperand(DecimalValue(activationRecordSize)),Registers32.ESP)

		self.functionSetup = ClusteredInstruction([pushEbp,moveEspIntoEbp,createActivationStack])


		returnValue = MoveInstruction(returnOperand,Registers32.EAX)
		leave = LeaveInstruction()
		ret = ReturnInstruction()

		self.functionCleanup = ClusteredInstruction([returnValue,leave,ret])
		self.function = ClusteredInstruction([sectionHeader,self.functionSetup,clusteredInstruction,self.functionCleanup])

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.function])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.function])

	def printInstruction(self):
		return self.function.printInstruction()













