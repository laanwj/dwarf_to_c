"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from array import array
from bintools.elf.stream import ParseError
from bintools.elf.enums import SHT, SHF, MACHINE, ELFCLASS, ELFDATA
import os

class Header(object):
    
    def __init__(self, elf):
        elf.constant(4, b"\x7fELF")
        self.elfclass = elf.u08()
        elf.set_bits(self.elfclass)
        
        self.elfdata = elf.u08()
        elf.set_endianness(self.elfdata)
        
        self.version = elf.u08()
        elf.skip(9)
        
        self.type = elf.u16()
        self.machine = elf.u16()
        self.version = elf.u32()
        if self.elfclass == ELFCLASS.ELFCLASS32:
            self.entry = elf.u32()
            self.ph_offset = elf.u32()
            self.sh_offset = elf.u32()
        elif self.elfclass == ELFCLASS.ELFCLASS64:
            self.entry = elf.u64()
            self.ph_offset = elf.u64()
            self.sh_offset = elf.u64()
        self.flags = elf.u32()
        self.header_size = elf.u16()
        self.ph_entry_size = elf.u16()
        self.ph_count = elf.u16()
        self.sh_entry_size = elf.u16()
        self.sh_count = elf.u16()
        self.shstrndx = elf.u16()

    def __str__(self):
      return ''\
        + "elfclass      %x\n" % self.elfclass\
        + "elfdata       %x\n" % self.elfdata\
        + "version       %x\n" % self.version\
        + "type          %x\n" % self.type\
        + "machine       %x\n" % self.machine\
        + "version       %x\n" % self.version\
        + "entry         %x\n" % self.entry\
        + "ph_offset     %x\n" % self.ph_offset\
        + "sh_offset     %x\n" % self.sh_offset\
        + "flags         %x\n" % self.flags\
        + "header_size   %x\n" % self.header_size\
        + "ph_entry_size %x\n" % self.ph_entry_size\
        + "ph_count      %x\n" % self.ph_count\
        + "sh_entry_size %x\n" % self.sh_entry_size\
        + "sh_count      %x\n" % self.sh_count\
        + "shstrndx      %x\n" % self.shstrndx\

    
    
    

class SectionHeader(object):
    def __init__(self, elf, index):
        self.elf = elf
        self.index = index
        
        if elf.bits == ELFCLASS.ELFCLASS32:
            self.name_index = elf.u32()
            self.type = elf.u32()
            self.flags = elf.u32()
            self.addr = elf.u32()
            self.offset = elf.u32()
            self.size = elf.u32()
            self.link = elf.u32()
            self.info = elf.u32()
            self.addralign = elf.u32()
            self.entsize = elf.u32()
        elif elf.bits == ELFCLASS.ELFCLASS64:
            self.name_index = elf.u32()
            self.type = elf.u32()
            self.flags = elf.u64()
            self.addr = elf.u64()
            self.offset = elf.u64()
            self.size = elf.u64()
            self.link = elf.u32()
            self.info = elf.u32()
            self.addralign = elf.u64()
            self.entsize = elf.u64()
        
        self._name = None
        self._data = None
        
    def is_loadable(self):
        return self.type == SHT.PROGBITS and self.flags & SHF.ALLOC == SHF.ALLOC
    
    def is_execinstr(self):
        return self.flags & SHF.EXECINSTR == SHF.EXECINSTR
     
    # name property ############################################
    @property
    def name(self):
        if self._name == None:
            self._name = self.elf.shstrtab[self.name_index]
        return self._name
        
    @name.setter
    def name(self,value):
        pass

    # symbols property ############################################
    @property
    def symbols(self):
        return [sym for sym in self.elf.symbols if sym.shndx == self.index]
    
    # data property ############################################
    @property 
    def data(self):
        if self._data == None:
            curr_offset = self.elf.io.tell()
            self.elf.io.seek(self.offset, os.SEEK_SET)
            self._data = self.elf.io.read(self.size)
            self.elf.io.seek(curr_offset, os.SEEK_SET)
        return self._data
    
    @data.setter
    def data(self, data):
        if len(data) != len(self.__data) :
            raise ParseError('Size of new data (%d) mismatch with current '
                                'size (%d)' % (len(data), self.size))
        self._data = data
        curr_offset = self.elf.io.tell()
        self.elf.io.seek(self.offset, os.SEEK_SET)
        self.elf.io.read(self.__data)
        self.elf.io.seek(curr_offset, os.SEEK_SET)

class ProgramHeader(object):
    def __init__(self, elf, index):
        self.elf = elf
        self.index = index
        
        if elf.bits == ELFCLASS.ELFCLASS32:
            self.type = elf.u32()
            self.offset = elf.u32()
            self.vaddr = elf.u32()
            self.paddr = elf.u32()
            self.filesz = elf.u32()
            self.memsz = elf.u32()
            self.flags = elf.u32()
            self.align = elf.u32()
        elif elf.bits == ELFCLASS.ELFCLASS64:
            self.type = elf.u32()
            self.flags = elf.u32()
            self.offset = elf.u64()
            self.vaddr = elf.u64()
            self.paddr = elf.u64()
            self.filesz = elf.u64()
            self.memsz = elf.u64()
            self.align = elf.u64()


class Symbol(object):
    LENGTH = 16
    
    def __init__(self, elf, index):
        self.elf = elf
        self.index = index
        
        self.name_index = elf.u32()
        self.value = elf.u32()
        self.size = elf.u32()
        self.info = elf.u08()
        self.other = elf.u08()
        self.shndx = elf.u16()
        
        self._name    = None
        self._section = None
        self._bind    = None
        self._type    = None
        
    # name property ############################################
    @property
    def name(self):
        if self._name == None:
            self._name = self.elf.strtab[self.name_index]
        return self._name
        
    @property
    def section(self):
        if self._section == None:
            special_dict = {
              0xff00 : 'LORESERVE',
              0xff00 : 'LOPROC',
              0xff1f : 'HIPROC',
              0xfff1 : 'ABS',
              0xfff2 : 'COMMON',
              0xffff : 'HIRESERVE',
            }
            if self.shndx in special_dict:
                self._section = special_dict[self.shndx]
            else:
                self._section = self.elf.sect_headers[self.shndx].name
        return self._section
    
    @property
    def bind(self):
        if self._bind == None:
            bind_dict = {
               0 : 'LOCAL',
               1 : 'GLOBAL',
               2 : 'WEAK',
              13 : 'LOPROC',
              15 : 'HIPROC',
            }
            self._bind = bind_dict[self.get_bind()]
        return self._bind

    @property
    def type(self):
        if self._type == None:
            type_dict = {
               0 : 'NOTYPE',
               1 : 'OBJECT',
               2 : 'FUNC',
               3 : 'SECTION',
               4 : 'FILE',
              13 : 'LOPROC',
              15 : 'HIPROC',
            }
            self._type = type_dict[self.get_type()]
        return self._type

    @name.setter
    def name(self,value):
        pass
    
    def get_bind(self):
        return self.info >> 4
    
    def get_type(self):
        return self.info & 0xF


class StringTable(object):
    def __init__(self, stream, offset, size):
        self.offset = offset
        stream.seek(offset)
        self.table = array('B', stream.read(size))
        self.max = len(self.table)
    
    def __getitem__(self, key):
        if (key >= self.max):
            raise ParseError('The required index is out of the table: (0x%x) '
                        '+%d (max=%d)' % (self.offset, key, self.max))
        i = self.table[key:].index(0) + key
        return self.table[key:i].tostring().decode('utf8')
