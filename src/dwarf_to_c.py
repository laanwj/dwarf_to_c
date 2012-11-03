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
from __future__ import print_function, division, unicode_literals
import argparse

import sys, os
from collections import defaultdict

DEBUG=False

# Logging
def error(x):
    print('Error: '+x, file=sys.stderr)
def warning(x):
    print('Warning: '+x, file=sys.stderr)
def progress(x):
    print('* '+x, file=sys.stderr)

# Command-line argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert DWARF annotations in ELF executable to C declarations')
    parser.add_argument('input', metavar='INFILE', type=str, 
            help='Input file (ELF)')
    parser.add_argument('cuname', metavar='CUNAME', type=str, 
            help='Compilation unit name', nargs='*')
    return parser.parse_args()        

from bintools.dwarf import DWARF
from bintools.dwarf.enums import DW_AT, DW_TAG, DW_LANG, DW_ATE, DW_FORM, DW_OP
from pycunparser.c_generator import CGenerator
from pycunparser import c_ast
from dwarfhelpers import get_flag, get_str, get_int, get_ref, not_none, expect_str

# DWARF die to syntax tree fragment
#     Algorithm: realize types when needed for processing
#     keep cache for types that have been built
#    
#     Structs and unions and enums can be predeclared
#     Do this as needed
#     Both anonymous and non-anonymous types can be moved as needed
#     Named types by predeclaring, anonymous types can just be generated where they are needed
class ERROR(object):
    def __init__(self, offset):
        self.offset = offset
    def __call__(self, name):
        raise ValueError('Error: %s (for die %i)' % (name, self.offset))

# Create enum/struct/union <name> to predefine types
TAG_NODE_CONS = {
    DW_TAG.enumeration_type: c_ast.Enum,
    DW_TAG.structure_type:   c_ast.Struct,
    DW_TAG.union_type:       c_ast.Union
}

WRITTEN_NONE = 0   # Nothing has been written about this type
WRITTEN_PREREF = 1 # Predefinition has been written
WRITTEN_FINAL = 2  # Final structure has been written

def unistr(x):
    return unicode(str(x), 'latin-1')

# Syntax tree helpers
def Comment(x):
    return c_ast.DummyNode(postcomment=x) 
def IntConst(n):
    if n is None:
        return None
    return c_ast.Constant('int', str(n))
def EnumItem(key, value):
    return c_ast.Enumerator(key,IntConst(value), postcomment = 
            (('0x%08x' % value) if value>=0 else None))
def SimpleDecl(x):
    return c_ast.Decl(None, [], [], [], x, None, None) 


