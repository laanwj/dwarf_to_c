#!/usr/bin/python
'''
List usage of inline functions throughout program.
'''
# Copyright (C) 2012 W.J. van der Laan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
# of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Import as much from the future as we can!
from __future__ import print_function, division, unicode_literals
import argparse, sys, os

from bintools.dwarf import DWARF
from bintools.dwarf.enums import DW_AT, DW_TAG, DW_LANG, DW_ATE, DW_FORM, DW_OP
from dwarfhelpers import get_flag, get_str, get_int, get_ref, not_none, expect_str, get_addr

DEBUG=False
SEP='------------------------------------------------------------------------------------'

# Logging
def error(x):
    print('Error: '+x, file=sys.stderr)
def warning(x):
    print('Warning: '+x, file=sys.stderr)
def progress(x):
    print('* '+x, file=sys.stderr)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Find usages of inline functions')
    parser.add_argument('input', metavar='INPUT', type=str,
            help='ELF input file')
    return parser.parse_args()

def ip_range(die):
    low_pc = get_addr(die, 'low_pc')
    high_pc = get_addr(die, 'high_pc')
    if low_pc is not None and high_pc is not None:
        return '[0x%x-0x%x]' % (low_pc, high_pc)
    else:
        return None

def entry_pc(die):
    pc = get_addr(die, 'entry_pc')
    if pc is not None:
        return '[entry=0x%x]' % pc
    else:
        return None

def get_ref_lookup(die, attr, by_offset):
    '''Get referenced die'''
    try:
        return by_offset[get_ref(die, attr)]
    except KeyError:
        return None

def filter_none(x):
    return (i for i in x if i is not None)

# visitor
def process(die, by_offset, depth):
    # TODO: if lexical scope, print some nice information about parameters and variables
    indent = '  ' * depth
    
    name = get_str(die, 'name')

    # Look up abstract origin
    origin = get_ref_lookup(die, 'abstract_origin', by_offset)
    if origin is not None:
        name = get_str(origin, 'name')
   
    info = [ip_range(die), DW_TAG.fmt(die.tag), name, entry_pc(die)]

    print(indent + (' '.join(filter_none(info))))

    for child in die.children:
        process(child, by_offset, depth+1)

def process_compile_unit(dwarf, cu, out):
    cu_die = cu.compile_unit
    c_file = cu.name # cu name is main file path
    for child in cu_die.children:
        name = get_str(child, 'name')
        if (name is not None and child.tag == DW_TAG.subprogram and 
            'low_pc' in child.attr_dict): # non-anonymous function with memory address
            process(child, cu.dies_dict, 0)
            print()

def parse_dwarf(infile, out):
    if not os.path.isfile(infile):
        error("No such file %s" % infile)
        exit(1)
    dwarf = DWARF(infile)
    # inline functions are restricted to usage within a compilation unit,
    # no need to keep state between them
    for cu in dwarf.info.cus:
        print(SEP)
        print("Compilation unit %s" % cu.name)
        print(SEP)
        process_compile_unit(dwarf, cu, out)


def main():
    # The main idea is to iterate over the DWARF tree, inside subprograms,
    # and find usage of inline functions
    args = parse_arguments()
    parse_dwarf(args.input, sys.stdout)

if __name__ == '__main__':
    main()
