"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.elf.exception import *
from bintools.dwarf.enums import DW_OP


class Instruction(object):
    def __init__(self, addr, opcode, operand_1=None, operand_2=None):
        self.addr = addr
        self.opcode = opcode
        self.operand_1 = operand_1
        self.operand_2 = operand_2
    
    def get(self):
        return (self.addr, self.opcode, self.operand_1, self.operand_2)
    
    def __str__(self):
        s = 'DW_OP_' + DW_OP[self.opcode]
        if self.operand_1 is not None:
          s += '('
          if DW_OP[self.opcode] == 'addr':
              s += str(hex(self.operand_1))
          else:
              s += str(self.operand_1)
          if self.operand_2 is not None:
            s += ','
            s += str(self.operand_2)
          s += ')'
        return s #''.join(s)


DW_OP_OPERANDS = {
    # Literal Encodings
    DW_OP.addr   : ('addr' , None),
    DW_OP.const1u: ('data1', None),
    DW_OP.const1s: ('sdata1', None),
    DW_OP.const2u: ('data2', None),
    DW_OP.const2s: ('sdata2', None),
    DW_OP.const4u: ('data4', None),
    DW_OP.const4s: ('sdata4', None),
    DW_OP.const8u: ('data8', None),
    DW_OP.const8s: ('sdata8', None),
    DW_OP.constu : ('read_udata', None),
    DW_OP.consts : ('read_sdata', None),
    
    # Register Based Addressing
    DW_OP.fbreg : ('sdata', None),
    DW_OP.breg0 : ('sdata', None), DW_OP.breg1 : ('sdata', None),
    DW_OP.breg2 : ('sdata', None), DW_OP.breg3 : ('sdata', None),
    DW_OP.breg4 : ('sdata', None), DW_OP.breg5 : ('sdata', None),
    DW_OP.breg6 : ('sdata', None), DW_OP.breg7 : ('sdata', None),
    DW_OP.breg8 : ('sdata', None), DW_OP.breg9 : ('sdata', None),
    DW_OP.breg10: ('sdata', None), DW_OP.breg11: ('sdata', None),
    DW_OP.breg12: ('sdata', None), DW_OP.breg13: ('sdata', None),
    DW_OP.breg14: ('sdata', None), DW_OP.breg15: ('sdata', None),
    DW_OP.breg16: ('sdata', None), DW_OP.breg17: ('sdata', None),
    DW_OP.breg18: ('sdata', None), DW_OP.breg19: ('sdata', None),
    DW_OP.breg20: ('sdata', None), DW_OP.breg21: ('sdata', None),
    DW_OP.breg22: ('sdata', None), DW_OP.breg23: ('sdata', None),
    DW_OP.breg24: ('sdata', None), DW_OP.breg25: ('sdata', None),
    DW_OP.breg26: ('sdata', None), DW_OP.breg27: ('sdata', None),
    DW_OP.breg28: ('sdata', None), DW_OP.breg29: ('sdata', None),
    DW_OP.breg30: ('sdata', None), DW_OP.breg31: ('sdata', None),
    DW_OP.bregx : ('sdata', 'sdata'),
    
    # Stack Operations
    DW_OP.pick       : ('data1', None),
    DW_OP.deref_size : ('data1', None),
    DW_OP.xderef_size: ('data1', None),
    
    # Arithmetic and Logical Operations
    DW_OP.plus_uconst: ('udata', None),
    
    # Control Flow Operations
    DW_OP.skip: ('sdata2', None),
    DW_OP.bra : ('sdata2', None),
    
    # Special Operations
    DW_OP.piece: ('udata', None),

    # DWARF3/4
    DW_OP.call2: ('data2', None),
    DW_OP.call4: ('data4', None),
    DW_OP.call_ref: ('data4', None),
    DW_OP.bit_piece: ('udata', 'udata'),
    DW_OP.implicit_value: ('block', None),
}


