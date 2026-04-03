class MemorySimulationError(Exception):
    pass

instruction_rom = {}  
execution_stack = {}    
heap_data = {}     

for mem_offset in range(65536, 65664, 4):
    heap_data[mem_offset] = 0
def fetch_word_from_bus(target_address):
    if target_address % 4 != 0:
        raise MemorySimulationError(f"Misaligned memory read attempted at address {target_address}")
    if 0 <= target_address <= 255:
        return instruction_rom.get(target_address, 0)
    
    if 256 <= target_address <= 383:
        return execution_stack.get(target_address, 0)
        
    if 65536 <= target_address <= 65663:
        return heap_data.get(target_address, 0)
        
    raise MemorySimulationError(f"Segmentation Fault: Read address {target_address} is outside mapped simulated regions.")
def write_word_to_bus(target_address, data_value):
    if target_address % 4 != 0:
        raise MemorySimulationError(f"Misaligned memory write attempted at address {target_address}")
    
    clamped_value = data_value & 0xFFFFFFFF 
    
    if 256 <= target_address <= 383:
        execution_stack[target_address] = clamped_value
        return
        
    if 65536 <= target_address <= 65663:
        heap_data[target_address] = clamped_value
        return
        
    if 0 <= target_address <= 255:
        raise MemorySimulationError("Access Violation: Attempted to write to the read-only Instruction Memory (ROM).")
    
    raise MemorySimulationError(f"Segmentation Fault: Write address {target_address} cannot be routed.")