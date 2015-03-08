from X86Instructions import *

class JumpPredicate():
	def __init__(self,name):
		self.name = name

	def __repr__(self):
		return self.name

	def __str__(self):
		return self.name

class JumpPredicateEnum():
	NONE = JumpPredicate("jmp")
	ZERO = JumpPredicate("jz")
	NOTZERO = JumpPredicate("jnz")
	NEGATIVE = JumpPredicate("js")
	NOTNEGATIVE = JumpPredicate("jns")
	OVERFLOW = JumpPredicate("jo")
	NOTOVERFLOW = JumpPredicate("jno")
	CARRY = JumpPredicate("jc")
	NOTCARRY = JumpPredicate("jnc")
	BORROW = JumpPredicate("jb")
	NOTBORROW = JumpPredicate("jae")
	BORROWORZERO = JumpPredicate("jbe")
	NOTBORROWNOTZERO = JumpPredicate("ja")
	SIGNEDLESS = JumpPredicate("jl")
	SIGNEDLESSOREQUAL = JumpPredicate("jle")
	SIGNEDGREATER = JumpPredicate("jg")
	SIGNEDGREATEROREQUAL = JumpPredicate("jge")

class JumpInstruction(BinaryInstruction):
	def __init__(self,fromOperand,toOperand,predicate=JumpPredicateEnum.NONE):
		if not isinstance(predicate,JumpPredicate):
			raise Exception("predicate must be JumpPredicate.")
		BinaryInstruction(fromOperand,toOperand)
		self.predicate = predicate

	def __repr__(self):
		return x86InstructionToString(self.__class__.__name__,[self.predicate,self.fromOperand,self.toOperand])

	def __str__(self):
		return x86InstructionToString(self.__class__.__name__,[self.predicate,self.fromOperand,self.toOperand])

	def printInstruction(self):
		size = getMinSizeFromOperands(self.fromOperand,self.toOperand)
		return printBinaryX86Instruction(self.predicate.name,self.fromOperand,self.toOperand,OperandSize.sizeToString(size))
