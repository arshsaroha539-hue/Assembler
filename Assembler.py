import string
import sys
class Instruction:
    def __init__(self,instructionType="",instructionParams = None,label=""):
        self.label = label
        self.instructionType = instructionType
        if instructionParams == None:
            instructionParams = []
        self.instructionParams = instructionParams
    def __eq__(self, value):
        return self.label == value.label and self.instructionType == value.instructionType and self.instructionParams == value.instructionParams

_DEFAULT_INSTRUCTION = Instruction()
_VALID_SET_FOR_LABEL = set(string.ascii_lowercase).union(set(string.ascii_uppercase)).union("_")

class Lexer:
    def __init__(self):
        self._instructions = []
        pass

    def appendInstruction(self,instruction,line_num):
        self._instructions.append((line_num,instruction))

    def parseInstructionTypeAndParams(self,instruction,line_num):
        parsedInstruction = instruction.strip().split()
        intermediateInstruction = instruction.strip()
        if intermediateInstruction == "":
            return("",[])
        parsedInstruction = intermediateInstruction.split()
        if len(parsedInstruction) < 2:
            raise ValueError(f"Error in line no. {line_num}:Invalid instruciton")
        else:
            instructionType = parsedInstruction[0]
            instructionParamsStr = "".join(parsedInstruction[1:])
            instructionParams = list(map(lambda x: x.strip(), instructionParamsStr.strip().split(",")))
            return instructionType,instructionParams

    def parseInstructionWithLabel(self,instruction,line_num):
        inputWithLabel = instruction.strip().split(":")
        if len(inputWithLabel) > 2:
            raise ValueError(f"Error in line no. {line_num}:Multiple labels detected")
        label = ""
        instructionWithoutLabel = ""
        if len(inputWithLabel) == 1:
            instructionWithoutLabel = inputWithLabel[0]
        else:
            figuredLabel = inputWithLabel[0]
            if figuredLabel[0] in _VALID_SET_FOR_LABEL:
                label = figuredLabel
            else:
                raise ValueError(f"Error in line no.{line_num}:Label must begin with valid characters")
            if " " in figuredLabel:
                raise ValueError(f"Error in line no. {line_num}:Label cannot contain whitespaces")
            instructionWithoutLabel = inputWithLabel[1]
        instructionType,instructionParams = self.parseInstructionTypeAndParams(instructionWithoutLabel,line_num)
        return Instruction(instructionType,instructionParams,label)
    
    def parseInputLine(self,line,line_num):
        commentsWithInput = line.strip().split("#")
        parsedInstruction = self.parseInstructionWithLabel(commentsWithInput[0],line_num)
        self.appendInstruction(parsedInstruction,line_num)
    
    def getInstructions(self):
        return self._instructions
def lexer_output(file_name):
    lexer = Lexer()
    line_num = 1
    with open(file_name,"r") as f:
        for line in f.readlines():
            lexer.parseInputLine(line,line_num)
            line_num = line_num+1
    instruction_list = []
    for line_num,ins in lexer.getInstructions():
        if (ins.label or ins.instructionType):
            if ins.label != "" and ins.instructionType != "":
                instruction_list.append((line_num,[f"{ins.label}:"]+[ins.instructionType]+ins.instructionParams))
            elif ins.label != "" and ins.instructionType == "":
                instruction_list.append((line_num,[f"{ins.label}:"]))
            else:
                instruction_list.append((line_num,[ins.instructionType]+ins.instructionParams))
    return(instruction_list)
