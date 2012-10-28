#!/usr/bin/python
'''
Convert DWARF annotations in ELF executable to C declarations
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
import argparse
import cgen

import sys, os
from collections import defaultdict

DEBUG=False
# TODO: typedef for subroutine types is wrong
# should be (*name) to make C compiler able to distinguish
# return pointer types and pointer type

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert DWARF annotations in ELF executable to C declarations')
    parser.add_argument('input', metavar='INFILE', type=str, 
            help='Input file (ELF)')
    return parser.parse_args()        

from bintools.dwarf import DWARF
from bintools.dwarf.enums import DW_AT, DW_TAG, DW_LANG, DW_ATE, DW_FORM
from cgen import (Module, Include, FunctionBody, FunctionDeclaration, Const, 
        Pointer, Value, Block, Statement, Struct, Value, Enum, EnumItem, 
        Comment, Typedef, Declarator, Union, ArrayOf)

# Functions to "unpack" DWARF attributes
def expect_str(attr):
    assert(attr.form in ['string', 'strp'])
    return attr.value

def expect_int(attr):
    assert(attr.form in ['sdata', 'data1', 'data2', 'data4', 'data8'])
    return attr.value

def expect_ref(attr):
    assert(attr.form in ['ref1', 'ref2', 'ref4', 'ref8'])
    return attr.value

def expect_flag(attr):
    assert(attr.form in ['flag'])
    return attr.value

def get_flag(die, attrname, default=None):
    try:
        attr = die.attr_dict[attrname]
    except KeyError:
        return default
    else:
        return expect_flag(attr)

def get_str(die, attrname, default=None, allow_none=True):
    try:
        attr = die.attr_dict[attrname]
    except KeyError:
        return default
    else:
        return expect_str(attr)

def get_int(die, attrname, default=None):
    try:
        attr = die.attr_dict[attrname]
    except KeyError:
        return default
    else:
        return expect_int(attr)

def get_ref(die, attrname, default=None):
    try:
        attr = die.attr_dict[attrname]
    except KeyError:
        return default
    else:
        return expect_ref(attr)

def not_none(x):
    assert x is not None
    return x

# DWARF die to syntax tree fragment
#     Algorithm: realize types when needed for processing
#     keep cache for types that have been built
#    
#     Structs and unions and enums can be predeclared
#     Do this as needed
#     Both anonymous and non-anonymous types can be moved as needed
#     Named types by predeclaring, anonymous types can just be generated where they are needed
def ERROR(name):
    raise ValueError('Error: %s' % name)

PREREF_PREFIX = {
    DW_TAG.enumeration_type: 'enum',
    DW_TAG.structure_type: 'struct',
    DW_TAG.union_type: 'union'
}

WRITTEN_NONE = 0   # Nothing has been written about this type
WRITTEN_PREREF = 1 # Predefinition has been written
WRITTEN_FINAL = 2  # Final structure has been written

def to_c_process(die, by_offset, names, rv, written, preref=False):
    if DEBUG:
        print "to_c_process", die.offset, preref
    def get_type_ref(die, attr, allow_missing=True):
        '''
        Get type ref for a type attribute.
        A type ref is a function that, given a name, constructs a syntax tree
        for referring to that type.
        '''
        type_ = get_ref(die, 'type')
        if DEBUG:
            print die.offset, "->", type_
        if type_ is None:
            assert(allow_missing) # Allow missing field?
            ref = base_type_ref('void')
        else:
            ref = names.get(type_)
            if ref is None:
                #ref = base_type_ref('unknown_%i' % type_)
                ref = to_c_process(by_offset[type_], by_offset, names, rv, written, preref=True)
            elif ref is ERROR:
                raise ValueError("Unexpected recursion")
        return ref
        
    names[die.offset] = typeref = ERROR # prevent unbounded recursion

    # Typeref based on name: simple
    name = get_str(die, 'name')
    if name is not None:
        try:
            prefix = PREREF_PREFIX[die.tag]
        except KeyError:
            pass
        else: # store early, to allow self-reference
            names[die.offset] = typeref = base_type_ref(prefix + ' ' + name)
            if preref: # early-out
                return typeref

    if die.tag == DW_TAG.enumeration_type:
        items = []
        for enumval in die.children:
            assert(enumval.tag == DW_TAG.enumerator)
            (sname, const_value) = (not_none(get_str(enumval,'name')), 
                                   not_none(get_int(enumval,'const_value')))
            items.append(EnumItem(sname, const_value, Comment('0x%08x' % const_value)))
        if name is None:
            typeref = anon_ref(Enum(name, items))
        else:
            rv.append(Enum(name, items))

    elif die.tag == DW_TAG.typedef:
        assert(name is not None)
        ref = get_type_ref(die, 'type', allow_missing=False)
        rv.append(Typedef(ref(name)))
        written[die.offset] = WRITTEN_FINAL
        typeref = base_type_ref(name) 

    elif die.tag == DW_TAG.base_type:
        if name is None:
            name = 'unknown_base' #??
            rv.append(Comment(str(die)))
        rv.append(Comment("Basetype: %s" % name))
        typeref = base_type_ref(name)

    elif die.tag == DW_TAG.pointer_type:
        ref = get_type_ref(die, 'type')
        typeref = ptr_to_ref(ref) 

    elif die.tag == DW_TAG.const_type:
        ref = get_type_ref(die, 'type', allow_missing=False)
        typeref = const_ref(ref) 

    elif die.tag in [DW_TAG.structure_type, DW_TAG.union_type]:
        if get_flag(die, 'declaration', False):
            items = None # declaration only
        else:
            items = []
            warning = False
            for enumval in die.children:
                assert(enumval.tag == DW_TAG.member)
                # TODO: data_member_location and bit_size / bit_offset as comment for fields...
                if 'bit_size' in enumval.attr_dict or 'bit_offset' in enumval.attr_dict:
                    warning = True
                ename = expect_str(enumval.attr_dict['name'])
                ref = get_type_ref(enumval, 'type', allow_missing=False)
                items.append(ref(ename))
            if warning:
                rv.append(Comment("Warning: this structure contains bitfields"))
        if die.tag == DW_TAG.structure_type:
            cons = Struct(name, items)
        else:
            cons = Union(name, items)
        if name is None: # anonymous structure
            typeref = anon_ref(cons)
        else:
            rv.append(cons)
            written[die.offset] = WRITTEN_FINAL

    elif die.tag == DW_TAG.subroutine_type:
        returntype = get_type_ref(die, 'type')
        args = []
        for val in die.children:
            assert(val.tag == DW_TAG.formal_parameter)
            argtype = get_type_ref(val, 'type')
            argname = get_str(val, 'name', '')
            args.append(argtype(argname))
        typeref = lambda name: Pointer(FunctionDeclaration(returntype(name), args))

    elif die.tag == DW_TAG.array_type:
        subtype = get_type_ref(die, 'type')
        count = None
        for val in die.children:
            if val.tag == DW_TAG.subrange_type:
                count = get_int(val, 'upper_bound')
        if count is not None:
            count += 1 # count is upper_bound + 1
        typeref = array_ref(subtype, count) 

    elif die.tag == DW_TAG.subprogram:
        assert(name is not None)
        inline = get_int(die, 'inline', 0)
        returntype = get_type_ref(die, 'type')
        args = []
        for i,val in enumerate(die.children):
            if val.tag == DW_TAG.formal_parameter:
                argtype = get_type_ref(val, 'type')
                argname = get_str(val, 'name', 'arg%i' % i)
                args.append(argtype(argname))
        cons = FunctionDeclaration(returntype(name), args)
        if inline: # Generate commented declaration for inlined function
            rv.append(Comment('\n'.join(cons.generate())))
        else:
            rv.append(cons)
        written[die.offset] = WRITTEN_FINAL
    else:
        rv.append(Comment("Unhandled: %s\n%s" % (DW_TAG[die.tag], die)))

    names[die.offset] = typeref
    return typeref

# Functions for manipulating "type references"
# Effectively these are unary functions that return a constructed
# syntax tree from a name.
from functools import partial
def anon_ref(type_def):
    '''Return reference to anonymous struct or enum'''
    def name_anon(name):
        '''Name an anonymous object and return it'''
        assert(type_def.name is None) # name of anon object can only be used once
        type_def.name = name
        return type_def 
    return name_anon

def base_type_ref(basetypename):
    return partial(Value, basetypename)

def ptr_to_ref(ref):
    return lambda x: Pointer(ref(x))

def const_ref(ref):
    return lambda x: Const(ref(x))

def array_ref(ref, count=None):
    return lambda x: ArrayOf(ref(x), count=count)

# Main conversion function
def parse_dwarf(infile):
    if not os.path.isfile(infile):
        print >>sys.stderr, "No such file %s" % infile
        exit(1)
    dwarf = DWARF(infile)

    #for i, cu in enumerate(dwarf.info.cus):
    #    print i, cu.name
    cu = dwarf.info.cus[130]
    # enumerate all dies (flat list)
    #for die in cu.dies:
    #    print DW_TAG[die.tag]
    cu_die = cu.compile_unit
    c_file = cu.name # cu name is main file path
    statements = []
    prev_decl_file = object()
    # Collect type information
    by_offset = {}
    for child in cu_die.children:
        by_offset[child.offset] = child 
    # Generate actual syntax tree
    names = {} # Defined names for dies, as references, indexed by offset
    written = defaultdict(int) # What has been written to syntax tree?
    for child in cu_die.children:
        decl_file_id = get_int(child, 'decl_file')
        decl_file = cu.get_file_path(decl_file_id) if decl_file_id is not None else None
        '''
        if decl_file != prev_decl_file:
            if decl_file == c_file:
                s = "Defined in compilation unit"
            elif decl_file is not None:
                s = "Defined in " + decl_file
            else:
                s = "Defined in base"
            statements.append(Comment("======== " + s))
        '''
        if 'name' in child.attr_dict:
            if DEBUG:
                print "root", child.offset
            if written[child.offset] != WRITTEN_FINAL:
                to_c_process(child, by_offset, names, statements, written)

        prev_decl_file = decl_file
    return statements

def generate_c_code(statements):
    '''Generate syntax tree'''
    rv = Module(statements)
    #rv = Module(
    #        [Include('stdio.h'),
    #         Struct(None, [Const(Pointer(Value('int', 'x')))]),
    #         FunctionDeclaration(Const(Pointer(Const(Value('char', 'greet')))), []),
    #         FunctionBody(
    #             FunctionDeclaration(Const(Pointer(Const(Value('char', 'greet')))), []),
    #             Block([Statement('return "hello world"')]))])
    return rv

def main():
    # The idea, basically is to convert the DWARF tree to a C syntax tree, then 
    # generate C code using cgen
    args = parse_arguments()
    statements = parse_dwarf(args.input)
    ast = generate_c_code(statements)
    for line in ast.generate():
        sys.stdout.write(line+'\n')

if __name__ == '__main__':
    main()
