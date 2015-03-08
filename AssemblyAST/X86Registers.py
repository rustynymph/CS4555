class RegisterSize:
	SixtyFourBits = 64
	ThirtyTwoBits = 32
	SixteenBits = 16
	EightBits = 8

	@staticmethod
	def sizeToString(size):
		if RegisterSize.SixtyFourBits == size: return "q"
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

class ArguementRegister(Register):
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
	EAX = CallerSavedRegister("eax",RegisterSize.ThirtyTwoBits)
	ECX = CallerSavedRegister("ecx",RegisterSize.ThirtyTwoBits)
	EDX = CallerSavedRegister("edx",RegisterSize.ThirtyTwoBits)
	EBX = CalleeSavedRegister("ebx",RegisterSize.ThirtyTwoBits)
	ESI = CalleeSavedRegister("esi",RegisterSize.ThirtyTwoBits)
	EDI = CalleeSavedRegister("edi",RegisterSize.ThirtyTwoBits)
	ESP = Register("esp",RegisterSize.ThirtyTwoBits)
	EBP = Register("ebp",RegisterSize.ThirtyTwoBits)
	

class Registers64(Registers32):
	RAX = CallerSavedRegister("rax",RegisterSize.SixtyFourBits)
	RCX = ArguementRegister("rcx",RegisterSize.SixtyFourBits)
	RDX = ArguementRegister("rdx",RegisterSize.SixtyFourBits)
	RBX = CalleeSavedRegister("rbx",RegisterSize.SixtyFourBits)
	RSP = Register("rsp",RegisterSize.SixtyFourBits)
	RBP = Register("rbp",RegisterSize.SixtyFourBits)
	RSI = ArguementRegister("rsi",RegisterSize.SixtyFourBits)
	RDI = ArguementRegister("rdi",RegisterSize.SixtyFourBits)
	R8  = ArguementRegister("r8",RegisterSize.SixtyFourBits)
	R9  = ArguementRegister("r9",RegisterSize.SixtyFourBits)
	R10 = CallerSavedRegister("r10",RegisterSize.SixtyFourBits)
	R11 = CallerSavedRegister("r11",RegisterSize.SixtyFourBits)
	R12 = CalleeSavedRegister("r12",RegisterSize.SixtyFourBits)
	R13 = CalleeSavedRegister("r13",RegisterSize.SixtyFourBits)
	R14 = CalleeSavedRegister("r14",RegisterSize.SixtyFourBits)
	R15 = CalleeSavedRegister("r15",RegisterSize.SixtyFourBits)