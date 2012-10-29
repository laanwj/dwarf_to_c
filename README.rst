dwarf_to_c
===============
Tool to generate C headers from DWARF debug data.

Can be used to recover types and function signatures from compiled 
executables and libraries with debug information.

Derived packages
=================
pycunparser is based on pycparser, but keeps only the C-generation code
and adds code for handling adding comments.

* cgen: git clone https://github.com/inducer/cgen.git 
  commit: 2a2ee40c32d7c8cef6e64aa712a0c3eddd592352

* pycparser: hg clone https://code.google.com/p/pycparser/ 
  commit: 85c90831e94d 

* pydevtools: svn checkout http://pydevtools.googlecode.com/svn/trunk/ pydevtools-read-only 
  commit: r43

* pytools: git clone https://github.com/inducer/pytools.git
  commit: 431bb3f1069e4d4fda8a2a8abf5250a3831ba3c1

