"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.dwarf.stream import SectionLoader


class ARange(object):
    def __init__(self, dwarf):
        self.address = dwarf.read_addr()
        self.length = dwarf.read_addr()
    
    def __str__(self):
        return 'starts at 0x%08x, length of %d' % (self.address, self.length)


class ARanges(object):
    def __init__(self, dwarf, offset):
        start = dwarf.io.tell()
        length = dwarf.u32()
        stop = dwarf.io.tell() + length
        dwarf.check_version()
        
        self.info_offset = dwarf.u32()
        self.addr_size = dwarf.u08()
        self.segm_size = dwarf.u08()

        # Tuples need to be aligned to the tuple size (two words).
        # Note that the alignment needs to be for offset from start of the
        # section and not from the start of the file.
        alignment = 2 * self.addr_size
        current_offset = dwarf.io.tell() - start
        aligned_offset = (current_offset + (alignment - 1)) & ~(alignment - 1)
        dwarf.io.seek(start + aligned_offset)
        
        self.aranges = []
        while dwarf.io.tell() < stop:
            ar = ARange(dwarf)
            if ar.address == 0 and ar.length == 0:
                return
            self.aranges.append(ar)
    
    def contains(self, addr):
        for range in self.aranges:
            if addr >= range.address:
                if (addr - range.address) < range.length:
                    return True
    
    def __str__(self):
        return '\n'.join(['CU: %d' % self.info_offset]+list(map(str, self.aranges)))


class ARangesLoader(SectionLoader):
    def __init__(self, dwarf):
        SectionLoader.__init__(self, dwarf, '.debug_aranges', ARanges)
    
    def get_cu_by_addr(self, addr):
        for entry in self.entries:
            if entry.contains(addr):
                return self.dwarf.info.get_cu_by_offset(entry.info_offset)
        raise KeyError('The given address 0x%x is not within any CU range' % addr)
