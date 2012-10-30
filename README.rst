dwarf_to_c
===============
Tool to generate C headers from DWARF debug data.

Can be used to recover types and function signatures from compiled 
executables and libraries with debug information.

Usage
======

    usage: dwarf_to_c.py [-h] INFILE CUNAME

Where INFILE is the name of the ELF binary, and CUNAME is the name of the compilation unit 
(this can be the full name or only the base name, such as `test.c`).

Derived packages
=================

pycunparser is based on pycparser, but keeps only the C-generation code
and adds code for handling adding comments.

`cgen` has a much friendlier API, however it supports a smaller subset of (correct) C. Enumerations
and unions are not supported, which was not that hard to add, however it also could
not handle bit offsets on structure fields, and function pointer support was lacking.
         
So we took the c generation part out of pycparser and adapt it to our needs.

* pycparser: hg clone https://code.google.com/p/pycparser/ 
  commit: 85c90831e94d 

* pydevtools: svn checkout http://pydevtools.googlecode.com/svn/trunk/ pydevtools-read-only 
  commit: r43

* pytools: git clone https://github.com/inducer/pytools.git
  commit: 431bb3f1069e4d4fda8a2a8abf5250a3831ba3c1

