import sys
program_memory = {x:0 for x in range(0x0,0xFF+1,4)}
stack_memory = {x:0 for x in range(0x100,0x17F + 1,4)}
data_memory = {x:0 for x in range(0x10000,0x1007F+1,4)}
register_file = {x: 0 for x in range(0,32)}
register_file[2] = 0x0000017C
opcode_control_dict= {
    "0110011": ("1", "_", "0", "0", "00", "0", "10", "0"),
    "0010011": ("1", "000", "1", "0", "00", "0", "10", "0"),
    "0000011": ("1", "000", "1", "0", "01", "0", "00", "0"),
    "0100011": ("0", "001", "1", "1", "_", "0", "00", "0"),
    "1100011": ("0", "011", "0", "0", "_", "1", "_", "0"),
    "1101111": ("1", "010", "_", "0", "10", "0", "_", "1"),
    "1100111": ("1", "000", "1", "0", "10", "0", "00", "1"),
    "0110111": ("1", "100", "_", "0", "11", "0", "_", "0"),
    "0010111": ("1", "100", "1", "0", "00", "0", "00", "0"),
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
    def PCSRC_gen(self, instruction):
        # Default: no branch/jump
        take_branch = False

        if self.BRANCH:
            if instruction.funct3 == "000":      # BEQ
                take_branch = self.zero
            elif instruction.funct3 == "001":    # BNE
                take_branch = not self.zero
            elif instruction.funct3 == "100":    # BLT
                take_branch = not self.gte
            elif instruction.funct3 == "101":    # BGE
                take_branch = self.gte
            elif instruction.funct3 == "110":    # BLTU
                take_branch = not self.gteu
            elif instruction.funct3 == "111":    # BGEU
                take_branch = self.gteu
        self.PCSRC = self.JUMP or take_branch
class Instruction:
    def __init__(self,binary_instruction,address):
        self.address = address
        self.opcode = binary_instruction[25:]
        self.funct3 = binary_instruction[17:20]
        self.funct7 = binary_instruction[0:7]
        self.rs1 = binary_instruction[12:17]
        self.rs2 = binary_instruction[7:12]
        self.rd = binary_instruction[20:25]
        self.imm_ex = binary_instruction[0:25]
        self._full_binary = binary_instruction
        self.control_signals = control_signal(self,address)
        self.ALURESULT = None
        self.PCplustarget = None
        self.PCplusfour = None
        self.read_data = None
    def immediate_extend(self):
        b = self.imm_ex
        immsrc = self.control_signals.IMMSRC
        def sign_extend(num):
            value = int(num,2)
            if num[0]=="1":
                value -= 2**len(num)
            return value
        #I-type
        if immsrc=="000": 
            imm = b[0:12]
            return sign_extend(imm)
        #S-type
        elif immsrc=="001": 
            imm = b[0:7] + b[20:25]
            return sign_extend(imm)
        #B-type
        elif immsrc=="011":
            imm = b[0] + self._full_binary[24] + b[1:7] + b[20:24] + "0"
            return sign_extend(imm)
        #J-type
        elif immsrc=="010":
            imm = b[0] + b[12:20] + b[11] + b[1:11] + "0"
            return sign_extend(imm)
        #U-type
        elif immsrc=="100":
            return int(b[0:20],2)*(2**12)
        return 0;
    def ALU_decoder(self):
        op5 = self.opcode[1]
        f75 = self.funct7[1]
        if self.control_signals.ALUOP == "00":
            return "ADD"
        if self.control_signals.ALUOP == "01":
            return "SUB"
        if self.control_signals.ALUOP == "10":
            if self.funct3 == "000":
                if op5 == "1" and f75 == "1":
                    return "SUB"
                else:
                    return "ADD"
            if self.funct3 == "001":
                return "SLL"
            if self.funct3 == "010":
                return "SLT"
            if self.funct3 == "011":
                return "SLTU"
            if self.funct3 == "100":
                return "XOR"
            if self.funct3 == "101":
                return "SRL"
            if self.funct3 == "110":
                return "OR"
            if self.funct3 == "111":
                return "AND"
        if self.control_signals.ALUOP == "11":
            return "ADD"
        if self.control_signals.ALUOP == "_":
            return "ADD"
    def ADD(self,a,b):
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
    def ALU(self):
        rs1_idx = int(self.rs1, 2)
        A = register_file[rs1_idx]
        if self.control_signals.ALUSRC == "1":
            B = self.immediate_extend()
        else:
            rs2_idx = int(self.rs2, 2)
            B = register_file[rs2_idx]
        if self.opcode == "0110111":
            self.ALURESULT = B % (2**32)
            self.control_signals.zero = False
            self.control_signals.gte = True
            self.control_signals.gteu = True
            return
        if self.opcode == "0010111":
            self.ALURESULT = (self.address + B) % (2**32)
            self.control_signals.zero = False
            self.control_signals.gte = True
            self.control_signals.gteu = True
            return
        operation = self.ALU_decoder()
        result = self.operations[operation](self,A, B)
        self.ALURESULT = result % (2**32)
        if A >= 2**31:
            A_signed = A - 2**32
        else:
            A_signed = A
        if B >= 2**31:
            B_signed = B - 2**32
        else:
            B_signed = B
        if A_signed == B_signed:
            self.control_signals.zero = True
        else:
            self.control_signals.zero = False
        if A_signed >= B_signed:
            self.control_signals.gte = True
        else:
            self.control_signals.gte = False
        if A >= B:
            self.control_signals.gteu = True
        else:
            self.control_signals.gteu = False
    def Memory_read_write(self):
        class MemorySimulationError(Exception):
            pass
        target_address = self.ALURESULT
        if self.control_signals.MEMWRITE == "1":
            if target_address % 4 != 0:
                raise MemorySimulationError(f"Misaligned memory write attempted at address {target_address}")
            
            rs2_idx = int(self.rs2, 2)
            clamped_value = register_file[rs2_idx] & 0xFFFFFFFF 
            
            if 256 <= target_address <= 383:
                stack_memory[target_address] = clamped_value
            elif 65536 <= target_address <= 65663:
                data_memory[target_address] = clamped_value
            elif 0 <= target_address <= 255:
                raise MemorySimulationError("Access Violation: Read-only ROM.")
            else:
                raise MemorySimulationError(f"Segmentation Fault: Write address {target_address} cannot be routed.")
                
        elif self.control_signals.RESULTSRC == "01": 
            if target_address % 4 != 0:
                raise MemorySimulationError(f"Misaligned memory read attempted at address {target_address}")
                
            if 0 <= target_address <= 255:
                self.read_data = program_memory.get(target_address, 0)
            elif 256 <= target_address <= 383:
                self.read_data = stack_memory.get(target_address, 0)
            elif 65536 <= target_address <= 65663:
                self.read_data = data_memory.get(target_address, 0)
            else:
                raise MemorySimulationError(f"Segmentation Fault: Read address {target_address} outside bounds.")
            
            
        
    def register_write_back(self):
        if self.control_signals.REGWRITE!="1":
            return
        idx = int(self.rd,2)
        if idx==0:
            return
        src = self.control_signals.RESULTSRC
        if src=="00": #ALU result
            value = self.ALURESULT
        elif src=="01": #Load
            value = self.read_data
        elif src=="10": #JAL/JALR
            value = self.PCplusfour
        elif src=="11": #LUI
            value = self.immediate_extend()
        else:
            return
        register_file[idx] = value % (2**32)
        
def fetch(binary_string,instruction_num):
    inst = Instruction(binary_string,instruction_num*(4))
    return(inst)


instruction_pointer = 0

def bin_stringify(raw_integer):
    if raw_integer < 0:
        adjusted = raw_integer + (1 << 32)
    else:
        adjusted = raw_integer
    stripped = str(bin(adjusted & 0xFFFFFFFF))[2:]
    return("0b" + stripped.zfill(32))
def export_execution_state(output_stream):
    if register_file[0] != 0: register_file[0] = 0
    current_state_line = bin_stringify(instruction_pointer)
    iterator_index = 0
    while iterator_index < 32:
        current_state_line = current_state_line + " " + bin_stringify(register_file[iterator_index])
        iterator_index += 1
    output_stream.write(current_state_line.rstrip() + "\n")

def dump_heap_memory(output_stream):
    scan_address = 65536
    while scan_address <= 65660:
        fetched_val = data_memory.get(scan_address, 0)
        binary_representation = bin_stringify(fetched_val)
        hex_string = hex(scan_address)[2:].upper()
        padded_hex = hex_string.rjust(8, '0')
        output_stream.write("0x" + padded_hex + ":" + binary_representation + "\n")
        scan_address = scan_address + 4

def engine_start(input_file, trace_file_path):
    global instruction_pointer
    instruction_pointer = 0
    register_file[2] = 380

    
    addr = 0
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            program_memory[addr] = int(line, 2)
            addr += 4

    halting_instruction_hex = 99 
    cycle_timeout = 1000
    current_cycle = 0

    with open(trace_file_path, 'w') as output_stream:
        while current_cycle < cycle_timeout:
            fetched_instruction = program_memory.get(instruction_pointer, 0)
            
            if fetched_instruction == halting_instruction_hex:
                export_execution_state(output_stream)
                dump_heap_memory(output_stream)
                break
                
            fetch_bin = bin_stringify(fetched_instruction)[2:]
            inst = Instruction(fetch_bin, instruction_pointer)
            
            inst.PCplusfour = instruction_pointer + 4
            inst.PCplustarget = instruction_pointer + inst.immediate_extend()
            
            inst.ALU()
            inst.control_signals.PCSRC_gen(inst)
            inst.Memory_read_write()
            inst.register_write_back()
            
            if inst.control_signals.PCSRC:
                if inst.opcode == "1100111":
                    instruction_pointer = inst.ALURESULT & ~1
                else:
                    instruction_pointer = inst.PCplustarget
            else:
                instruction_pointer = inst.PCplusfour
            export_execution_state(output_stream)
            current_cycle += 1

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        engine_start(sys.argv[1], sys.argv[2])
    else:
        print("Usage error: You must provide input.txt and trace.txt file path.")
