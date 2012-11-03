
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

def expect_addr(attr):
    assert(attr.form in ['addr'])
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

def get_addr(die, attrname, default=None):
    try:
        attr = die.attr_dict[attrname]
    except KeyError:
        return default
    else:
        return expect_addr(attr)

def not_none(x):
    assert x is not None
    return x