mnemonic_dict ={

    #R_Type
    "add":  {"type": "R", "funct7": "0000000", "funct3": "000", "opcode": "0110011"},
    "sub":  {"type": "R", "funct7": "0100000", "funct3": "000", "opcode": "0110011"},
    "sll":  {"type": "R", "funct7": "0000000", "funct3": "001", "opcode": "0110011"},
    "slt":  {"type": "R", "funct7": "0000000", "funct3": "010", "opcode": "0110011"},
    "sltu": {"type": "R", "funct7": "0000000", "funct3": "011", "opcode": "0110011"},
    "xor":  {"type": "R", "funct7": "0000000", "funct3": "100", "opcode": "0110011"},
    "srl":  {"type": "R", "funct7": "0000000", "funct3": "101", "opcode": "0110011"},
    "or":   {"type": "R", "funct7": "0000000", "funct3": "110", "opcode": "0110011"},
    "and":  {"type": "R", "funct7": "0000000", "funct3": "111", "opcode": "0110011"},
    #I_Type
    "lw":    {"type": "I_load", "funct3": "010", "opcode": "0000011"},
    "addi":  {"type": "I_arith/logic", "funct3": "000", "opcode": "0010011"},
    "sltiu": {"type": "I_arith/logic", "funct3": "011", "opcode": "0010011"},
    "jalr":  {"type": "I_jalr", "funct3": "000", "opcode": "1100111"},
    #S_Type
    "sw": {"type": "S", "funct3": "010", "opcode": "0100011"},
    #B_Type
    "beq": {"type": "B", "funct3": "000", "opcode": "1100011"},
    "bne": {"type": "B", "funct3": "001", "opcode": "1100011"},
    "blt": {"type": "B", "funct3": "100", "opcode": "1100011"},
    "bge": {"type": "B", "funct3": "101", "opcode": "1100011"},
    "bltu": {"type": "B", "funct3": "110", "opcode": "1100011"},
    "bgeu": {"type": "B", "funct3": "111", "opcode": "1100011"},
    #U_Type
    "lui":   {"type": "U", "opcode": "0110111"},
    "auipc": {"type": "U", "opcode": "0010111"},
    #J_Type
    "jal": {"type": "J", "opcode": "1101111"},
}
register_name_dict = {}
for i in range(32):
    register_name_dict[f"x{i}"] = "{:05b}".format(i)
ABI_register_dict = {
    #ABI names
    "zero":"00000",
    "ra":"00001",
    "sp":"00010",
    "gp":"00011",
    "tp":"00100",
    "t0":"00101",
    "t1":"00110",
    "t2":"00111",
    "s0":"01000",
    "fp":"01000",
    "s1":"01001",
    "a0":"01010",
    "a1":"01011",
    "a2":"01100",
    "a3":"01101",
    "a4":"01110",
    "a5":"01111",
    "a6":"10000",
    "a7":"10001",
    "s2":"10010",
    "s3":"10011",
    "s4":"10100",
    "s5":"10101",
    "s6":"10110",
    "s7":"10111",
    "s8":"11000",
    "s9":"11001",
    "s10":"11010",
    "s11":"11011",
    "t3":"11100",
    "t4":"11101",
    "t5":"11110",
    "t6":"11111",
}
type_operands_dict = {

    "R": {
        "operand_count": 3
    },

    "I_arith/logic": {
        "operand_count": 3
    },

    "I_load": {
        "operand_count": 2
    },

    "I_jalr": {
        "operand_count": 3
    },

    "S": {
        "operand_count": 2 #treating imm(rs1) as one operand for error detection convenience
    },

    "B": {
        "operand_count": 3
    },

    "U": {
        "operand_count": 2
    },

    "J": {
        "operand_count": 2
    }
}
def pass1(instruction_list):
    label_address_dict = {}
    address_list = []
    address = 0
    for line_num,instructions in instruction_list:
        if(instructions[0][-1] != ":"): #If Instruction does not have labels.
            address_list.append((address,line_num,instructions))
            if address+4 >= 0x100:
                raise ValueError(f"Error in line no.{line_num}:Program memory exceeded")
            address = address+4
        else:
            if len(instructions) == 1: #Instructions which are only of the form label: with nothing else after that in the same line
                label_name = instructions[0]
                label_name = label_name[:-1] #remove the semicolon
                if label_name in label_address_dict:
                    raise ValueError(f"Error line no: {line_num}:Cannot Reuse Label Names")
                label_address_dict[label_name] = address
            else: #When the instruction is of the form label:{instruction}
                label_name = instructions[0]
                label_name = label_name[:-1] #remove the semicolon
                if label_name in label_address_dict:
                    raise ValueError(f"Error line no: {line_num}:Cannot Reuse Label Names")
                label_address_dict[label_name] = address 
                address_list.append((address,line_num,instructions[1:]))
                if address+4 >= 0x100:
                    raise ValueError(f"Error in line no.{line_num}:Program memory exceeded")
                address = address + 4
    return(address_list,label_address_dict)
def R_Type_operand_check(instruction,label_address_dict,address_list,line_num,address):
    operands = [instruction[1],instruction[2],instruction[3]] #rd,rs1,rs2
    for operand in operands:
        if operand not in ABI_register_dict and operand not in register_name_dict:
            raise ValueError(f"Error in line no. {line_num}:Unrecognised operands")
