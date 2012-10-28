"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.elf import ELF
from bintools.elf.enums import ELFCLASS
from bintools.elf.structs import StringTable

from bintools.dwarf.stream import DwarfStream
from bintools.dwarf.abbrev import AbbrevLoader
from bintools.dwarf.info import DebugInfoLoader
from bintools.dwarf.line import StatementProgramLoader
from bintools.dwarf.pubnames import PubNamesLoader
from bintools.dwarf.aranges import ARangesLoader
from bintools.dwarf.ranges import RangesLoader
from bintools.dwarf.frame import FrameLoader
from bintools.dwarf.loc import LocationLoader


class DWARF(ELF, DwarfStream):
    def __init__(self, path, addr_size=4):
        ELF.__init__(self, path)
        if self.bits == ELFCLASS.ELFCLASS64:
            addr_size = 8
        DwarfStream.__init__(self, addr_size)
        
        # DEBUG STRING TABLE
        debug_str = self.sect_dict['.debug_str']
        self.debug_str = StringTable(self.io, debug_str.offset, debug_str.size)
        
        # DEBUG LINE
        self.stmt = StatementProgramLoader(self)
        
        # DEBUG ABBREV
        self.abbrev = AbbrevLoader(self)
        
        # DEBUG INFO
        self.info = DebugInfoLoader(self)
        
        # DEBUG PUBNAMES
        if '.debug_pubnames' in self.sect_dict:
          self.pubnames = PubNamesLoader(self)
        else:
          self.pubnames = None
        
        # DEBUG ARANGES
        self.aranges = ARangesLoader(self)
        
        # DEBUG RANGES
        self.ranges = RangesLoader(self)
        
        # DEBUG FRAME
        if '.debug_frame' in self.sect_dict:
            self.frame = FrameLoader(self)
        else:
            self.frame = None
        
        # DEBUG LOC
        if '.debug_loc' in self.sect_dict:
            self.loc = LocationLoader(self)
        else:
            self.loc = None
    
    # Lookup by location
    def get_addr_by_loc(self, filename, line):
        cu = self.info.get_cu_by_filename(filename)
        lines = self.stmt.get(cu)
        file_index = lines.get_file_index(filename)
        return lines.get_addr_by_loc(file_index, line)
    
    # Lookup by symbol
    def get_loc_by_sym(self, symname):
        die = self.pubnames.get_die(symname)
        decl_file = die.attr_dict['decl_file'].get_value()
        decl_line = die.attr_dict['decl_line'].value
        return (decl_file, decl_line, 0)
    
    def get_addr_by_sym(self, symname):
        die = self.pubnames.get_die(symname)
        file_index = die.attr_dict['decl_file'].value
        decl_line = die.attr_dict['decl_line'].value
        lines = self.stmt.get(die.cu)
        return lines.get_addr_by_loc(file_index, decl_line)
    
    # Lookup by address
    def get_loc_by_addr(self, addr):
        cu = self.aranges.get_cu_by_addr(addr)
        lines = self.stmt.get(cu)
        return lines.get_loc_by_addr(addr)
    
    def __str__(self):
        return '\n'.join(map(str,
                [self.info, self.pubnames, self.aranges, self.frame, self.loc]))
