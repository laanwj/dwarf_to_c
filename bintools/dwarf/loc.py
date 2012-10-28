"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.dwarf.stream import SectionLoader


class Location(object):
    def __init__(self, dwarf, begin_addr, end_addr, loc_expr):
        self.dwarf = dwarf
        self.begin_addr = begin_addr
        self.end_addr = end_addr
        self.loc_expr = loc_expr
    
    def __str__(self):
        return '<0x%x:0x%x> %s' % (self.begin_addr, self.end_addr, str(self.loc_expr))


class BaseAddress(object):
    def __init__(self, addr):
        self.addr = addr
    
    def __str__(self):
        return 'base addr: %x' % self.addr


def locationEntry(dwarf, offset):
    """
    Each entry in a location list is either:
      * a base address selection entry
      * an end of list entry
      * a location list entry
    """
    beginning_address = dwarf.read_addr()
    ending_address = dwarf.read_addr()
    
    if beginning_address == dwarf.max_addr:
        """
        An address, which defines the appropriate base address for use in
        interpreting the beginning and ending address offsets of subsequent
        entries of the location list.
        """
        return BaseAddress(ending_address)
    
    if beginning_address == 0 and ending_address == 0:
        # The end of any given location list
        return None
    
    loc_expr = dwarf.read_expr()
    return Location(dwarf, beginning_address, ending_address, loc_expr)


class LocationLoader(SectionLoader):
    def __init__(self, dwarf):
        SectionLoader.__init__(self, dwarf, '.debug_loc', locationEntry)
    
    def get_loc_list(self, offset):
        start = self.offset_index_dict[offset]
        
        end = start
        for i in range(start, len(self.entries)):
            if self.entries[i] is None:
                end = i
                break
        
        return self.entries[start:end]
