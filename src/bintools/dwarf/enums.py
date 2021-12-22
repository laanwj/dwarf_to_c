"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.utils import Enum


DW_TAG = Enum({
    0x00: 'null',
    0x01: 'array_type',
    0x02: 'class_type',
    0x03: 'entry_point',
    0x04: 'enumeration_type',
    0x05: 'formal_parameter',
    0x08: 'imported_declaration',
    0x0a: 'label',
    0x0b: 'lexical_block',
    0x0d: 'member',
    0x0f: 'pointer_type',
    0x10: 'reference_type',
    0x11: 'compile_unit',
    0x12: 'string_type',
    0x13: 'structure_type',
    0x15: 'subroutine_type',
    0x16: 'typedef',
    0x17: 'union_type',
    0x18: 'unspecified_parameters',
    0x19: 'variant',
    0x1a: 'common_block',
    0x1b: 'common_inclusion',
    0x1c: 'inheritance',
    0x1d: 'inlined_subroutine',
    0x1e: 'module',
    0x1f: 'ptr_to_member_type',
    0x20: 'set_type',
    0x21: 'subrange_type',
    0x22: 'with_stmt',
    0x23: 'access_declaration',
    0x24: 'base_type',
    0x25: 'catch_block',
    0x26: 'const_type',
    0x27: 'constant',
    0x28: 'enumerator',
    0x29: 'file_type',
    0x2a: 'friend',
    0x2b: 'namelist',
    0x2c: 'namelist_item',
    0x2d: 'packed_type',
    0x2e: 'subprogram',
    0x2f: 'template_type_parameter',
    0x30: 'template_value_parameter',
    0x31: 'thrown_type',
    0x32: 'try_block',
    0x33: 'variant_part',
    0x34: 'variable',
    0x35: 'volatile_type',
    0x36: 'dwarf_procedure',
    0x37: 'restrict_type',
    0x38: 'interface_type',
    0x39: 'namespace',
    0x3a: 'imported_module',
    0x3b: 'unspecified_type',
    0x3c: 'partial_unit',
    0x3d: 'imported_unit',
    # 0x3e is reserved
    0x3f: 'condition',
    0x40: 'shared_type',
    0x41: 'type_unit',
    0x42: 'rvalue_reference_type',
    0x43: 'template_alias',

    # New in DWARF v5.
    0x44: 'coarray_type',
    0x45: 'generic_subrange',
    0x46: 'dynamic_type',
    0x47: 'atomic_type',
    0x48: 'call_site',
    0x49: 'call_site_parameter',
    0x4a: 'skeleton_unit',
    0x4b: 'immutable_type',

    0x4080: 'lo_user',
    0xffff: 'hi_user',
})