# Main function to process a Dwarf die to a syntax tree fragment
def to_c_process(die, by_offset, names, rv, written, preref=False):
    if DEBUG:
        print("to_c_process", die.offset, preref)
    def get_type_ref(die, attr):
        '''
        Get type ref for a type attribute.
        A type ref is a function that, given a name, constructs a syntax tree
        for referring to that type.
        '''
        type_ = get_ref(die, 'type')
        if DEBUG:
            print (die.offset, "->", type_)
        if type_ is None:
            ref = base_type_ref('void')
        else:
            ref = names.get(type_)
            if ref is None:
                #ref = base_type_ref('unknown_%i' % type_)
                ref = to_c_process(by_offset[type_], by_offset, names, rv, written, preref=True)
            elif ref is ERROR:
                raise ValueError("Unexpected recursion")
        return ref
        
    names[die.offset] = typeref = ERROR(die.offset) # prevent unbounded recursion

    # Typeref based on name: simple
    name = get_str(die, 'name')
    if name is not None:
        try:
            prefix = TAG_NODE_CONS[die.tag](name, None)
        except KeyError:
            pass
        else: # store early, to allow self-reference
            names[die.offset] = typeref = lambda name: c_ast.TypeDecl(name,[],prefix)
            if preref: # early-out
                return typeref

    if die.tag == DW_TAG.enumeration_type:
        items = []
        for enumval in die.children:
            assert(enumval.tag == DW_TAG.enumerator)
            (sname, const_value) = (not_none(get_str(enumval,'name')), 
                                   not_none(get_int(enumval,'const_value')))
            items.append(EnumItem(sname, const_value))
        enum = c_ast.Enum(name, c_ast.EnumeratorList(items))
        if name is None:
            typeref = anon_ref(enum)
        else:
            if written[(die.tag, name)] != WRITTEN_FINAL:
                rv.append(SimpleDecl(enum))
                written[(die.tag, name)] = WRITTEN_FINAL # typedef is always final

    elif die.tag == DW_TAG.typedef:
        assert(name is not None)
        ref = get_type_ref(die, 'type')
        if written[(die.tag, name)] != WRITTEN_FINAL:
            rv.append(c_ast.Typedef(name, [], ['typedef'], ref(name)))
            written[(die.tag, name)] = WRITTEN_FINAL # typedef is always final
        typeref = base_type_ref(name) 

    elif die.tag == DW_TAG.base_type: # IdentifierType
        if name is None: 
            name = 'unknown_base' #??
        if written[(die.tag, name)] != WRITTEN_FINAL:
            rv.append(Comment("Basetype: %s" % name))
            written[(die.tag, name)] = WRITTEN_FINAL # typedef is always final
        typeref = base_type_ref(name)

    elif die.tag == DW_TAG.pointer_type:
        ref = get_type_ref(die, 'type')
        typeref = ptr_to_ref(ref) 

    elif die.tag in [DW_TAG.const_type, DW_TAG.volatile_type]:
        ref = get_type_ref(die, 'type')
        typeref = qualified_ref(ref, die.tag) 

    elif die.tag in [DW_TAG.structure_type, DW_TAG.union_type]:
        if get_flag(die, 'declaration', False):
            items = None # declaration only
            level = WRITTEN_PREREF
        else:
            items = []
            for enumval in die.children:
                if enumval.tag != DW_TAG.member:
                    warning('Unexpected tag %s inside struct or union (die %i)' %
                            (DW_TAG.fmt(enumval.tag), die.offset))
                    continue
                # data_member_location and bit_size / bit_offset as comment for fields
                bit_size = None
                comment = []
                if 'data_member_location' in enumval.attr_dict:
                    expr = enumval.attr_dict['data_member_location'].value
                    assert(expr.instructions[0].opcode == DW_OP.plus_uconst)
                    comment.append("+0x%x" % expr.instructions[0].operand_1)
                if 'bit_size' in enumval.attr_dict:
                    bit_size = get_int(enumval, 'bit_size')
                if 'bit_offset' in enumval.attr_dict:
                    bit_offset = get_int(enumval, 'bit_offset')
                    comment.append('bit %i..%i' % (bit_offset, bit_offset+bit_size-1))
                if 'byte_size' in enumval.attr_dict:
                    comment.append('of %i' % (8*get_int(enumval, 'byte_size')))
                # TODO: validate member location (alignment), bit offset
                ename = expect_str(enumval.attr_dict['name'])
                ref = get_type_ref(enumval, 'type')
                items.append(c_ast.Decl(ename,[],[],[], ref(ename), None,
                    IntConst(bit_size), postcomment=(' '.join(comment))))
            level = WRITTEN_FINAL

        cons = TAG_NODE_CONS[die.tag](name, items)
        if name is None: # anonymous structure
            typeref = anon_ref(cons)
        else:
            if written[(die.tag,name)] < level:
                rv.append(SimpleDecl(cons))
                written[(die.tag,name)] = level

    elif die.tag == DW_TAG.array_type:
        subtype = get_type_ref(die, 'type')
        count = None
        for val in die.children:
            if val.tag == DW_TAG.subrange_type:
                count = get_int(val, 'upper_bound')
        if count is not None:
            count += 1 # count is upper_bound + 1
        typeref = array_ref(subtype, count) 

    elif die.tag in [DW_TAG.subroutine_type, DW_TAG.subprogram]:
        inline = get_int(die, 'inline', 0)
        returntype = get_type_ref(die, 'type')
        args = []
        for i,val in enumerate(die.children):
            if val.tag == DW_TAG.formal_parameter:
                argtype = get_type_ref(val, 'type')
                argname = get_str(val, 'name', '')
                args.append(c_ast.Typename([], argtype(argname)))
        cons = lambda name: c_ast.FuncDecl(c_ast.ParamList(args), returntype(name))

        if die.tag == DW_TAG.subprogram:
            # Is it somehow specified whether this function is static or external?
            assert(name is not None)
            if written[(die.tag,name)] != WRITTEN_FINAL:
                if inline: # Generate commented declaration for inlined function
                    #rv.append(Comment('\n'.join(cons.generate())))
                    rv.append(Comment('inline %s' % (CGenerator().visit(SimpleDecl(cons(name))))))
                else:
                    rv.append(SimpleDecl(cons(name)))
                written[(die.tag,name)] = WRITTEN_FINAL
        else: # DW_TAG.subroutine_type
            typeref = cons
    else:
        # reference_type, class_type, set_type   etc
        # variable
        if name is None or written[(die.tag,name)] != WRITTEN_FINAL:
            rv.append(Comment("Unhandled: %s\n%s" % (DW_TAG.fmt(die.tag), unistr(die))))
            written[(die.tag,name)] = WRITTEN_FINAL
        warning("unhandled %s (die %i)" % (DW_TAG.fmt(die.tag), die.offset))

    names[die.offset] = typeref
    return typeref