def I_Type_operand_check(instruction,label_address_dict,address_list,line_num,address):
    #I type, arith: mnemonic rd,rs1,imm
    #I type, load: lw rd,imm(rs1)
    #I type, jalr: jalr rd,rs1,offset
    mnemonic = instruction[0]
    mnem_type = mnemonic_dict[mnemonic]["type"]
    if type_operands_dict[mnem_type]["operand_count"] == 3:
        reg_ops = [instruction[1],instruction[2]]
        imm_ops = instruction[3]
        for reg in reg_ops:
                if reg not in ABI_register_dict and reg not in register_name_dict:
                    raise ValueError(f"Error in line no. {line_num}:Unrecognised operand")
        try:
            int(imm_ops)
        except:
            raise ValueError(f"Error in line no. {line_num}:Immediate field requires 12 bit integer input")
        if not(-2048<=int(imm_ops)<=2047):
            raise ValueError(f"Error in line no. {line_num}:Immediate out of range")
    else:
        operands = [instruction[1],instruction[2]]
        if operands[1].count("(") != 1 or operands[1].count(")") != 1:
            raise ValueError(f"Error in line no. {line_num}:Invalid syntax for lw instruction")
        x = operands[1].index("(")
        y = operands[1].index(")")
        if x>y:
            raise ValueError(f"Error in line no. {line_num}:Invalid syntax for lw instruction")
        if x==0:
            raise ValueError(f"Error in line no. {line_num}:Immediate absent")
        if y == x+1:
            raise ValueError(f"Error in line no. {line_num}:Source register absent")
        try:
            immediate = int(operands[1][0:x])
        except:
            raise ValueError(f"Error in line no. {line_num}:Immediate field requires 12 bit integer input")
        if not(-2048<=int(immediate)<=2047):
            raise ValueError(f"Error in line no. {line_num}:Immediate out of bounds")
        rs1 = operands[1][x+1:y]
        rd = operands[0]
        if rs1 not in ABI_register_dict and rs1 not in register_name_dict:
            raise ValueError(f"Error in line no. {line_num}:Register not found")
        if rd not in ABI_register_dict and rd not in register_name_dict:
            raise ValueError(f"Error in line no. {line_num}:Register not found")
def J_Type_operand_check(instruction,label_address_dict,address_list,line_num,address):#COPIED ADDRESS LIST IS BEING PASSED
    rd = instruction[1]
    imm_label = instruction[2]
    if rd not in ABI_register_dict and rd not in register_name_dict:
        raise ValueError(f"Error in line no. {line_num}:Register not found")
    imm = ''
    try:
        imm = int(imm_label)
    except:
        label = imm_label
        if label not in label_address_dict:
            raise ValueError(f"Error in line no. {line_num}:Label not found")
        offset = label_address_dict[label] - address
        idx = address_list.index((address,line_num,instruction))
        instruction[2] = str(offset)
        address_list[idx] = (address,line_num,instruction)
    if imm != '':
        if not(-(2**(20))<=imm<= 2**(20)-2):
            raise ValueError(f"Error in line no. {line_num}:Immediate out of bounds")
        if abs(imm)%2 == 1:
            raise ValueError(f"Error in line no. {line_num}:Immediate must be a multiple of 2")
def U_Type_operand_check(instruction,label_address_dict,address_list,line_num,address):
    rd = instruction[1]
    imm = instruction[2]
    if rd not in ABI_register_dict and rd not in register_name_dict:
        raise ValueError(f"Error in line no. {line_num}:Register not found")
    try:
        imm = int(imm)
    except:
        raise ValueError(f"Error in line no. {line_num}:Immediate must be a 20 bit integer")
    if not(0<=int(imm)<=(2**(20)-1)):
        raise ValueError(f"Error in line no. {line_num}:Immediate out of bounds")
def B_Type_operand_check(instruction,label_address_dict,address_list,line_num,address): #copied address list will be passed into this function
    #B-type syntax: instruction rs1, rs2, label/imm
    reg_ops = [instruction[1],instruction[2]]
    imm_label_ops = instruction[3]
    for reg in reg_ops:
        if reg not in ABI_register_dict and reg not in register_name_dict:
            raise ValueError(f"Error in line no. {line_num}:Register not found")
    imm = ''
    try:
        imm = int(imm_label_ops)
    except:
        label = imm_label_ops
        if label not in label_address_dict:
            raise ValueError(f"Error in line no. {line_num}:Label not found")
        offset = label_address_dict[label] - address
        idx = address_list.index((address,line_num,instruction))
        instruction[3] = str(offset)
        address_list[idx] = (address,line_num,instruction)
    if imm != '':
        if not(-4096<=imm<=4094):
            raise ValueError(f"Error in line no. {line_num}:Immediate out of bounds")
        if abs(imm)%2 == 1:
            raise ValueError(f"Error in line no. {line_num}:Immediate must be an even number")
