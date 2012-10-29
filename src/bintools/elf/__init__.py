"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.elf.stream import *
from bintools.elf.structs import *
from bintools.elf.exception import ParseError
from io import FileIO
from io import StringIO
import os 


    
class ELF(ElfStream):
    def __init__(self, initer ):
        if isinstance(initer, str):
            #test if initer is path to a file ...
            if os.path.exists(initer) :
                iobj = FileIO(initer,'rb')
            else : 
                # it should be a binary buffer ..
                iobj = StringIO()
                iobj.write(initer)
                iobj.seek(0,os.SEEK_SET)
        else :
            #it should be an io object (StringIO, FiliIO) 
            #(interface will be great in python)
            iobj = initer
        ElfStream.__init__(self,iobj)
        self.iobj = iobj
        
        # HEADER
        self.header = Header(self)
        
        # LOAD PROGRAM and SECTION HEADER TABLES
        self.prog_headers = self.load_entries(self.header.ph_offset, self.header.ph_count, ProgramHeader)
        self.sect_headers = self.load_entries(self.header.sh_offset, self.header.sh_count, SectionHeader)
        
        # LOAD SECTION HEADERS STRING TABLE
        strtab = self.sect_headers[self.header.shstrndx]
        self.shstrtab = StringTable(self.io, strtab.offset, strtab.size)
        
        # Create a section dictionary
        self.sect_dict = {}
        for sec in self.sect_headers:
            self.sect_dict[sec.name] = sec
        
        # LOAD STRING TABLE
        if '.strtab' in self.sect_dict:
            strtab = self.sect_dict['.strtab']
            self.strtab = StringTable(self.io, strtab.offset, strtab.size)

        # LOAD SYMBOL TABLE
        if '.symtab' in self.sect_dict:
            symtab = self.sect_dict['.symtab']
            count = symtab.size / Symbol.LENGTH
            self.symbols = self.load_entries(symtab.offset, count, Symbol)

    def __del__(self):
        if not self.iobj.closed :
            self.iobj.close()
    
    @staticmethod
    def get_from_file(path):
        return ELF(path)
    
    @staticmethod
    def get_from_file_memory_duplicate(path):
        io = FileIO(path,'rb')
        io2 = StringIO()
        io2.write(io.read())
        io.close()
        io2.seek(0, os.SEEK_SET)
        return ELF(io2)
    
    @staticmethod
    def get_from_memory(bytes):
        io2 = StringIO(bytes)
        io2.write(io.read())
        io.close()
        io2.seek(0, os.SEEK_SET)
        return ELF(io2)
    