DW_AT = Enum({
    0x01: 'sibling',
    0x02: 'location',
    0x03: 'name',
    0x09: 'ordering',
    0x0a: 'subscr_data',
    0x0b: 'byte_size',
    0x0c: 'bit_offset',
    0x0d: 'bit_size',
    0x0f: 'element_list',
    0x10: 'stmt_list',
    0x11: 'low_pc',
    0x12: 'high_pc',
    0x13: 'language',
    0x14: 'member',
    0x15: 'discr',
    0x16: 'discr_value',
    0x17: 'visibility',
    0x18: 'import',
    0x19: 'string_length',
    0x1a: 'common_reference',
    0x1b: 'comp_dir',
    0x1c: 'const_value',
    0x1d: 'containing_type',
    0x1e: 'default_value',
    0x20: 'inline',
    0x21: 'is_optional',
    0x22: 'lower_bound',
    0x25: 'producer',
    0x27: 'prototyped',
    0x2a: 'return_addr',
    0x2c: 'start_scope',
    0x2e: 'stride_size',
    0x2f: 'upper_bound',
    0x31: 'abstract_origin',
    0x32: 'accessibility',
    0x33: 'address_class',
    0x34: 'artificial',
    0x35: 'base_types',
    0x36: 'calling_convention',
    0x37: 'count',
    0x38: 'data_member_location',
    0x39: 'decl_column',
    0x3a: 'decl_file',
    0x3b: 'decl_line',
    0x3c: 'declaration',
    0x3d: 'discr_list',
    0x3e: 'encoding',
    0x3f: 'external',
    0x40: 'frame_base',
    0x41: 'friend',
    0x42: 'identifier_case',
    0x43: 'macro_info',
    0x44: 'namelist_items',
    0x45: 'priority',
    0x46: 'segment',
    0x47: 'specification',
    0x48: 'static_link',
    0x49: 'type',
    0x4a: 'use_location',
    0x4b: 'variable_parameter',
    0x4c: 'virtuality',
    0x4d: 'vtable_elem_location',
    # DWARF 3 values
    0x4e: 'allocated',
    0x4f: 'associated',
    0x50: 'data_location',
    0x51: 'stride',
    0x52: 'entry_pc',
    0x53: 'use_UTF8',
    0x54: 'extension',
    0x55: 'ranges',
    0x56: 'trampoline',
    0x57: 'call_column',
    0x58: 'call_file',
    0x59: 'call_line',
    0x5a: 'description',
    0x5b: 'binary_scale',
    0x5c: 'decimal_scale',
    0x5d: 'small',
    0x5e: 'decimal_sign',
    0x5f: 'digit_count',
    0x60: 'picture_string',
    0x61: 'mutable',
    0x62: 'threads_scaled',
    0x63: 'explicit',
    0x64: 'object_pointer',
    0x65: 'endianity',
    0x66: 'elemental',
    0x67: 'pure',
    0x68: 'recursive',
    # DWARF 4 values
    0x69: 'signature',
    0x6a: 'main_subprogram',
    0x6b: 'data_bit_offset',
    0x6c: 'const_expr',
    0x6d: 'enum_class',
    0x6e: 'linkage_name',
    # DWARF 5 values
    0x87: 'noreturn',
    0x88: 'alignment',

    0x2000: 'lo_user',
    0x2007: 'MIPS_linkage_name',

    0x2110: 'GNU_template_name',

    0x2111: 'GNU_call_site_value',
    0x2112: 'GNU_call_site_data_value',
    0x2113: 'GNU_call_site_target',
    0x2114: 'GNU_call_site_target_clobbered',
    0x2115: 'GNU_tail_call',
    0x2116: 'GNU_all_tail_call_sites',
    0x2117: 'GNU_all_call_sites',
    0x2118: 'GNU_all_source_call_sites',
    0x2119: 'GNU_macros',
    0x211a: 'GNU_deleted',

    # Extensions for Fission.  See http://gcc.gnu.org/wiki/DebugFission.
    0x2130: 'GNU_dwo_name',
    0x2131: 'GNU_dwo_id',
    0x2132: 'GNU_ranges_base',
    0x2133: 'GNU_addr_base',
    0x2134: 'GNU_pubnames',
    0x2135: 'GNU_pubtypes',
    0x3fff: 'hi_user',
})


DW_FORM = Enum({
    0x01: 'addr',
    0x03: 'block2',
    0x04: 'block4',
    0x05: 'data2',
    0x06: 'data4',
    0x07: 'data8',
    0x08: 'string',
    0x09: 'block',
    0x0a: 'block1',
    0x0b: 'data1',
    0x0c: 'flag',
    0x0d: 'sdata',
    0x0e: 'strp',
    0x0f: 'udata',
    0x10: 'ref_addr',
    0x11: 'ref1',
    0x12: 'ref2',
    0x13: 'ref4',
    0x14: 'ref8',
    0x15: 'ref_udata',
    0x16: 'indirect',
    0x17: 'sec_offset',
    0x18: 'exprloc',
    0x19: 'flag_present',
    0x20: 'ref_sig8',
})


DW_LANG = {
    0x0001: 'C89',
    0x0002: 'C',
    0x0003: 'Ada83',
    0x0004: 'C_plus_plus',
    0x0005: 'Cobol74',
    0x0006: 'Cobol85',
    0x0007: 'Fortran77',
    0x0008: 'Fortran90',
    0x0009: 'Pascal83',
    0x000a: 'Modula2',
    0x8000: 'lo_user',
    0x8001: 'Mips_Assembler',
    0xffff: 'hi_user',
}


DW_ATE = {
    0x01: 'address',
    0x02: 'boolean',
    0x03: 'complex_float',
    0x04: 'float',
    0x05: 'signed',
    0x06: 'signed_char',
    0x07: 'unsigned',
    0x08: 'unsigned_char',
    0x80: 'lo_user',
    0xff: 'hi_user',
}


