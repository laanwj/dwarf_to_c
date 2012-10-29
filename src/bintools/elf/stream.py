"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from sys import exit
from traceback import print_stack
from struct import unpack

from bintools.elf.exception import *
from bintools.elf.enums import ELFCLASS, ELFDATA

class ElfStream(object):

    def __init__(self, ioboj):
        self.io = ioboj

    def get_io_object():
        return self.io()

    def set_bits(self, bits):
        if bits == ELFCLASS.ELFCLASS32:
            pass
        elif bits == ELFCLASS.ELFCLASS64:
            pass
        else:
            raise ParseError("Invalid elf class")
        self.bits = bits
    
    def set_endianness(self, endianness):       
        if endianness == ELFDATA.ELFDATA2LSB:
            self.u16 = self.ULInt16
            self.u32 = self.ULInt32
            self.u64 = self.ULInt64
            self.s16 = self.SLInt16
            self.s32 = self.SLInt32
            self.s64 = self.SLInt64
        elif endianness == ELFDATA.ELFDATA2MSB:
            self.u16 = self.UBInt16
            self.u32 = self.UBInt32
            self.u64 = self.UBInt64
            self.s16 = self.SBInt16
            self.s32 = self.SBInt32
            self.s64 = self.SBInt64
        else:
            raise ParseError("Invalid data encoding")
        self.endianness = endianness
    
    def fatal(self, msg):
        print('@0x%x FatalError: %s\n' % (self.io.tell(), msg))
        print_stack()
        exit(2)

    def constant(self, length, value):
        const = self.io.read(length) 
        if const != value:
            raise ParseError('Wrong constant: %s != %s' % (const, value))

    def u08(self):
        return ord(self.io.read(1))
    
    def s08(self):
        return unpack('b', self.io.read(1))[0]
    
    def bytes(self, n):
        return list(map(ord, self.io.read(n)))

    def skip(self, length):
        self.io.seek(length, 1)

    # Little Endian
    def ULInt16(self):
        return unpack('<H', self.io.read(2))[0]

    def ULInt32(self):
        return unpack('<I', self.io.read(4))[0]

    def ULInt64(self):
        return unpack('<Q', self.io.read(8))[0]

    def SLInt16(self):
        return unpack('<h', self.io.read(2))[0]

    def SLInt32(self):
        return unpack('<i', self.io.read(4))[0]

    def SLInt64(self):
        return unpack('<q', self.io.read(8))[0]

    # Big Endian
    def UBInt16(self):
        return unpack('>H', self.io.read(2))[0]

    def UBInt32(self):
        return unpack('>I', self.io.read(4))[0]

    def UBInt64(self):
        return unpack('>Q', self.io.read(8))[0]

    def SBInt16(self):
        return unpack('>h', self.io.read(2))[0]

    def SBInt32(self):
        return unpack('>i', self.io.read(4))[0]

    def SBInt64(self):
        return unpack('>q', self.io.read(8))[0]

    def load_entries(self, offset, n, Entry):
        entries = []
        if offset != 0:
            self.io.seek(offset)
            for i in range(int(n)):
                entries.append(Entry(self, i))
        return entries

