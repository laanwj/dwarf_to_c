"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from io import StringIO
from bintools.elf.stream import ElfStream
from bintools.elf.enums import ELFCLASS, ELFDATA
from bintools.elf.exception import *

from bintools.dwarf.enums import DW_FORM
from bintools.dwarf.expressions import Expression


class DwarfStream(object):
    def __init__(self, addr_size=4):
        self.addr_size = addr_size
        if addr_size == 1:
            self.read_addr = self.u08
            self.max_addr = 0xFF
        elif addr_size == 2:
            self.read_addr = self.u16
            self.max_addr = 0xFFFF
        elif addr_size == 4:
            self.read_addr = self.u32
            self.max_addr = 0xFFFFFFFF
        
        elif addr_size == 8:
            self.read_addr = self.u64
            self.max_addr = 0xFFFFFFFFFFFFFFFF
        if self.bits == ELFCLASS.ELFCLASS32:
            self.CIE_ID = 0xFFFFFFFF
        elif self.bits == ELFCLASS.ELFCLASS64:
            self.CIE_ID = 0xFFFFFFFFFFFFFFFF
        
        # Read methods aliases
        self.read_data1 = self.read_ref1 = self.u08
        self.read_data2 = self.read_ref2 = self.u16
        self.read_data4 = self.read_ref4 = self.u32
        self.read_data8 = self.read_ref8 = self.u64
        self.read_ref_addr = self.read_addr
        self.read_sdata1 = self.s08
        self.read_sdata2 = self.s16
        self.read_sdata4 = self.s32
        self.read_sdata8 = self.s64
    
    def check_version(self, handled=[2], bytes=2):
        if bytes == 1:
            ver = self.u08()
        elif bytes == 2:
            ver = self.u16()
        
        if ver not in handled:
            raise ParseError("Unhandled version: %d" % ver)
        
        return ver
    
    def ULEB128(self):
        result = 0
        shift = 0
        while True:
            byte = self.u08()
            result |= ((byte & 0x7F) << shift)
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result
    
    def SLEB128(self):
        result = 0
        shift = 0
        while True:
            byte = self.u08()
            result |= ((byte & 0x7F) << shift)
            shift += 7
            if (byte & 0x80) == 0:
                break
        
        if byte & 0x40:
            result |= -(1 << shift)
        
        return result
    
    def read_type(self, type_name):
        return getattr(self, 'read_'+type_name)()
    
    # Read DW_FORM
    def read_form(self, form):
        return self.read_type(DW_FORM[form])
    
    read_sdata = SLEB128
    read_udata = read_ref_udata = ULEB128
    
    def read_string(self):
        s = bytearray()
        while True:
            c = self.io.read(1)
            if c[0:1] == b'\x00': break
            s[len(s):] = c
        return s.decode('utf8')
    
    def read_strp(self):
        return self.debug_str[self.u32()]
    
    def read_flag(self):
        return (self.u08() != 0)
    
    def read_indirect(self):
        return self.read_form(self.ULEB128())
    
    def read_block1(self):
        return self.io.read(self.u08())
    
    def read_block2(self):
        return self.io.read(self.u16())
    
    def read_block4(self):
        return self.io.read(self.u32())
    
    def read_block(self):
        return self.io.read(self.ULEB128())
    
    def read_expr_block(self, form):
        if   form == DW_FORM.block1:
            length = self.u08()
        elif form == DW_FORM.block2:
            length = self.u16()
        elif form == DW_FORM.block4:
            length = self.u32()
        elif form == DW_FORM.block:
            length = self.ULEB128()
        else:
            raise ParseError("Not an expression block: %s" % DW_FORM[form])
        return Expression(self, length)
    
    def read_expr(self):
        return Expression(self, self.u16())


class SectionLoader(object):
    def __init__(self, dwarf, section_name, Entry):
        """
        Loads all the *Entries* of the given *senction_name*
        """
        self.dwarf = dwarf
        self.section_name = section_name
        self.section = dwarf.sect_dict[section_name]
        
        dwarf.io.seek(self.section.offset)
        
        self.entries = []
        self.entries_dict = {}
        self.offset_index_dict = {}
        i = 0
        while True:
            offset = dwarf.io.tell() - self.section.offset
            if offset >= self.section.size:
                break
            
            entry = Entry(dwarf, offset)
            self.entries.append(entry)
            self.entries_dict[offset] = entry
            
            self.offset_index_dict[offset] = i
            i += 1
    
    def __str__(self):
        return '\n'.join(['\n%s' % self.section_name] +
                [' ' if x is None else str(x) for x in self.entries])


class SectionCache(object):
    def __init__(self, dwarf, section_name, Entry, offset_attr=None):
        """
        Init a cache for the given *section_name*'s *Entries*
        The cache lookup, will work on an offset from the section start.
        Instead of passing the offset number, it is possible to pass an object 
        with the given *offset_attr*.
        """
        if section_name not in dwarf.sect_dict:
            return
        self.dwarf = dwarf
        self.section_name = section_name
        self.section_start = dwarf.sect_dict[section_name].offset
        self.Entry = Entry
        self.offset_attr = offset_attr
        self.__cache = {}
    
    def get(self, key):
        if self.offset_attr is None:
            offset = key
        else:
            offset = getattr(key, self.offset_attr)
        
        if offset not in self.__cache:
            self.dwarf.io.seek(self.section_start + offset)
            self.__cache[offset] = self.Entry(self.dwarf, key)
        
        return self.__cache[offset]


class DwarfString(DwarfStream, ElfStream, StringIO):
    def __init__(self, buffer, bits=ELFCLASS.ELFCLASS32, endianness=ELFDATA.ELFDATA2LSB, addr_size=4):
        StringIO.__init__(self, buffer)
        self.set_bits(bits)
        self.set_endianness(endianness)
        DwarfStream.__init__(self, addr_size)


class DwarfList(DwarfString):
    def __init__(self, list, bits=ELFCLASS.ELFCLASS32, endianness=ELFDATA.ELFDATA2LSB, addr_size=4):
        buffer = ''.join(map(chr, list))
        DwarfString.__init__(self, buffer, bits, endianness, addr_size)


if __name__ == '__main__':
    data = [
        0xE5, 0x8E, 0x26, # unsigned number 624485
        0x9b, 0xf1, 0x59, # signed number -624485
    ]
    
    test_stream = DwarfList(data)
    assert test_stream.ULEB128() == 624485
    assert test_stream.SLEB128() == -624485
    print('OK')