class DW_LNS(object):
    extended_op = 0
    copy = 1
    advance_pc = 2
    advance_line = 3
    set_file = 4
    set_column = 5
    negate_stmt = 6
    set_basic_block = 7
    const_add_pc = 8
    fixed_advance_pc = 9


class DW_LNE(object):
    end_sequence = 1
    set_address = 2
    define_file = 3
    set_discriminator = 4


class DW_OP(object):
    addr = 0x03
    deref = 0x06
    const1u = 0x08
    const1s = 0x09
    const2u = 0x0a
    const2s = 0x0b
    const4u = 0x0c
    const4s = 0x0d
    const8u = 0x0e
    const8s = 0x0f
    constu = 0x10
    consts = 0x11
    dup = 0x12
    drop = 0x13
    over = 0x14
    pick = 0x15
    swap = 0x16
    rot = 0x17
    xderef = 0x18
    abs = 0x19
    and_ = 0x1a
    div = 0x1b
    minus = 0x1c
    mod = 0x1d
    mul = 0x1e
    neg = 0x1f
    not_ = 0x20
    or_ = 0x21
    plus = 0x22
    plus_uconst = 0x23
    shl = 0x24
    shr = 0x25
    shra = 0x26
    xor = 0x27
    bra = 0x28
    eq = 0x29
    ge = 0x2a
    gt = 0x2b
    le = 0x2c
    lt = 0x2d
    ne = 0x2e
    skip = 0x2f
    lit0 = 0x30
    lit1 = 0x31
    lit2 = 0x32
    lit3 = 0x33
    lit4 = 0x34
    lit5 = 0x35
    lit6 = 0x36
    lit7 = 0x37
    lit8 = 0x38
    lit9 = 0x39
    lit10 = 0x3a
    lit11 = 0x3b
    lit12 = 0x3c
    lit13 = 0x3d
    lit14 = 0x3e
    lit15 = 0x3f
    lit16 = 0x40
    lit17 = 0x41
    lit18 = 0x42
    lit19 = 0x43
    lit20 = 0x44
    lit21 = 0x45
    lit22 = 0x46
    lit23 = 0x47
    lit24 = 0x48
    lit25 = 0x49
    lit26 = 0x4a
    lit27 = 0x4b
    lit28 = 0x4c
    lit29 = 0x4d
    lit30 = 0x4e
    lit31 = 0x4f
    reg0 = 0x50
    reg1 = 0x51
    reg2 = 0x52
    reg3 = 0x53
    reg4 = 0x54
    reg5 = 0x55
    reg6 = 0x56
    reg7 = 0x57
    reg8 = 0x58
    reg9 = 0x59
    reg10 = 0x5a
    reg11 = 0x5b
    reg12 = 0x5c
    reg13 = 0x5d
    reg14 = 0x5e
    reg15 = 0x5f
    reg16 = 0x60
    reg17 = 0x61
    reg18 = 0x62
    reg19 = 0x63
    reg20 = 0x64
    reg21 = 0x65
    reg22 = 0x66
    reg23 = 0x67
    reg24 = 0x68
    reg25 = 0x69
    reg26 = 0x6a
    reg27 = 0x6b
    reg28 = 0x6c
    reg29 = 0x6d
    reg30 = 0x6e
    reg31 = 0x6f
    breg0 = 0x70
    breg1 = 0x71
    breg2 = 0x72
    breg3 = 0x73
    breg4 = 0x74
    breg5 = 0x75
    breg6 = 0x76
    breg7 = 0x77
    breg8 = 0x78
    breg9 = 0x79
    breg10 = 0x7a
    breg11 = 0x7b
    breg12 = 0x7c
    breg13 = 0x7d
    breg14 = 0x7e
    breg15 = 0x7f
    breg16 = 0x80
    breg17 = 0x81
    breg18 = 0x82
    breg19 = 0x83
    breg20 = 0x84
    breg21 = 0x85
    breg22 = 0x86
    breg23 = 0x87
    breg24 = 0x88
    breg25 = 0x89
    breg26 = 0x8a
    breg27 = 0x8b
    breg28 = 0x8c
    breg29 = 0x8d
    breg30 = 0x8e
    breg31 = 0x8f
    regx = 0x90
    fbreg = 0x91
    bregx = 0x92
    piece = 0x93
    deref_size = 0x94
    xderef_size = 0x95
    nop = 0x96
    push_object_address = 0x97
    call2 = 0x98
    call4 = 0x99
    call_ref = 0x9a
    form_tls_address = 0x9b
    call_frame_cfa = 0x9c
    bit_piece = 0x9d
    implicit_value = 0x9e
    stack_value = 0x9f
    lo_user = 0xe0

    # https://fedorahosted.org/elfutils/wiki/DwarfExtensions
    GNU_uninit = 0xf0
    GNU_encoded_addr = 0xf1
    GNU_implicit_pointer = 0xf2
    GNU_entry_value = 0xf3  # http://www.dwarfstd.org/ShowIssue.php?issue=100909.1
    GNU_const_type = 0xf4 # http://www.dwarfstd.org/doc/040408.1.html
    GNU_regval_type = 0xf5 # http://www.dwarfstd.org/doc/040408.1.html
    GNU_deref_type = 0xf6 # http://www.dwarfstd.org/doc/040408.1.html
    GNU_convert = 0xf7 # http://www.dwarfstd.org/doc/040408.1.html
    GNU_reinterpret = 0xf9
    GNU_parameter_ref = 0xfa # https://gcc.gnu.org/ml/gcc-patches/2011-06/msg00649.html
    GNU_addr_index = 0xfb
    GNU_const_index = 0xfc

    hi_user = 0xff



