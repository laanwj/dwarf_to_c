"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.dwarf.stream import SectionCache


class Ranges(object):
    def __init__(self, dwarf, offset):
        self.entries = []
        
        base_addr = 0
        while True:
            start = dwarf.read_addr()
            end = dwarf.read_addr()
            
            if start == dwarf.max_addr:
                base_addr = end
            elif start == 0 and end == 0:
                break
            else:
                self.entries.append((base_addr+start, base_addr+end))
    
    def __str__(self):
        return '\n'.join(['    0x%08x - 0x%08x' % range for range in self.entries])


class RangesLoader(SectionCache):
    def __init__(self, dwarf):
        SectionCache.__init__(self, dwarf, '.debug_ranges', Ranges)
