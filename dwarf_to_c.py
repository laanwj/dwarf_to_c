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

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert DWARF annotations in ELF executable to C declarations')
    parser.add_argument('input', metavar='INFILE', type=str, 
            help='Input file (ELF)')
    return parser.parse_args()        

from bintools.dwarf import DWARF
from bintools.dwarf.enums import DW_AT, DW_TAG, DW_LANG, DW_ATE, DW_FORM
from cgen import (Module, Include, FunctionBody, FunctionDeclaration, Const, 
        Pointer, Value, Block, Statement, Struct, Value, Enum, EnumItem, 
        Comment, Typedef, Declarator, Union)

# Functions to "unpack" DWARF attributes
def expect_str(attr):
    assert(attr.form in ['string', 'strp'])
    return attr.value

def expect_str_n(attr):
    if attr is None:
        return None
    assert(attr.form in ['string', 'strp'])
    return attr.value

def expect_int(attr):
    assert(attr.form in ['sdata', 'data1', 'data2', 'data4', 'data8'])
    return attr.value

def expect_int_n(attr):
    if attr is None:
        return None
    assert(attr.form in ['sdata', 'data1', 'data2', 'data4', 'data8'])
    return attr.value

def expect_ref(attr):
    assert(attr.form in ['ref1', 'ref2', 'ref4', 'ref8'])
    return attr.value

def expect_ref_n(attr):
    if attr is None:
        return None
    assert(attr.form in ['ref1', 'ref2', 'ref4', 'ref8'])
    return attr.value

def get_flag(die, attrname, default=None):
    try:
        attr = die.attr_dict[attrname]
    except KeyError:
        return default
    else:
        assert(attr.form in ['flag'])
        return attr.value

def get_str(die, attrname, default=None):
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

# DWARF die to syntax tree fragment
# TODO: forward type references are possible, need to split into two passes
def to_c_process(die, names):
    def get_type_ref(die, attr):
        type_ = expect_ref_n(die.attr_dict.get('type'))
        if type_ is None:
            ref = base_type_ref('void')
        else:
            ref = names.get(type_)
            if ref is None:
                ref = base_type_ref('unknown_%i' % type_)
        return ref
        
    rv = []
    typeref = None
    if die.tag == DW_TAG.enumeration_type:
        items = []
        for enumval in die.children:
            assert(enumval.tag == DW_TAG.enumerator)
            (name, const_value) = (expect_str(enumval.attr_dict['name']), 
                                   expect_int(enumval.attr_dict['const_value']))
            items.append(EnumItem(name, const_value, Comment('0x%08x' % const_value)))
        name = expect_str(die.attr_dict['name']) if 'name' in die.attr_dict else None
        if name is None:
            typeref = anon_ref(Enum(name, items))
        else:
            rv.append(Enum(name, items))
            typeref = base_type_ref('enum ' + name)
    elif die.tag == DW_TAG.typedef:
        name = expect_str(die.attr_dict['name'])
        type_ = expect_ref(die.attr_dict['type'])
        ref = names.get(type_)
        if ref is not None:
            rv.append(Typedef(ref(name)))
            typeref = base_type_ref(name) 
        else:
            rv.append(Comment("Unhandled typedef %s:%i" % (name, type_)))
    elif die.tag == DW_TAG.base_type:
        name = expect_str_n(die.attr_dict.get('name'))
        if name is None:
            name = 'unknown' #??
            rv.append(Comment(str(die)))
        rv.append(Comment("Basetype: %s" % name))
        typeref = base_type_ref(name)
    elif die.tag == DW_TAG.pointer_type:
        type_ = expect_ref_n(die.attr_dict.get('type'))

        if type_ is not None:
            ref = names.get(type_)
        else: # pointer to unspecified type =~ void*
            ref = base_type_ref('void')
        if ref is not None:
            typeref = ptr_to_ref(ref) 
        else:
            rv.append(Comment("Unhandled pointer type to %s" % (type_)))
    elif die.tag == DW_TAG.const_type:
        type_ = expect_ref_n(die.attr_dict.get('type'))
        if type_ is not None:
            ref = names.get(type_)
        if ref is not None:
            typeref = const_ref(ref) 
        else:
            rv.append(Comment("Unhandled const type to %s" % (type_)))
    elif die.tag == DW_TAG.structure_type or die.tag == DW_TAG.union_type:
        if get_flag(die, 'declaration', False):
            items = None # declaration only
        else:
            items = []
            for enumval in die.children:
                assert(enumval.tag == DW_TAG.member)
                # mind bit_size / bit_offset
                # data_member_location...
                name = expect_str(enumval.attr_dict['name'])
                type_ = expect_ref(enumval.attr_dict['type'])
                ref = names.get(type_)
                if ref is None:
                    ref = base_type_ref('unknown_%i' % type_)
                items.append(ref(name))
        name = expect_str(die.attr_dict['name']) if 'name' in die.attr_dict else None
        if die.tag == DW_TAG.structure_type:
            cons = Struct(name, items)
            tname = 'struct'
        else:
            cons = Union(name, items)
            tname = 'union'
        if name is None: # anonymous structure
            typeref = anon_ref(cons)
        else:
            rv.append(cons)
            typeref = base_type_ref(tname + ' ' + name)
    elif 0:# die.tag == DW_TAG.subroutine_type:
        returntype = get_type_ref(die, 'type')
        args = []
        for i,val in enumerate(die.children):
            assert(val.tag == DW_TAG.formal_parameter)
            argtype = get_type_ref(val, 'type')
            argname = get_str(val, 'name', 'arg%i' % i)
            args.append(argtype(argname))
        cons = FunctionDeclaration(returntype, args)
        rv.append(Comment("subroutine"))
        rv.append(cons)
    elif die.tag == DW_TAG.subprogram:
        inline = get_int(die, 'inline', 0)
        returntype = get_type_ref(die, 'type')
        name = get_str(die, 'name') 
        assert(name is not None)
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
    else:
        rv.append(Comment("Unhandled: %s\n%s" % (DW_TAG[die.tag], die)))
    # TODO: subroutine_type
    #       array_type
    #       subprogram
    return (rv, typeref)

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
    names = {} # Defined names for dies, as references, indexed by offset
    for child in cu_die.children:
        decl_file_id = expect_int_n(child.attr_dict.get('decl_file'))
        decl_file = cu.get_file_path(decl_file_id) if decl_file_id is not None else None
        if decl_file != prev_decl_file:
            if decl_file == c_file:
                s = "Defined in compilation unit"
            elif decl_file is not None:
                s = "Defined in " + decl_file
            else:
                s = "Defined in base"
            statements.append(Comment("======== " + s))
        (rv, typeref) = to_c_process(child, names)
        statements.extend(rv)
        if typeref is not None:
            names[child.offset] = typeref

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
