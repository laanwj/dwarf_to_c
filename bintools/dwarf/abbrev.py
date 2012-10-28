"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.dwarf.stream import SectionCache
from bintools.dwarf.enums import DW_AT, DW_FORM, DW_TAG


class AttribForm(object):
    def __init__(self, name_id, form):
        self.name_id = name_id
        self.form = form

    def __str__(self):
        return '%s: %s' % (DW_AT[self.name_id], DW_FORM[self.form])


class Abbrev(object):
    def __init__(self, stream):
        self.index = stream.ULEB128()
        if self.index == 0:
            return
        
        self.tag = stream.ULEB128()
        self.has_children = stream.u08()
        
        self.attrib_forms = []
        while True:
            name_id = stream.ULEB128()
            form = stream.ULEB128()
            if (name_id == 0) and (form == 0):
                break
            self.attrib_forms.append(AttribForm(name_id, form))

    def __str__(self):
        tag = '\n[%s]' % DW_TAG[self.tag]
        return '\n'.join(map(str, [tag] + self.attrib_forms)) 


def abbrev_dict(dwarf, offset):
    abbrevs = {}
    while True:
        a = Abbrev(dwarf)
        if a.index == 0:
            break
        abbrevs[a.index] = a
    
    return abbrevs


class AbbrevLoader(SectionCache):
    def __init__(self, dwarf):
        SectionCache.__init__(self, dwarf, '.debug_abbrev', abbrev_dict)
