import sys
import memory

riscv_regs = [0 for _ in range(32)]
instruction_pointer = 0
riscv_regs[2] = 380
def bin_stringify(raw_integer):
    
    if raw_integer < 0:
        adjusted = raw_integer + (1 << 32)
    else:
        adjusted = raw_integer
        
    stripped = str(bin(adjusted & 0xFFFFFFFF))[2:]
    return stripped.zfill(32)
def export_execution_state(output_stream):
    
    
    if riscv_regs[0] != 0:
        riscv_regs[0] = 0
    
    current_state_line = bin_stringify(instruction_pointer)
    
    iterator_index = 0
    while iterator_index < 32:
        current_state_line = current_state_line + " " + bin_stringify(riscv_regs[iterator_index])
        iterator_index += 1
        
    output_stream.write(current_state_line + "\n")
def dump_heap_memory(output_stream):
    
    scan_address = 65536
    
    while scan_address <= 65660:
        fetched_val = memory.fetch_word_from_bus(scan_address)
        binary_representation = bin_stringify(fetched_val)
        
        hex_string = hex(scan_address)[2:]
        padded_hex = hex_string.rjust(8, '0')
        
        output_stream.write("0x" + padded_hex + ":" + binary_representation + "\n")
        scan_address = scan_address + 4
def engine_start(output_stream):
    global instruction_pointer
    
    
    halting_instruction_hex = 99 
    
    cycle_timeout = 100
    current_cycle = 0
    while current_cycle < cycle_timeout:
        try:
            fetched_instruction = memory.fetch_word_from_bus(instruction_pointer)
        except memory.MemorySimulationError as mem_err:
            print(f"FATAL: Bus Error on fetch. {mem_err}")
            break
        
        
        
        
        if fetched_instruction == halting_instruction_hex:
            export_execution_state(output_stream)
            dump_heap_memory(output_stream)
            break
            
        export_execution_state(output_stream)
        
        instruction_pointer += 4
        current_cycle += 1
        
    if current_cycle >= cycle_timeout:
        print("SIMULATOR KILLED: Cycle timeout reached. Your decode logic probably isn't incrementing the IP.")
if __name__ == "__main__":
    if len(sys.argv) > 1:
        trace_file = open(sys.argv[1], 'w')
        try:
            engine_start(trace_file)
        finally:
            trace_file.close()
    else:
        print("Usage error: You must provide a trace file path.")