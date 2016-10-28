dwarf_to_c
===============
Tool to generate C headers from DWARF debug data.

Can be used to recover types and function signatures from compiled 
executables and libraries with debug information.

!!IMPORTANT NOTE!!
====================

This utility, as well as the underlying library `pydevtools` has limited
support for the more recent DWARF 4 format.

This makes it currently fail on a lot of recent executables.

Patches to improve this are welcome. Unfortunately, `pydevtools` is not
actively maintained, so this would mean either switching to another ELF/DWARF
parsing library ([pyelftools](https://github.com/eliben/pyelftools) looks
promising) or taking up maintenance...

Alternatively, if you have control over compilation, you can specify GCC to
generate DWARF3 instead:

   gcc teest.c -gdwarf-3 -o teest 

In:

```c
struct packet {
    int from, to;
    char name[16];
    int sin:1, ark:1, arg:1, fun:1;
    enum { NEWT, DUCK, WOLF } type;
} x;

int main() { return 0; }
```

Out:

```c
struct packet
{
  int from; /* +0x0 */
  int to; /* +0x4 */
  char name[16]; /* +0x8 */
  int sin:1; /* +0x18 bit 31..31 of 32 */
  int ark:1; /* +0x18 bit 30..30 of 32 */
  int arg:1; /* +0x18 bit 29..29 of 32 */
  int fun:1; /* +0x18 bit 28..28 of 32 */
  enum {
    NEWT = 0, /* 0x00000000 */
    DUCK = 1, /* 0x00000001 */
    WOLF = 2 /* 0x00000002 */
  } type; /* +0x1c */
};
/* Basetype: sizetype */
int main();
```

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

    usage: extract_structures_json.py [-h] INFILE ROOT

Dump DWARF information for data structure ROOT and all substructures into JSON
format. This can be useful for pretty-printers.

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

* pycparser: https://github.com/eliben/pycparser commit: 07f67a2 2012-08-10

* pydevtools: https://github.com/arowser/pydevtools commit: a360056 2012-05-14

Authors
===========
* W.J. van der Laan <laanwj@gmail.com>