# Functions for manipulating "type references"
# Effectively these are unary functions that return a constructed
# syntax tree from a name.
from functools import partial
def anon_ref(type_def):
    '''Return reference to anonymous struct or enum'''
    return lambda name: c_ast.TypeDecl(name,[],type_def)

def base_type_ref(basetypename):
    basetypename = basetypename.split(' ')
    return lambda x: c_ast.TypeDecl(x,[],c_ast.IdentifierType(basetypename))

def ptr_to_ref(ref):
    return lambda x: c_ast.PtrDecl([], ref(x))

def qualified_ref(ref, tag):
    # XXX nested qualifiers are in reversed order in C
    # tag: DW_TAG.const_type, DW_TAG.volatile_type
    return lambda x: ref(x) #Const(ref(x))

def array_ref(ref, count=None):
    return lambda x: c_ast.ArrayDecl(ref(x), dim=IntConst(count))

# Main conversion function
def parse_dwarf(infile, cuname):
    if not os.path.isfile(infile):
        error("No such file %s" % infile)
        exit(1)
    dwarf = DWARF(infile)
    # Keep track of what has been written to the syntax tree
    # Indexed by (tag,name)
    # Instead of using this, it may be better to just collect and
    # to dedup later, so that we can check that there are no name conflicts.
    written = defaultdict(int) 
    if cuname:
        # TODO: handle multiple specific compilation units
        cu = None
        for i, c in enumerate(dwarf.info.cus):
            if c.name.endswith(cuname[0]):
                cu = c
                break
        if cu is None:
            print("Can't find compilation unit %s" % cuname, file=sys.stderr)
        statements = process_compile_unit(dwarf, cu, written)
    else:
        statements = []
        for cu in dwarf.info.cus:
            progress("Processing %s" % cu.name)
            statements.extend(process_compile_unit(dwarf, cu, written))
    return statements

def process_compile_unit(dwarf, cu, written):
    cu_die = cu.compile_unit
    c_file = cu.name # cu name is main file path
    statements = []
    prev_decl_file = object()
    # Generate actual syntax tree
    names = {} # Defined names for dies, as references, indexed by offset
    for child in cu_die.children:
        decl_file_id = get_int(child, 'decl_file')
        decl_file = cu.get_file_path(decl_file_id) if decl_file_id is not None else None
        # TODO: usefully keep track of decl_file per (final) symbol
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
        name = get_str(child, 'name')
        if name is not None: # non-anonymous
            if DEBUG:
                print("root", child.offset)
            if written[(child.tag, name)] != WRITTEN_FINAL:
                to_c_process(child, cu.dies_dict, names, statements, written)

        prev_decl_file = decl_file
    return statements

def generate_c_code(statements):
    '''Generate syntax tree'''
    rv = c_ast.FileAST(statements)
    #print( rv.show())
    return rv

def main():
    # The main idea is to convert the DWARF tree to a C syntax tree, then 
    # generate C code using cgen
    args = parse_arguments()
    statements = parse_dwarf(args.input,args.cuname)
    ast = generate_c_code(statements)
    progress('Generating output')
    sys.stdout.write(CGenerator().visit(ast))

if __name__ == '__main__':
    main()
