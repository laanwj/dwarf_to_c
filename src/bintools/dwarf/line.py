"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from copy import copy
from bintools.dwarf.enums import DW_LNS, DW_LNE
from bintools.dwarf.stream import SectionCache


class MachineRegisters(object):
    default_is_stmt = False
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.address = 0
        self.file = 1
        self.line = 1
        self.column = 0
        self.is_stmt = MachineRegisters.default_is_stmt
        self.basic_block = False
        self.end_sequence = False


def statement_information(dwarf, prog):
    MachineRegisters.default_is_stmt = prog.default_is_stmt
    regs = MachineRegisters()
    matrix = []
    
    while dwarf.io.tell() < prog.stop:
        opcode = dwarf.u08()
        
        # Special Opcodes
        if opcode >= prog.opcode_base:
            adj_opcode = opcode - prog.opcode_base
            address_advance = adj_opcode/prog.line_range
            line_advance = prog.line_base + (adj_opcode % prog.line_range)
            
            regs.line += line_advance
            regs.address += (prog.min_instr_length * address_advance)
            matrix.append(copy(regs))
            regs.basic_block = False
        
        # Extended Opcodes
        elif opcode == 0:
            dwarf.ULEB128() # length
            extended_op = dwarf.u08()
            if extended_op == DW_LNE.end_sequence:
                regs.end_sequence = True
                matrix.append(copy(regs))
                regs.reset()
            
            elif extended_op == DW_LNE.set_address:
                regs.address = dwarf.read_addr()
            
            elif extended_op == DW_LNE.define_file:
                prog.file_names.append(FileEntry(dwarf))
            
            elif extended_op == DW_LNE.set_discriminator:
                dwarf.ULEB128() # TODO?
            
            else:
                assert False, 'Extended Opcode not implemented: %d' % extended_op
            
        # Standard Opcodes
        elif opcode == DW_LNS.copy:
            matrix.append(copy(regs))
            regs.basic_block = False
        
        elif opcode == DW_LNS.advance_pc:
            address_advance = dwarf.ULEB128()
            regs.address += (prog.min_instr_length * address_advance)
        
        elif opcode == DW_LNS.advance_line:
            regs.line += dwarf.SLEB128()
        
        elif opcode == DW_LNS.set_file:
            regs.file = dwarf.ULEB128()
        
        elif opcode == DW_LNS.set_column:
            regs.column = dwarf.ULEB128()
        
        elif opcode == DW_LNS.negate_stmt:
            regs.is_stmt = not regs.is_stmt
        
        elif opcode == DW_LNS.set_basic_block:
            regs.basic_block = True
        
        elif opcode == DW_LNS.const_add_pc:
            regs.address += prog.min_instr_length * (
                        (255 - prog.opcode_base) / prog.line_range)
        
        else:
            assert False, 'Opcode not implemented: %d' % opcode
    
    return matrix


class FileEntry(object):
    def __init__(self, dwarf):
        self.name = dwarf.read_string()
        if self.name == '':
            return
        
        self.directory_index = dwarf.ULEB128()
        self.time_last_mod = dwarf.ULEB128()
        self.length = dwarf.ULEB128()


class ProgramPrologue(object):
    def __init__(self, dwarf):
        total_length = dwarf.u32()
        self.stop = dwarf.io.tell() + total_length
        ver = dwarf.check_version(handled=[2, 3])
        dwarf.u32() # prologue_length
        
        self.min_instr_length = dwarf.u08()
        self.default_is_stmt = dwarf.u08() != 0
        self.line_base = dwarf.s08()
        self.line_range = dwarf.u08()
        self.opcode_base = dwarf.u08()
        
        self.standard_opcode_lengths = []
        for _ in range(self.opcode_base-1):
            self.standard_opcode_lengths.append(dwarf.u08())
        
        # Directories
        self.include_directories = []
        while True:
            string = dwarf.read_string()
            if string == '': break
            self.include_directories.append(string)
        
        # Files
        self.file_names = []
        while True:
            f = FileEntry(dwarf)
            if f.name == '': break
            self.file_names.append(f)


class StatementProgram(object):
    def __init__(self, dwarf, cu):
        self.cu = cu
        self.prog = ProgramPrologue(dwarf)
        self.matrix = statement_information(dwarf, self.prog)
    
    def get_file_path(self, i):
        f = self.prog.file_names[i-1]
        dir = None
        if f.directory_index != 0:
            dir = self.prog.include_directories[f.directory_index - 1]
        return dir, f.name
    
    def get_file_index(self, name):
        for i, f in enumerate(self.prog.file_names):
            if name.endswith(f.name):
                return i + 1
        raise KeyError('The given filename "%s" is not in the file list.' % (name))
    
    def regs_to_str(self, regs):
        flags = [name for name in ['is_stmt', 'basic_block', 'end_sequence']
                          if getattr(regs, name)]
        return '%s [%3d,%d] 0x%08x - %s' % (
            self.cu.get_file_path(regs.file), regs.line, regs.column,
            regs.address, ', '.join(flags))
    
    def get_regs_by_addr(self, addr):
        prev_regs = None
        for regs in self.matrix:
            if addr == regs.address:
                return regs
            elif prev_regs is not None and addr < regs.address:
                # Assuming it was ordered by addr
                return prev_regs
            prev_regs = regs
        
        raise KeyError("The given address 0x%x is not contained in this compilation unit %d" % (addr, self.cu.overall_offset))
    
    def get_addr_by_loc(self, f_index, line):
        prev_regs = None
        for regs in self.matrix:
            if regs.file == f_index:
                if line == regs.line:
                    return regs.address
                elif prev_regs is not None and line < regs.line:
                    # Assuming it was ordered by line
                    return prev_regs.address
            prev_regs = regs
        
        raise KeyError("The given location is not contained in this compilation unit %d" % (self.cu.overall_offset))
    
    def get_loc_by_addr(self, addr):
        regs = self.get_regs_by_addr(addr)
        return (self.cu.get_file_path(regs.file), regs.line, regs.column)
    
    def __str__(self):
        s = ['\n.debug_line: line number info for a single cu']
        s+= list(map(self.regs_to_str, self.matrix))
        return '\n'.join(s)


class StatementProgramLoader(SectionCache):
    def __init__(self, dwarf):
        SectionCache.__init__(self, dwarf, '.debug_line', StatementProgram, 'stmt_list')
