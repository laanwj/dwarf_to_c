"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from os.path import join, dirname
from bintools.dwarf.enums import DW_AT, DW_TAG, DW_LANG, DW_ATE, DW_FORM


class Attrib(object):
    def __init__(self, cu, attrib_form):
        self.cu = cu
        self.name = DW_AT[attrib_form.name_id]
        self.form = DW_FORM[attrib_form.form]
        if   self.name in ['location', 'data_member_location', 'frame_base'] and self.form[0:5] == 'block':
            self.value = self.cu.dwarf.read_expr_block(attrib_form.form)
        else:
            self.value = self.cu.dwarf.read_form(attrib_form.form)
    
    def get_value(self):
        if   self.name == 'ranges':
            value = self.cu.dwarf.ranges.get(self.value)
        elif self.name in ['location', 'data_member_location', 'frame_base'] and type(self.value) == int:
            if self.cu.dwarf.loc is None:
                value = self.value	# should be a constant value
            else:
                value = self.cu.dwarf.loc.get_loc_list(self.value)
        else:
            value = self.value
        return value
    
    def get_str(self):
        if   self.name == 'language':
            value = DW_LANG[self.value]
        elif self.name == 'encoding':
            value = DW_ATE[self.value]
        elif self.name in ['decl_file', 'call_file']:
            value = self.cu.get_file_path(self.value)
        elif self.name == 'ranges':
            value = '\n' + str(self.cu.dwarf.ranges.get(self.value))
        elif self.name in ['low_pc', 'high_pc']:
            value = '0x%08x' % self.value
        elif self.name in ['location', 'data_member_location', 'frame_base'] and type(self.value) == int:
            if self.cu.dwarf.loc is None:
                value = self.value	# should be a constant value
            else:
                loc_list = self.cu.dwarf.loc.get_loc_list(self.value)
                value = '\n    ' + '\n    '.join(map(str, loc_list))
        else:
            value = self.value
        return value
    
    def __str__(self):
        return '%s/%s: %s' % (self.name, self.form, self.get_str())


class DIE(object):
    def __init__(self, dwarf, cu, abbrev_dict, level):
        self.cu = cu
        self.offset = dwarf.io.tell() - cu.offset
        self.attr_index = dwarf.ULEB128()
        self.tag = None
        self.attr = []
        self.attr_dict = {}
        
        self.level = level
        
        if self.attr_index == 0:
            return
        
        abbr = abbrev_dict[self.attr_index]
        self.tag = abbr.tag
        
        for attrib_form in abbr.attrib_forms:
            a = Attrib(cu, attrib_form)
            self.attr.append(a)
            self.attr_dict[a.name] = a
        
        self.has_children = abbr.has_children
        self.children = []
    
    def short_description(self):
        description = '<%d> %s ' % (self.offset, DW_TAG[self.tag])
        if 'name' in self.attr_dict:
            description += str(self.attr_dict['name'])
        return description
    
    def __str__(self):
        if self.tag is not None:
            tag = '\n<%d><%d> %s' % (self.level, self.offset, DW_TAG.fmt(self.tag))
        else:
            tag = '\n[None]'
        return '\n'.join(map(str, [tag] + self.attr))


class CU(object):
    def __init__(self, dwarf, overall_offset):
        self.dwarf = dwarf
        self.overall_offset = overall_offset
        self.offset = dwarf.io.tell()
        
        length = dwarf.u32()
        stop = dwarf.io.tell() + length
        
        ver = dwarf.check_version(handled=[2, 3])
        
        abbrev_offset = dwarf.u32()
        self.pointer_size = dwarf.u08()
        
        abbrevs = dwarf.abbrev.get(abbrev_offset)
        self.line_offset = 0
        
        dwarf.io.seek(self.offset+11)
        self.dies = []
        self.dies_dict = {}
        self.root = None
        level = 0
        die_stack = []
        current_parent = None
        while dwarf.io.tell() < stop:
            die = DIE(dwarf, self, abbrevs, level)
            if die.tag is None:
                level -= 1
                current_parent = die_stack.pop()
            else:
                # Add item to die list and dictionary
                self.dies.append(die)
                self.dies_dict[die.offset] = die
                
                # Set Root
                if level == 0:
                    if self.root == None:
                        self.root = die
                    else:
                        raise Exception("I was expecting only one root for Compile Unit")
                
                if current_parent != None:
                    current_parent.children.append(die)
                
                if die.has_children:
                    level += 1
                    die_stack.append(current_parent)
                    current_parent = die
        
        self.compile_unit = self.dies[0]
        self.stmt_list = self.compile_unit.attr_dict['stmt_list'].value
        if 'comd_dir' in self.compile_unit.attr_dict:
            self.comp_dir = self.compile_unit.attr_dict['comp_dir'].value
            self.name = self.compile_unit.attr_dict['name'].value
        else:
            # Assume that self.name contains a full path name
            self.name = self.compile_unit.attr_dict['name'].value
            self.comp_dir = dirname(self.name)
    
    def get_file_path(self, i):
        dir, name = self.dwarf.stmt.get(self).get_file_path(i)
        if dir is None:
            dir = self.comp_dir
        return join(dir, name)
    
    def get_die_by_offset(self, offset):
        return self.dies_dict[offset]
    
    def short_description(self):
        return 'COMPILE_UNIT<%s>' % (self.name)
    
    def __str__(self):
        s = [self.short_description()] + list(map(str, self.dies))
        s.append(str(self.dwarf.stmt.get(self)))
        return '\n' + '\n'.join(s)


class DebugInfoLoader(object):
    def __init__(self, dwarf):
        debug_info = dwarf.sect_dict['.debug_info']
        dwarf.io.seek(debug_info.offset)
        
        overall_offset = 0
        self.cus = []
        self.cus_dict = {}
        self.cus_files = {}
        while True:
            cu = CU(dwarf, overall_offset)
            self.cus.append(cu)
            self.cus_dict[overall_offset] = cu
            self.cus_files[cu.name] = cu
            overall_offset = dwarf.io.tell() - debug_info.offset
            if overall_offset >= debug_info.size:
                break
    
    def get_cu_by_offset(self, offset):
        return self.cus_dict[offset]
    
    def get_cu_by_filename(self, filename):
        return self.cus_files[filename]
    
    def __str__(self):
        return '\n'.join(['.debug_info'] + list(map(str, self.cus)))
