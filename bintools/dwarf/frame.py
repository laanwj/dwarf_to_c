"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.dwarf.stream import SectionLoader
from bintools.dwarf.enums import DW_CFA


class CallFrameInstruction(object):
    def __init__(self, opcode, operand_1=None, operand_2=None):
        self.opcode = opcode
        self.operand_1 = operand_1
        self.operand_2 = operand_2
    
    def __str__(self):
        s = [DW_CFA[self.opcode]]
        if self.operand_1 is not None:
            s.append(str(self.operand_1))
        if self.operand_2 is not None:
            s.append(str(self.operand_2))
        return ' '.join(s)


DW_CFA_OPERANDS = {
    DW_CFA.set_loc           : ('addr' , None),
    DW_CFA.advance_loc1      : ('data1', None),
    DW_CFA.advance_loc2      : ('data2', None),
    DW_CFA.advance_loc4      : ('data4', None),
    DW_CFA.offset_extended   : ('udata', 'udata'),
    DW_CFA.restore_extended  : ('udata', None),
    DW_CFA.undefined         : ('udata', None),
    DW_CFA.same_value        : ('udata', None),
    DW_CFA.register          : ('udata', 'udata'),
    DW_CFA.def_cfa           : ('udata', 'udata'),
    DW_CFA.def_cfa_register  : ('udata', None),
    DW_CFA.def_cfa_offset    : ('udata', None),
    DW_CFA.def_cfa_expression: ('block', None),
    DW_CFA.expression        : ('udata', 'block'),
    DW_CFA.offset_extended_sf: ('udata', 'sdata'),
    DW_CFA.def_cfa_sf        : ('udata', 'sdata'),
    DW_CFA.def_cfa_offset_sf : ('sdata', None),
    DW_CFA.val_offset        : ('udata', 'udata'),
    DW_CFA.val_offset_sf     : ('udata', 'sdata'),
    DW_CFA.val_expression    : ('udata', 'block'),
    DW_CFA.GNU_args_size     : ('udata', None),
    DW_CFA.GNU_negative_offset_extended : ('udata', 'udata'),
}


def parse_call_frame_instructions(dwarf, length):
    instructions = []
    
    stop = dwarf.io.tell() + length
    while dwarf.io.tell() < stop:
        opcode = dwarf.u08()
        if opcode == DW_CFA.nop:
            continue
        
        operand_1 = operand_2 = None
        
        primary_opcode = opcode & 0xc0
        if primary_opcode != 0:
            operand_1 = opcode & 0x3F
            opcode = primary_opcode
            if primary_opcode == DW_CFA.offset:
                operand_2 = dwarf.ULEB128()
        else:
            if opcode in DW_CFA_OPERANDS:
                type_1, type_2 = DW_CFA_OPERANDS[opcode]
                operand_1 = dwarf.read_type(type_1)
                if type_2 is not None:
                    operand_2 = dwarf.read_type(type_2)
            else:
                opname = DW_CFA[opcode] if opcode in DW_CFA else "unknown"
                print("unhandled opcode: %02x (%s)" % (opcode,opname))
        
        instructions.append(CallFrameInstruction(opcode, operand_1, operand_2))
    
    return instructions


class CallFrameInformation(object):
    def __init__(self, dwarf, offset, length):
        self.offset = offset
        start = dwarf.io.tell()
        ver = dwarf.check_version(handled=[1, 3], bytes=1)
        
        self.augmentation = dwarf.read_string()
        self.code_alignment_factor = dwarf.ULEB128()
        self.data_alignment_factor = dwarf.SLEB128()
        self.return_address_register = dwarf.u08()
        
        instr_length = length - (dwarf.io.tell() - start)
        self.initial_instructions =  parse_call_frame_instructions(dwarf, instr_length)
    
    def __str__(self):
        s = ['<%d> CFI:' % self.offset]
        if self.augmentation:
            s.append('augmentation      : "%s"' % self.augmentation)
        s.append('(code, data) align: (%d, %d)' % (self.code_alignment_factor, self.data_alignment_factor))
        s.append('return address    : r%d' % self.return_address_register)
        s.append('instructions      : %s' % ' '.join(map(str, self.initial_instructions)))
        return '\n   '.join(s)


class FrameTable(object):
    def __init__(self, fde):
        pass


class FrameDescriptionEntry(object):
    def __init__(self, dwarf, offset, length, cie):
        start = dwarf.io.tell()
        self.cie_p = cie
        self.initial_location = dwarf.read_ref_addr()
        self.address_range = dwarf.read_ref_addr()
        
        instr_length = length - (dwarf.io.tell() - start)
        self.instructions =  parse_call_frame_instructions(dwarf, instr_length)
    
    def __str__(self):
        s = ['FDE:']
        s.append('cie_p        : %d' % self.cie_p)
        s.append('address range: <0x%x:0x%x>' % (self.initial_location, self.initial_location+self.address_range))
        s.append('instructions : %s' % ' '.join(map(str, self.instructions)))
        return '\n   '.join(s)


def debugFrameEntry(dwarf, offset):
    length = dwarf.u32()
    cie =  dwarf.u32()
    # remaining length, without cie's bytes
    length -= 4
    if cie == dwarf.CIE_ID:
        return CallFrameInformation(dwarf, offset, length)
    else:
        return FrameDescriptionEntry(dwarf, offset, length, cie)


class FrameLoader(SectionLoader):
    def __init__(self, dwarf):
        SectionLoader.__init__(self, dwarf, '.debug_frame', debugFrameEntry)
    
    def get_frame_table(self, offset):
        return 