DW_OP = Enum({
    0x03: 'addr',
    0x06: 'deref',
    0x08: 'const1u',
    0x09: 'const1s',
    0x0a: 'const2u',
    0x0b: 'const2s',
    0x0c: 'const4u',
    0x0d: 'const4s',
    0x0e: 'const8u',
    0x0f: 'const8s',
    0x10: 'constu',
    0x11: 'consts',
    0x12: 'dup',
    0x13: 'drop',
    0x14: 'over',
    0x15: 'pick',
    0x16: 'swap',
    0x17: 'rot',
    0x18: 'xderef',
    0x19: 'abs',
    0x1a: 'and',
    0x1b: 'div',
    0x1c: 'minus',
    0x1d: 'mod',
    0x1e: 'mul',
    0x1f: 'neg',
    0x20: 'not',
    0x21: 'or',
    0x22: 'plus',
    0x23: 'plus_uconst',
    0x24: 'shl',
    0x25: 'shr',
    0x26: 'shra',
    0x27: 'xor',
    0x28: 'bra',
    0x29: 'eq',
    0x2a: 'ge',
    0x2b: 'gt',
    0x2c: 'le',
    0x2d: 'lt',
    0x2e: 'ne',
    0x2f: 'skip',
    0x30: 'lit0',
    0x31: 'lit1',
    0x32: 'lit2',
    0x33: 'lit3',
    0x34: 'lit4',
    0x35: 'lit5',
    0x36: 'lit6',
    0x37: 'lit7',
    0x38: 'lit8',
    0x39: 'lit9',
    0x3a: 'lit10',
    0x3b: 'lit11',
    0x3c: 'lit12',
    0x3d: 'lit13',
    0x3e: 'lit14',
    0x3f: 'lit15',
    0x40: 'lit16',
    0x41: 'lit17',
    0x42: 'lit18',
    0x43: 'lit19',
    0x44: 'lit20',
    0x45: 'lit21',
    0x46: 'lit22',
    0x47: 'lit23',
    0x48: 'lit24',
    0x49: 'lit25',
    0x4a: 'lit26',
    0x4b: 'lit27',
    0x4c: 'lit28',
    0x4d: 'lit29',
    0x4e: 'lit30',
    0x4f: 'lit31',
    0x50: 'reg0',
    0x51: 'reg1',
    0x52: 'reg2',
    0x53: 'reg3',
    0x54: 'reg4',
    0x55: 'reg5',
    0x56: 'reg6',
    0x57: 'reg7',
    0x58: 'reg8',
    0x59: 'reg9',
    0x5a: 'reg10',
    0x5b: 'reg11',
    0x5c: 'reg12',
    0x5d: 'reg13',
    0x5e: 'reg14',
    0x5f: 'reg15',
    0x60: 'reg16',
    0x61: 'reg17',
    0x62: 'reg18',
    0x63: 'reg19',
    0x64: 'reg20',
    0x65: 'reg21',
    0x66: 'reg22',
    0x67: 'reg23',
    0x68: 'reg24',
    0x69: 'reg25',
    0x6a: 'reg26',
    0x6b: 'reg27',
    0x6c: 'reg28',
    0x6d: 'reg29',
    0x6e: 'reg30',
    0x6f: 'reg31',
    0x70: 'breg0',
    0x71: 'breg1',
    0x72: 'breg2',
    0x73: 'breg3',
    0x74: 'breg4',
    0x75: 'breg5',
    0x76: 'breg6',
    0x77: 'breg7',
    0x78: 'breg8',
    0x79: 'breg9',
    0x7a: 'breg10',
    0x7b: 'breg11',
    0x7c: 'breg12',
    0x7d: 'breg13',
    0x7e: 'breg14',
    0x7f: 'breg15',
    0x80: 'breg16',
    0x81: 'breg17',
    0x82: 'breg18',
    0x83: 'breg19',
    0x84: 'breg20',
    0x85: 'breg21',
    0x86: 'breg22',
    0x87: 'breg23',
    0x88: 'breg24',
    0x89: 'breg25',
    0x8a: 'breg26',
    0x8b: 'breg27',
    0x8c: 'breg28',
    0x8d: 'breg29',
    0x8e: 'breg30',
    0x8f: 'breg31',
    0x90: 'regx',
    0x91: 'fbreg',
    0x92: 'bregx',
    0x93: 'piece',
    0x94: 'deref_size',
    0x95: 'xderef_size',
    0x96: 'nop',
    0x97: 'push_object_address',
    0x98: 'call2',
    0x99: 'call4',
    0x9a: 'call_ref',
    0x9b: 'form_tls_address',
    0x9c: 'call_frame_cfa',
    0x9d: 'bit_piece',
    0x9e: 'implicit_value',
    0x9f: 'stack_value',
    0xa0: 'implicit_pointer',
    0xa1: 'addrx',
    0xa2: 'constx',
    0xa3: 'entry_value',
    0xa4: 'const_type',
    0xa5: 'regval_type',
    0xa6: 'deref_type',
    0xa7: 'xderef_type',
    0xa8: 'convert',
    0xa9: 'reinterpret',

    #0xe0: 'lo_user',

    0xe0: 'GNU_push_tls_address',

    0xf0: 'GNU_uninit',
    0xf1: 'GNU_encoded_addr',
    0xf2: 'GNU_implicit_pointer',
    0xf3: 'GNU_entry_value',
    0xf4: 'GNU_const_type',
    0xf5: 'GNU_regval_type',
    0xf6: 'GNU_deref_type',
    0xf7: 'GNU_convert',
    0xf9: 'GNU_reinterpret',
    0xfa: 'GNU_parameter_ref',
    0xfb: 'GNU_addr_index',
    0xfc: 'GNU_const_index',

    0xff: 'hi_user',
})

