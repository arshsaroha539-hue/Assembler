import string

class Instruction:
    def __init__(self,instructionType="",instructionParams = [],label=""):
        self.label = label
        self.instructionType = instructionType
        self.instructionParams = instructionParams
    def __eq__(self, value):
        return self.label == value.label and self.instructionType == value.instructionType and self.instructionParams == value.instructionParams

_DEFAULT_INSTRUCTION = Instruction()
_VALID_SET_FOR_LABEL = set(string.ascii_lowercase).union(set(string.ascii_uppercase)).union("_")

class Lexer:
    def __init__(self):
        self._instructions = []
        pass

    def appendInstruction(self,instruction):
        self._instructions.append(instruction)

    def parseInstructionTypeAndParams(self,instruction):
        parsedInstruction = instruction.strip().split(" ")
        print(parsedInstruction)
        if len(parsedInstruction) < 2:
           print("Error: Invalid Instruction in this line")
           return "",[]
        else:
            instructionType = parsedInstruction[0]
            instructionParamsStr = "".join(parsedInstruction[1:])
            instructionParams = list(map(lambda x: x.strip(), instructionParamsStr.strip().split(",")))
            return instructionType,instructionParams

    def parseInstructionWithLabel(self,instruction):
        inputWithLabel = instruction.strip().split(":")
        label = ""
        instructionWithoutLabel = ""
        if len(inputWithLabel) == 0:
            print("Warn: No instructions in this line")
            return Instruction()
        
        elif len(inputWithLabel) == 1:
            instructionWithoutLabel = inputWithLabel[0]
            print("Debug: No label in this line")
        else:
            figuredLabel = inputWithLabel[0].strip()
            if figuredLabel[0] in _VALID_SET_FOR_LABEL:
                label = figuredLabel
            instructionWithoutLabel = inputWithLabel[1]
        instructionType,instructionParams = self.parseInstructionTypeAndParams(instructionWithoutLabel)
        return Instruction(instructionType,instructionParams,label)
    
    def parseInputLine(self,line):
        commentsWithInput = line.strip().split("#")
        if len(commentsWithInput) == 0:
            print("Warn: No instructions in this line")
        parsedInstruction = self.parseInstructionWithLabel(commentsWithInput[0])
        if parsedInstruction != _DEFAULT_INSTRUCTION:
            self.appendInstruction(parsedInstruction)
    
    def getInstructions(self):
        return self._instructions
    

if __name__ == "__main__":
    inputs = ["add s1, s2, s3",
              "addi x5, x6, 10",
              "lw a5, 20(s1)",
              "sw ra, 32(sp)",
              "loop: beq a0, a1, end",
              "lui t0, 0x12",
              "jal ra, targe",
              "",
              " #only comment"]
    outputs = [
        Instruction("add", ["s1", "s2", "s3"],""),
        Instruction("addi", ["x5", "x6", "10"],""),
        Instruction("lw", ["a5", "20(s1)"],""),
        Instruction("sw", ["ra", "32(sp)"],""),
        Instruction("beq", ["a0", "a1", "end"],"loop"),
        Instruction("lui", ["t0", "0x12"],""),
        Instruction("jal", ["ra", "targe"],""),
        Instruction(),
        Instruction()
    ]
    for index,input in enumerate(inputs):
        lexer = Lexer()
        lexer.parseInputLine(input)
        if outputs[index] == _DEFAULT_INSTRUCTION:
            assert len(lexer.getInstructions()) == 0
        else:
            result = lexer.getInstructions()[0]
            assert result == outputs[index]
    print("All test cases worked fine.")