dwarf_to_c
===============
Tool to generate C headers from DWARF debug data.

Can be used to recover types and function signatures from compiled 
executables and libraries with debug information.

Usage
======

    usage: dwarf_to_c.py [-h] INFILE [CUNAME]

Where INFILE is the name of an ELF binary, and CUNAME is the name of the compilation unit 
(this can be the full name or only the base name, such as `test.c`).

If CUNAME is left out, all compilation units in the ELF object will be processed.

Misc tools
===========

    usage: inline_functions.py [-h] INPUT

List all usages of inline functions.

Info on used libraries
========================

pycunparser is based on pycparser, but keeps only the C-generation code
and adds code for handling adding comments.

`cgen` has a much friendlier API, however it supports a smaller subset of (correct) C. Enumerations
and unions are not supported, which was not that hard to add, however it also could
not handle bit offsets on structure fields, and function pointer support was lacking
(granted, with C's Byzantine syntax, it's a suprise that anyone gets it right).

So we took the C generation part out of `pycparser` and adapted it to our needs. The parsing
support was stripped as it is not needed for these tools, and to remove the dependency on 
PLY.

* pycparser: hg clone https://code.google.com/p/pycparser/ 
  commit: 85c90831e94d 

* pydevtools: svn checkout http://pydevtools.googlecode.com/svn/trunk/ pydevtools-read-only 
  commit: r43

Authors
===========
* W.J. van der Laan <laanwj@gmail.com>