class Expression(object):
    def __init__(self, dwarf, length):
        self.instructions = []
        self.addr_index_dict = {}
        
        start = dwarf.io.tell()
        i = 0
        while True:
            addr = dwarf.io.tell() - start
            if addr >= length:
                break
            
            opcode = dwarf.u08()
            if opcode not in DW_OP:
                raise ParseError("Unknown DW_OP code: %d" % opcode)
            
            operand_1 = operand_2 = None
            if opcode in DW_OP_OPERANDS:
                type_1, type_2 = DW_OP_OPERANDS[opcode]
                operand_1 = dwarf.read_type(type_1)
                if type_2 is not None:
                    operand_2 = dwarf.read_type(type_2)
            
            self.instructions.append(Instruction(addr, opcode, operand_1, operand_2))
            self.addr_index_dict[addr] = i
            i += 1
    
    @staticmethod
    def get_values(addr_stack, n=2):
        values = []
        for _ in range(n):
            values.append(addr_stack.pop())
        return values
    
    def evaluate(self, base_address=0, machine=None):
        addr_stack = [base_address]
        
        i = 0
        while True:
            if i >= len(self.instructions): break
            
            op_addr, opcode, operand_1, operand_2 = self.instructions[i].get()
            
            # Literal Encodings
            if opcode >= DW_OP.lit0 and opcode >= DW_OP.lit31:
                addr_stack.append(opcode - DW_OP.lit0)
            
            if opcode in [DW_OP.addr, DW_OP.constu, DW_OP.consts,
                          DW_OP.const1u, DW_OP.const1s, DW_OP.const2u, DW_OP.const2s,
                          DW_OP.const4u, DW_OP.const4s, DW_OP.const8u, DW_OP.const8s]:
                addr_stack.append(operand_1)
            
            # Register Based Addressing
            elif opcode == DW_OP.fbreg:
                addr_stack.append(self.machine.read_fbreg() + operand_1)
            
            elif opcode >= DW_OP.breg0 and opcode <= DW_OP.breg31:
                reg_index = opcode - DW_OP.breg0
                addr_stack.append(self.machine.read_reg(reg_index) + operand_1)
            
            elif opcode == DW_OP.bregx:
                addr_stack.append(self.machine.read_reg(operand_1) + operand_2)
            
            # Stack Operations
            elif opcode == DW_OP.dup:
                addr_stack.append(addr_stack[-1])
            
            elif opcode == DW_OP.drop:
                addr_stack.pop()
            
            elif opcode == DW_OP.pick:
                index = len(addr_stack) - operand_1 - 1
                addr_stack.append(addr_stack[index])
            
            elif opcode == DW_OP.over:
                addr_stack.append(addr_stack[-2])
            
            elif opcode == DW_OP.swap:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack += [former_top, former_second]
            
            elif opcode == DW_OP.rot:
                top, second, third = Expression.__get_values(addr_stack, 3)
                addr_stack += [top, third, second]
            
            elif opcode == DW_OP.deref:
                addr = addr_stack.pop()
                addr_stack.append(self.machine.read_addr(addr))
            
            elif opcode == DW_OP.deref_size:
                addr = addr_stack.pop()
                addr_stack.append(self.machine.read_addr(addr))
            
            elif opcode == DW_OP.xderef:
                addr = addr_stack.pop()
                addr_space_id = addr_stack.pop()
                addr_stack.append(self.machine.read_addr(addr, addr_space_id))
            
            elif opcode == DW_OP.xderef_size:
                addr = addr_stack.pop()
                addr_space_id = addr_stack.pop()
                addr_stack.append(self.machine.read_addr(addr, addr_space_id))
            
            # Arithmetic and Logical Operations
            elif opcode == DW_OP.abs:
                top = addr_stack.pop()
                addr_stack.append(abs(top))
            
            elif opcode == DW_OP.and_:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_top & former_second)
            
            elif opcode == DW_OP.div:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_second // former_top)
            
            elif opcode == DW_OP.minus:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_second - former_top)
            
            elif opcode == DW_OP.mod:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_second % former_top)
            
            elif opcode == DW_OP.mul:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_second * former_top)
            
            elif opcode == DW_OP.neg:
                top = addr_stack.pop()
                addr_stack.append(-top)
            
            elif opcode == DW_OP.not_:
                top = addr_stack.pop()
                addr_stack.append(~top)
            
            elif opcode == DW_OP.plus:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_second + former_top)
            
            elif opcode == DW_OP.plus_uconst:
                top = addr_stack.pop()
                addr_stack.append(top + operand_1)
            
            elif opcode == DW_OP.shl:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_second << former_top)
            
            elif opcode == DW_OP.shr:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_second >> former_top)
            
            elif opcode == DW_OP.shra:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_second >> former_top)
            
            elif opcode == DW_OP.xor:
                former_top, former_second = Expression.__get_values(addr_stack)
                addr_stack.append(former_second ^ former_top)
            
            # Control Flow Operations
            elif opcode >= DW_OP.eq and opcode <= DW_OP.ne:
                former_top, former_second = Expression.__get_values(addr_stack)
                if opcode == DW_OP.eq:
                    control = former_top == former_second
                elif opcode == DW_OP.ge:
                    control = former_top >= former_second
                elif opcode == DW_OP.gt:
                    control = former_top > former_second
                elif opcode == DW_OP.le:
                    control = former_top <= former_second
                elif opcode == DW_OP.lt:
                    control = former_top < former_second
                elif opcode == DW_OP.ne:
                    control = former_top != former_second
                addr_stack.append(1 if control else 0)
            
            elif opcode == DW_OP.skip:
                i = self.addr_index_dict[op_addr + operand_1]
                continue
            
            elif opcode == DW_OP.bra:
                top = addr_stack.pop()
                if top != 0:
                    i = self.addr_index_dict[op_addr + operand_1]
                    continue
            
            # Special Operations
            elif opcode == DW_OP.piece:
                self.size = operand_1
            
            i += 1
        
        return addr_stack.pop() 
    
    def __str__(self):
        return ' '.join(map(str, self.instructions))


if __name__ == '__main__':
    from dwarf.stream import DwarfList
    location_data = [0x23, 0x08]
    test_stream = DwarfList(location_data)
    
    e = Expression(test_stream, len(location_data))
    loc = e.evaluate()
    
    assert loc == 8, 'Error evaluating: %s' % location_data
    
    print('OK')
