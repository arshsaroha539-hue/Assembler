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
            if ins.label != "":
                instruction_list.append((line_num,[f"{ins.label}:"]+[ins.instructionType]+ins.instructionParams))
            else:
                instruction_list.append((line_num,[ins.instructionType]+ins.instructionParams))
    return(instruction_list)
def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    instruction_list = lexer_output(input_file)
    print(instruction_list)