def S_Type_operand_check(instruction,label_address_dict,address_list,line_num,address):
    operands = [instruction[1],instruction[2]]
    if operands[1].count("(") != 1 or operands[1].count(")") != 1:
        raise ValueError(f"Error in line no. {line_num}:Invalid syntax for sw instruction")
    x = operands[1].index("(")
    y = operands[1].index(")")
    if x>y:
        raise ValueError(f"Error in line no. {line_num}:Invalid syntax for sw instruction")
    if x==0:
        raise ValueError(f"Error in line no. {line_num}:Immediate absent")
    if y == x+1:
        raise ValueError(f"Error in line no. {line_num}:Base Register absent")
    try:
        immediate = int(operands[1][0:x])
    except:
        raise ValueError(f"Error in line no. {line_num}:Immediate field requires 12 bit integer input")
    if not(-2048<=int(immediate)<=2047):
        raise ValueError(f"Error in line no. {line_num}:Immediate out of bounds")
    rs1 = operands[1][x+1:y]
    rs2 = operands[0]
    if rs1 not in ABI_register_dict and rs1 not in register_name_dict:
        raise ValueError(f"Error in line no. {line_num}:Register not found")
    if rs2 not in ABI_register_dict and rs2 not in register_name_dict:
        raise ValueError(f"Error in line no. {line_num}:Register not found")
def pass2(address_list,label_address_dict):
    #Purpose of pass2: Check mnemonic names, check immediate range, replace labels with the offset values,check for virtual halt,
    copied_address_list = [] #Of the form [(address,line_num,instructions)], with labels removed from instructions, leaving on the instruciton syntax
    for address,line_num,ins in address_list:
        copied_instruction = ins.copy()
        copied_address_list.append((address,line_num,copied_instruction))
    virtual_halt_count = 0
    for address,line_num,instructions in copied_address_list:
        if instructions == ["beq","zero","zero","0"]:
            virtual_halt_count+=1
        if instructions[0] not in mnemonic_dict:
            raise ValueError(f"Error in {line_num}:{instructions[0]} not a recognised mnemonic")
        else: #If the mnemonic is recognised, next step is to check if the appropriate fields are present,based on the instruction type:
            mnemonic = instructions[0]
            mnemonic_type = mnemonic_dict[mnemonic]["type"]
            #Check:1:Number of operands
            if len(instructions[1:]) != type_operands_dict[mnemonic_type]["operand_count"]:
                raise ValueError(f"Error in {line_num}:Incorrect number of operands")
            #Check:2 Appropriateness of operands
            else:
                mnem_type = mnemonic_dict[mnemonic]["type"]
                if mnem_type == "R":
                    R_Type_operand_check(instructions,label_address_dict,copied_address_list,line_num,address)
                elif mnem_type == "I_jalr" or mnem_type == "I_arith/logic" or mnem_type == "I_load":
                    I_Type_operand_check(instructions,label_address_dict,copied_address_list,line_num,address)
                elif mnem_type == "S":
                    S_Type_operand_check(instructions,label_address_dict,copied_address_list,line_num,address)
                elif mnem_type == "U":
                    U_Type_operand_check(instructions,label_address_dict,copied_address_list,line_num,address)
                elif mnem_type == "J":
                    J_Type_operand_check(instructions,label_address_dict,copied_address_list,line_num,address)
                elif mnem_type == "B":
                    B_Type_operand_check(instructions,label_address_dict,copied_address_list,line_num,address)
    if virtual_halt_count<1:
        raise ValueError("Error:No Virtual Halt Found")
    return(copied_address_list)
    
def imm_2_comp(immediate,num_bits): #Take the immediates and convert them into num_bit 2's complement representation, and return strings to be used in encoding functions
    immediate = int(immediate)

    //If number is non-negative
    if immediate>=0:
        return format(immediate,f'0{num_bits}b')
    //If number is negative
    else:
        value = (2**num_bits) + immediate
        return format(value,f'0{num_bits}b')
        
