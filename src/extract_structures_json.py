#!/usr/bin/python
# (C) W.J. van der Laan 2012
'''
Extract structures from DWARF data to JSON for the C structure
pretty-printer.
'''
from __future__ import print_function, division, unicode_literals
import argparse
import os, sys
from bintools.dwarf import DWARF
from bintools.dwarf.enums import DW_AT, DW_TAG, DW_LANG, DW_ATE, DW_FORM, DW_OP, DW_ATE
from dwarfhelpers import get_flag, get_str, get_int, get_ref, not_none, expect_str
'''
Output format JSON/Python:
  enums
  structures (name, field offsets)
  simple field types (size, type, structure, pointer to structure  + offset)
'''

DEBUG=False 

# Logging
def error(x):
    print('Error: '+x, file=sys.stderr)
def warning(x):
    print('Warning: '+x, file=sys.stderr)
def progress(x):
    print('* '+x, file=sys.stderr)

def type_name(die):
    if die is None:
        return 'void' # predefined nothing type
    type_name = get_str(die, 'name')
    if type_name is None: # Make up a name if it is not provided by DWARF
        return '%s_%i' % (DW_TAG[die.tag], die.offset)
    return type_name

def parse_type(type, dies_dict):
    '''
    Parse type by removing modifiers and counting pointer
    indirections.
    '''
   
    indirection = 0
    while type is not None and type.tag in [DW_TAG.const_type, DW_TAG.volatile_type, DW_TAG.typedef, DW_TAG.pointer_type]:
        if type.tag == DW_TAG.pointer_type:
            indirection += 1
        type = dies_dict.get(get_ref(type, 'type'), None)
    
    return (type, indirection)

def visit_base_type(die,dies_dict):
    type_info = {
        'kind': 'base_type',
        'byte_size': get_int(die, 'byte_size'),
        'encoding': DW_ATE[get_int(die, 'encoding')],
    }
    if DEBUG:
        print(type_info)
    return type_info

def visit_enumeration_type(die,dies_dict):
    type_info = {
        'kind': 'enumeration_type',
        'byte_size': get_int(die, 'byte_size'),
    }
    enumerators = []
    for child in die.children:
        if child.tag != DW_TAG.enumerator:
            continue
        enumerator_info = {
            'name': get_str(child, 'name'),
            'value': get_int(child, 'const_value'),
        }
        enumerators.append(enumerator_info)
        
    type_info['enumerators'] = enumerators
    if DEBUG:
        print(type_info)
    return type_info

def visit_array_type(die,dies_dict):
    type = dies_dict.get(get_ref(die, 'type'))
    (type,indirection) = parse_type(type, dies_dict)
    type_info = {
        'kind': 'array_type',
        'indirection': indirection,
        'type': type_name(type),
        'length': None
    }
    for child in die.children:
        if child.tag != DW_TAG.subrange_type:
            continue
        upper_bound = get_int(child, 'upper_bound')
        if upper_bound is not None:
            type_info['length'] = upper_bound + 1
    if DEBUG:
        print(type_info)
    return type_info

def visit_structure_type(die,dies_dict):
    # enumerate members of structure or union
    type_info = {
        'kind': DW_TAG[die.tag],
        'byte_size': get_int(die, 'byte_size')
    }
    members = []
    for child in die.children:
        name = get_str(child, 'name')
        member_info = {
            'name': name
        }
        # handle union as "structure with all fields at offset 0"
        offset = 0
        if 'data_member_location' in child.attr_dict:
            expr = child.attr_dict['data_member_location'].value
            assert(expr.instructions[0].opcode == DW_OP.plus_uconst)
            offset = expr.instructions[0].operand_1
        
        member_info['offset'] = offset

        type = dies_dict.get(get_ref(child, 'type'))
        (type,indirection) = parse_type(type, dies_dict)
        member_info['indirection'] = indirection
        member_info['type'] = type_name(type)
        members.append(member_info)
        if DEBUG:
            print(member_info)
        worklist.append(type)

    type_info['members'] = members
    return type_info

def process_compile_unit(dwarf, cu, root):
    cu_die = cu.compile_unit
    # Generate actual syntax tree
    global worklist
    global visited
    types = {}
    worklist = []
    for child in cu_die.children:
        visited = set()

        name = get_str(child, 'name')
        if name is not None: # non-anonymous
            if name == root: # nest into this structure
                worklist.append(child)
              
    while worklist:
        die = worklist.pop()
        if die is None or die.offset in visited:
            continue
        visited.add(die.offset)

        if DEBUG:
            print("[%s]" % (type_name(die)))
        if die.tag in [DW_TAG.structure_type, DW_TAG.union_type]:
            type_info = visit_structure_type(die, cu.dies_dict)
        elif die.tag in [DW_TAG.base_type]:
            type_info = visit_base_type(die, cu.dies_dict)
        elif die.tag in [DW_TAG.array_type]:
            type_info = visit_array_type(die, cu.dies_dict)
        elif die.tag in [DW_TAG.enumeration_type]:
            type_info = visit_enumeration_type(die, cu.dies_dict)
        else:
            print('%s not handled' % DW_TAG[die.tag])
            exit(1)

        types[type_name(die)] = type_info

    return types


# Main conversion function
def parse_dwarf(infile, root):
    if not os.path.isfile(infile):
        error("No such file %s" % infile)
        exit(1)
    dwarf = DWARF(infile)

    for cu in dwarf.info.cus:
        progress("Processing %s" % cu.name)
        types = process_compile_unit(dwarf, cu, root)
        if types:
            return types

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract structures from DWARF as parseable format')
    parser.add_argument('input', metavar='INFILE', type=str, 
            help='Input file (ELF)')
    parser.add_argument('root', metavar='INFILE', type=str, 
            help='Root data structure name')
    return parser.parse_args()        

def main():
    import json
    args = parse_arguments()
    types = parse_dwarf(args.input, args.root)
    json.dump(types, sys.stdout,
            sort_keys=True, indent=4, separators=(',', ': '))
    print()

if __name__ == '__main__':
    main()