DW_CFA = Enum({
    0x40: 'advance_loc',
    0x80: 'offset',
    0xc0: 'restore',
    0x00: 'nop',
    0x01: 'set_loc',
    0x02: 'advance_loc1',
    0x03: 'advance_loc2',
    0x04: 'advance_loc4',
    0x05: 'offset_extended',
    0x06: 'restore_extended',
    0x07: 'undefined',
    0x08: 'same_value',
    0x09: 'register',
    0x0a: 'remember_state',
    0x0b: 'restore_state',
    0x0c: 'def_cfa',
    0x0d: 'def_cfa_register',
    0x0e: 'def_cfa_offset',
    # DWARF 3
    0x0f: 'def_cfa_expression',
    0x10: 'expression',
    0x11: 'offset_extended_sf',
    0x12: 'def_cfa_sf',
    0x13: 'def_cfa_offset_sf',
    0x14: 'val_offset',
    0x15: 'val_offset_sf',
    0x16: 'val_expression',
    # SGI/MIPS specific
    0x1d: 'MIPS_advance_loc8',
    # GNU extensions
    0x24: 'GNU_unknown0', #???
    0x2d: 'GNU_window_save',
    0x2e: 'GNU_args_size',
    0x2f: 'GNU_negative_offset_extended',
})
