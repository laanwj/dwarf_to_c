"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.dwarf.stream import SectionLoader


class PubName(object):
    def __init__(self, dwarf):
        self.offset = dwarf.u32()
        if self.offset == 0:
            return
        self.name = dwarf.read_string()

    def __str__(self):
        return '%4d: %s' % (self.offset, self.name)


class PubNames(object):
    def __init__(self, dwarf, offset):
        length = dwarf.u32()
        stop = dwarf.io.tell() + length
        dwarf.check_version()
        
        self.info_offset = dwarf.u32()
        self.info_size = dwarf.u32()
        
        self.names = {}
        while dwarf.io.tell() < stop:
            pn = PubName(dwarf)
            if pn.offset != 0:
                self.names[pn.name] = pn
    
    def __str__(self):
        return '\n'.join(['CU: %d' % self.info_offset]+list(map(str, list(self.names.values()))))


class PubNamesLoader(SectionLoader):
    def __init__(self, dwarf):
        SectionLoader.__init__(self, dwarf, '.debug_pubnames', PubNames)
    
    def get_die(self, sym):
        for entry in self.entries:
            if sym in entry.names:
                cu = self.dwarf.info.get_cu_by_offset(entry.info_offset)
                pubname = entry.names[sym]
                return cu.get_die_by_offset(pubname.offset)
        
        raise KeyError('The given symbol 0x%x is not in the public names list' % sym)