def encode_R(instruction,mnemonic_dict): #Types have been distributed based on opcode. lw, jalr and addi,sltui have different opcodes hence, different classification
    mnemonic = instruction[0]
    rd = instruction[1]
    rs1 = instruction[2]
    rs2 = instruction[3]

    funct7 = mnemonic_dict[mnemonic]["funct7"]
    funct3 = mnemonic_dict[mnemonic]["funct3"]
    opcode = mnemonic_dict[mnemonic]["opcode"]
   #register binary values
    if rd in ABI_register_dict:
       rd_bin = ABI_register_dict[rd]
    else:
       rd_bin = register_name_dict[rd]
        
    if rs1 in ABI_register_dict:
       rs1_bin = ABI_register_dict[rs1]
    else:
        rs1_bin = register_name_dict[rs1]
        
    if rs2 in ABI_register_dict:
        rs2_bin = ABI_register_dict[rs2]
    else:
        rs2_bin = register_name_dict[rs2]
    #final machine instruction
    binary_form = funct7 + rs2_bin + rs1_bin + funct3 + rd_bin + opcode
    return binary_form


def encode_I_arith_logic(instruction,mnemonic_dict):
    mnemonic = instruction[0]
    rd = instruction[1]
    rs1 = instruction[2]
    imm = imm_2_comp(instruction[3],12)

    funct3 = mnemonic_dict[mnemonic]["funct3"]
    opcode = mnemonic_dict[mnemonic]["opcode"]
    #register binary values
    if rd in ABI_register_dict:
        rd_bin = ABI_register_dict[rd]
    else:
        rd_bin = register_name_dict[rd]
        
    if rs1 in ABI_register_dict:
        rs1_bin = ABI_register_dict[rs1]
    else:
        rs1_bin = register_name_dict[rs1]
    #final machine instruction
    binary_form = imm + rs1_bin + funct3 + rd_bin + opcode
    return binary_form
    
def encode_I_jalr(instruction,mnemonic_dict):
    {}
def encode_I_lw(instruction,mnemonic_dict):
    mnemonic = instruction[0]
    rd = instruction[1]
    operand = instruction[2] # imm(rs1)

    x = operand.index("(")
    y = operand.index(")")

    imm = imm_2_comp(operand[:x],12)
    rs1 = operand[x+1:y]

    funct3 = mnemonic_dict[mnemonic]["funct3"]
    opcode = mnemonic_dict[mnemonic]["opcode"]
    #register binary values
    if rd in ABI_register_dict:
        rd_bin = ABI_register_dict[rd]
    else:
        rd_bin = register_name_dict[rd]
    if rs1 in ABI_register_dict:
        rs1_bin = ABI_register_dict[rs1]
    else:
        rs1_bin = register_name_dict[rs1]
    #final machine instruction
    binary_form = imm + rs1_bin + funct3 + rd_bin + opcode
    return binary_form

def encode_J(instruction,mnemonic_dict):
    {}
def encode_S(instruction,mnemonic_dict):
    mnemonic = instruction[0]
    rs2 = instruction[1]
    operand = instruction[2] #imm(rs1)
    
    x = operand.index("(")
    y = operand.index(")")
    imm = imm_2_comp(operand[:x],12)
    rs1 = operand[x+1:y]
    
    funct3 = mnemonic_dict[mnemonic]["funct3"]
    opcode = mnemonic_dict[mnemonic]["opcode"]
    #register binary values
    if rs2 in ABI_register_dict:
        rs2_bin = ABI_register_dict[rs2]
    else:
        rs2_bin = register_name_dict[rs2]
    if rs1 in ABI_register_dict:
        rs1_bin = ABI_register_dict[rs1]
    else:
        rs1_bin = register_name_dict[rs1]
    #final machine instruction
    binary_form = imm[:7] + rs2_bin + rs1_bin + funct3 + imm[7:] + opcode
    return binary_form
    
def encode_U(instruction,mnemonic_dict):
    mnemonic = instruction[0]
    rd = instruction[1]
    imm = format(int(instruction[2]),'020b')
    
    opcode = mnemonic_dict[mnemonic]["opcode"]
    #register binary values
    if rd in ABI_register_dict:
        rd_bin = ABI_register_dict[rd]
    else:
        rd_bin = register_name_dict[rd]
    #final machine instruction
    binary_form = imm + rd_bin + opcode
    return binary_form
    
def encode_B(instruction,mnemonic_dict):
    {}
def encoder(final_address_list,mnemonic_dict): #return machine code to be written into output file
    {}
def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    instruction_list = lexer_output(input_file)
    address_list, label_address_dict = pass1(instruction_list)
    final_address_list = pass2(address_list,label_address_dict)
    machine_code = encoder(final_address_list,mnemonic_dict)
