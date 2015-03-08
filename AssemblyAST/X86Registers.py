class RegisterSize:
	SixtyFourBits = 64
	ThirtyTwoBits = 32
	SixteenBits = 16
	EightBits = 8

	@staticmethod
	def sizeToString(size):
		if RegisterSize.SixtyFourBits == size: return "qw"
		elif RegisterSize.ThirtyTwoBits == size: return "l"
		elif RegisterSize.SixteenBits == size: return "w"
		elif RegisterSize.EightBits == size: return "b"
		elif None == size: return ""
		else: raise Exception(str(size) + " is not a valid operand size.")

class Register():
	def __init__(self,name,size):
		self.name = name
		self.size = size

	def __eq__(self,other):
		return isinstance(other,self.__class__) and other.name == self.name

	def __repr__(self):
		return self.__class__.__name__ + "(" + self.name + "," + RegisterSize.sizeToString(self.size) + ")"

	def printRegister(self):
		return "%" + self.name

class CalleeSavedRegister(Register):
	def __init__(self,name,size):
		Register(name,size)

class CallerSavedRegister(Register):
	def __init__(self,name,size):
		Register(name,size)

class Registers8():
	AH = Register("ah",RegisterSize.EightBits)
	AL = Register("al",RegisterSize.EightBits)
	CH = Register("ch",RegisterSize.EightBits)
	CL = Register("cl",RegisterSize.EightBits)
	DH = Register("dh",RegisterSize.EightBits)
	DL = Register("dl",RegisterSize.EightBits)
	BH = Register("bh",RegisterSize.EightBits)
	BL = Register("bl",RegisterSize.EightBits)

class Registers16(Registers8):
	AX = Register("eax",RegisterSize.SixteenBits)
	CX = Register("ecx",RegisterSize.SixteenBits)
	DX = Register("edx",RegisterSize.SixteenBits)
	BX = Register("ebx",RegisterSize.SixteenBits)
	SP = Register("esp",RegisterSize.SixteenBits)
	BP = Register("ebp",RegisterSize.SixteenBits)
	SI = Register("esi",RegisterSize.SixteenBits)
	DI = Register("edi",RegisterSize.SixteenBits)

class Registers32(Registers16):
	EAX = Register("eax",RegisterSize.ThirtyTwoBits)
	ECX = Register("ecx",RegisterSize.ThirtyTwoBits)
	EDX = Register("edx",RegisterSize.ThirtyTwoBits)
	EBX = Register("ebx",RegisterSize.ThirtyTwoBits)
	ESP = Register("esp",RegisterSize.ThirtyTwoBits)
	EBP = Register("ebp",RegisterSize.ThirtyTwoBits)
	ESI = Register("esi",RegisterSize.ThirtyTwoBits)
	EDI = Register("edi",RegisterSize.ThirtyTwoBits)

class Registers64(Registers32):
	RAX = Register("rax",RegisterSize.SixtyFourBits)
	RCX = Register("rcx",RegisterSize.SixtyFourBits)
	RDX = Register("rdx",RegisterSize.SixtyFourBits)
	RBX = Register("rbx",RegisterSize.SixtyFourBits)
	RSP = Register("rsp",RegisterSize.SixtyFourBits)
	RBP = Register("rbp",RegisterSize.SixtyFourBits)
	RSI = Register("rsi",RegisterSize.SixtyFourBits)
	RDI = Register("rdi",RegisterSize.SixtyFourBits)
	R8  = Register("r8",RegisterSize.SixtyFourBits)
	R9  = Register("r9",RegisterSize.SixtyFourBits)
	R10 = Register("r10",RegisterSize.SixtyFourBits)
	R11 = Register("r11",RegisterSize.SixtyFourBits)
	R12 = Register("r12",RegisterSize.SixtyFourBits)
	R13 = Register("r13",RegisterSize.SixtyFourBits)
	R14 = Register("r14",RegisterSize.SixtyFourBits)
	R15 = Register("r15",RegisterSize.SixtyFourBits)