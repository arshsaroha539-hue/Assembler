import sys

def main():
    # 1. Check for Command Line Arguments (Required by Auto-Grader)
    if len(sys.argv) < 3:
        return

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # 2. Open the Assembly File
    try:
        with open(input_path, 'r') as file:
            raw_lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_path}")
        return

    cleaned_instructions = []
    instruction_count = 0

    # 3. Processing each line (The Lexer's Job)
    for idx, raw_text in enumerate(raw_lines, start=1):
        # A. Remove Comments (anything after #)
        line = raw_text.split('#')[0]
        
        # B. Remove Commas (normalize instruction format)
        line = line.replace(',', ' ')
        
        # C. Tokenize (Remove extra spaces and tabs)
        tokens = line.strip().split()
        
        # D. Skip Empty Lines
        if not tokens:
            continue

        # E. Check Label Syntax
        if tokens[0].endswith(':'):
            label_name = tokens[0][:-1]
            # Rule: Label must start with a letter or underscore
            if not (label_name[0].isalpha() or label_name[0] == '_'):
                print(f"Error at line {idx}: Invalid label name '{label_name}'")
                sys.exit()
            
            # If line is JUST a label, save it and continue
            if len(tokens) == 1:
                cleaned_instructions.append({'line': idx, 'tokens': tokens})
                continue

        # F. Program Memory Bound Check
        # Max memory = 256 bytes. Each instruction = 4 bytes. 256/4 = 64 lines.
        instruction_count += 1
        if instruction_count > 64:
            print(f"Error: Program memory overflow at line {idx} (Exceeded 64 instructions)")
            sys.exit()

        cleaned_instructions.append({'line': idx, 'tokens': tokens})

    # 4. Virtual Halt Check (Required by CO_Project_2026.pdf)
    # The last instruction must be 'beq zero,zero,0'
    if not cleaned_instructions:
        print("Error: Empty assembly file.")
        sys.exit()
        
    last_tokens = cleaned_instructions[-1]['tokens']
    # Check if 'beq zero zero 0' is the last item
    if 'beq' not in last_tokens or 'zero' not in last_tokens:
         print("Error: Missing Virtual Halt (beq zero,zero,0) at the end of the program.")
         # sys.exit() # Uncomment this if your professor strictly requires the halt

    # 5. Success Message
    print(f"Lexer: Processed {instruction_count} instructions successfully.")
    
    # NOTE FOR GROUP: 
    # 'cleaned_instructions' is now ready to be passed to the PARSER teammate.
    # It contains a list of dictionaries with line numbers and clean word tokens.

if __name__ == "__main__":
    main()