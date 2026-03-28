import sys
program_memory = {x:0 for x in range(0x0,0xFF+1,4)}
stack_memory = {x:0 for x in range(0x100,0x17F + 1,4)}
data_memory = {x:0 for x in range(0x10000,0x1007F+1,4)}
register_file = {x: 0 for x in range(0,32)}
register_file[2] = 0x0000017C #stack pointer init
opcode_control_dict= {
    #R-type(add, sub, and, or, etc.)
    "0110011": ("1", "_", "0", "0", "00", "0", "10", "0"),

    #I-type(addi, sltui)
    "0010011": ("1", "000", "1", "0", "00", "0", "10", "0"),

    #Load(lw)
    "0000011": ("1", "000", "1", "0", "01", "0", "00", "0"),

    #Store(sw)
    "0100011": ("0", "001", "1", "1", "_", "0", "00", "0"),

    #Branch(beq, bne, blt, bge, bltu, bgeu)
    "1100011": ("0", "011", "0", "0", "_", "1", "_", "0"),

    #JAL
    "1101111": ("1", "010", "_", "0", "10", "0", "_", "1"),

    #JALR
    "1100111": ("1", "000", "1", "0", "10", "0", "00", "1"),

    #LUI
    "0110111": ("1", "100", "_", "0", "11", "0", "_", "0"),

    #AUIPC
    "0010111": ("1", "100", "1", "0", "11", "0", "00", "0"),
}
class control_signal:
    def __init__(self,instruction,address):
        self.address = address
        self.REGWRITE = opcode_control_dict[instruction.opcode][0]
        self.IMMSRC = opcode_control_dict[instruction.opcode][1]
        self.ALUSRC = opcode_control_dict[instruction.opcode][2]
        self.MEMWRITE = opcode_control_dict[instruction.opcode][3]
        self.RESULTSRC = opcode_control_dict[instruction.opcode][4]
        self.BRANCH = bool(int(opcode_control_dict[instruction.opcode][5]))
        self.ALUOP = opcode_control_dict[instruction.opcode][6]
        self.JUMP = bool(int(opcode_control_dict[instruction.opcode][7]))
        self.gteu = None
        self.zero = None
        self.gte = None
        self.PCSRC = None
    def PCSRC_gen(self,instruction):
        flag = None
        self.PCSRC = bool(self.JUMP)
        if instruction.funct3 == "000":
            self.PCSRC = bool((self.BRANCH*self.zero) + self.JUMP)
        elif instruction.funct3 == "001":
            self.PCSRC = bool((not(self.zero)*self.BRANCH) + self.JUMP)
        elif instruction.funct3 == "100":
            self.PCSRC = bool((not(self.gte)*self.BRANCH)+self.JUMP)
        elif instruction.funct3 == "101":
            self.PCSRC = bool((self.gte*self.BRANCH)+self.JUMP)
        elif instruction.funct3 == "110":
            self.PCSRC = bool((not(self.gteu)*self.BRANCH)+self.JUMP)
        elif instruction.funct3 == "111":
            self.PCSRC = bool((self.gteu*self.BRANCH)+self.JUMP)
class Instruction:
    def __init__(self,binary_instruction,address): #instruction class will itself carry all of its results, so that calling a function only requires instruction as an attribute. Since fetch,decode,execute,memory,writeback will be called for every instruction, these attributes will eventually be assigned a value
        self.address = address
        self.opcode = binary_instruction[25:]
        self.funct3 = binary_instruction[17:20]
        self.funct7 = binary_instruction[0:7]
        self.rs1 = binary_instruction[12:17]
        self.rs2 = binary_instruction[7:12]
        self.rd = binary_instruction[20:25]
        self.imm_ex = binary_instruction[0:24] #input to immediate extender
        self.control_signals = control_signal(self,address)
        self.ALURESULT = None
        self.PCplustarget = None
        self.PCplusfour = None
        self.read_data = None
    def immediate_extend(self): #Use IMMSRC to ascertain how immediate is to be generated. IN the case of R-Type, simply return the integer zero
        {}
    def ALU_decoder(self):
        op5f75 = (self.opcode[2]+ self.funct7[2])
        if self.control_signals.ALUOP == "00":
            return("ADD")
        elif self.control_signals.ALUOP == "01":
            return("SUB")
        elif self.control_signals.ALUOP == "10":
            if self.funct3 == "010":
                return("SLT")
            elif self.funct3 == "110":
                return("OR")
            elif self.funct3 == "111":
                return("AND")
            elif self.funct3 == "001":
                return("SLL")
            elif self.funct3 == "011":
                return("SLTU")
            elif self.funct3 == "100":
                return("XOR")
            elif self.funct3 == "101":
                return("SRL")
            elif self.funct3 == "000" and (op5f75 == "00" or op5f75 == "01" or op5f75=="10"):
                return("ADD")
            elif self.funct3 == "000" and (op5f75 == "11"):
                return("SUB")
        elif self.control_signals.ALUOP=="_":
            return("DO NOTHING")
        else:
            raise ValueError
    def ADD(self,a,b): #a-rs1,b-rs2 
        return(a+b)
    def SUB(self,a,b):
        return(a-b)
    def XOR(self,a,b):
        return(a^b)
    def SRL(self,a,b):
        return((a & 0xFFFFFFFF) >> (b & 0x1F))
    def SLL(self,a,b):
        return ((a & 0xFFFFFFFF) << (b & 0x1F)) & 0xFFFFFFFF
    def SLTU(self,a,b):
        if a<b:
            return(1)
        else:
            return(0)
    def OR(self,a,b):
        return(a|b)
    def AND(self,a,b):
        return(a&b)
    def SLT(self,a,b):
        if a<b:
            return(1)
        else:
            return(0)
    operations = {"ADD":ADD,"SUB":SUB,"XOR":XOR,"SRL":SRL,"SLL":SLL,"SLTU":SLTU,"OR":OR,"AND":AND,"SLT":SLT}
    def ALU(self): #ALU function has to do the following- generate the zero,gteu,gte flags for every instruction,use ALU decoder to find the operation, and its sources, and store the result as the attribute ALURESULT
        {}
    def Memory_read_write(self):#Use the MEMWRITE attribute to ascertain whether data is to be written and load data from memory address(data_memory and stack_memory) into read_data attribute of instruction(WARNING: ensure addresses are positive and within bounds)
        {} 
    def register_write_back(self): #Write to register file if REGWRITE = "1"
        {}
def fetch(binary_string,instruction_num):
    inst = Instruction(binary_string,instruction_num*(4))
    return(inst)