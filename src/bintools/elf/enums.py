"""
Copyright (c) 2010, Cambridge Silicon Radio Ltd.
Written by Emilio Monti <emilmont@gmail.com>
"""
from bintools.utils import Enum

ELFCLASS = Enum({
    0x00: 'ELFCLASSNONE',
    0x01: 'ELFCLASS32',
    0x02: 'ELFCLASS64',
})

ELFDATA = Enum({
    0x00: 'ELFDATANONE',
    0x01: 'ELFDATA2LSB',
    0x02: 'ELFDATA2MSB',
})

class STT(object):
    NOTYPE = 0
    OBJECT = 1
    FUNCT = 2
    SECTION = 3
    FILE = 3
    LOPROC = 13
    HIPROC = 15


class STB(object):
    LOCAL = 0
    GLOBAL = 1
    WEAK = 2
    LOPROC = 13
    HIPROC = 15


class SHT(object):
    NULL = 0
    PROGBITS = 1
    SYMTAB = 2
    STRTAB = 3
    RELA = 4
    HASH = 5
    DYNAMIC = 6
    NOTE = 7
    NOBITS = 8
    REL = 9
    SHLIB = 10
    DYNSYM = 11
    LOPROC = 0x70000000
    HIPROC = 0x7fffffff
    LOUSER = 0x80000000
    HIUSER = 0xffffffff


class SHF(object):
    WRITE = 0x1
    ALLOC = 0x2
    EXECINSTR = 0x4
    MASKPROC = 0xf0000000

MACHINE = Enum({
    0	 : 'EM_NONE',          # No machine
    1	 : 'EM_M32',           # AT&T WE 32100
    2	 : 'EM_SPARC',         # SPARC
    3    : 'EM_386',           # Intel 80386
    4	 : 'EM_68K',           # Motorola 68000
    5	 : 'EM_88K',           # Motorola 88000
    6	 : 'EM_486',           # Reserved for future use (was EM_486)
    7	 : 'EM_860',           # Intel 80860
    8	 : 'EM_MIPS',          # MIPS I Architecture
    9	 : 'EM_S370',          # IBM System/370 Processor
    10   : 'EM_MIPS_RS3_LE',   # MIPS RS3000 Little-endian
    15   : 'EM_PARISC',        # Hewlett-Packard PA-RISC
    17   : 'EM_VPP500',        # Fujitsu VPP500
    18   : 'EM_SPARC32PLUS',   # Enhanced instruction set SPARC
    19   : 'EM_960',           # Intel 80960
    20   : 'EM_PPC',           # PowerPC
    21   : 'EM_PPC64',         # 64-bit PowerPC
    22   : 'EM_S390',          # IBM System/390 Processor
    23   : 'EM_SPU',           # IBM SPU/SPC
    36   : 'EM_V800',          # NEC V800
    37   : 'EM_FR20',          # Fujitsu FR20
    38   : 'EM_RH32',          # TRW RH-32
    39   : 'EM_RCE',           # Motorola RCE
    40   : 'EM_ARM',           # Advanced RISC Machines ARM
    41   : 'EM_ALPHA',         # Digital Alpha
    42   : 'EM_SH',            # Hitachi SH
    43   : 'EM_SPARCV9',       # SPARC Version 9
    44   : 'EM_TRICORE',       # Siemens TriCore embedded processor
    45   : 'EM_ARC',           # Argonaut RISC Core, Argonaut Technologies Inc.
    46   : 'EM_H8_300',        # Hitachi H8/300
    47   : 'EM_H8_300H',       # Hitachi H8/300H
    48   : 'EM_H8S',           # Hitachi H8S
    49   : 'EM_H8_500',        # Hitachi H8/500
    50   : 'EM_IA_64',         # Intel IA-64 processor architecture
    51   : 'EM_MIPS_X',        # Stanford MIPS-X
    52   : 'EM_COLDFIRE',      # Motorola ColdFire
    53   : 'EM_68HC12',        # Motorola M68HC12
    54   : 'EM_MMA',           # Fujitsu MMA Multimedia Accelerator
    55   : 'EM_PCP',           # Siemens PCP
    56   : 'EM_NCPU',          # Sony nCPU embedded RISC processor
    57   : 'EM_NDR1',          # Denso NDR1 microprocessor
    58   : 'EM_STARCORE',      # Motorola Star*Core processor
    59   : 'EM_ME16',          # Toyota ME16 processor
    60   : 'EM_ST100',         # STMicroelectronics ST100 processor
    61   : 'EM_TINYJ',         # Advanced Logic Corp. TinyJ embedded processor family
    62   : 'EM_X86_64',        # AMD x86-64 architecture
    63   : 'EM_PDSP',          # Sony DSP Processor
    64   : 'EM_PDP10',         # Digital Equipment Corp. PDP-10
    65   : 'EM_PDP11',         # Digital Equipment Corp. PDP-11
    66   : 'EM_FX66',          # Siemens FX66 microcontroller
    67   : 'EM_ST9PLUS',       # STMicroelectronics ST9+ 8/16 bit microcontroller
    68   : 'EM_ST7',           # STMicroelectronics ST7 8-bit microcontroller
    69   : 'EM_68HC16',        # Motorola MC68HC16 Microcontroller
    70   : 'EM_68HC11',        # Motorola MC68HC11 Microcontroller
    71   : 'EM_68HC08',        # Motorola MC68HC08 Microcontroller
    72   : 'EM_68HC05',        # Motorola MC68HC05 Microcontroller
    73   : 'EM_SVX',           # Silicon Graphics SVx
    74   : 'EM_ST19',          # STMicroelectronics ST19 8-bit microcontroller
    75   : 'EM_VAX',           # Digital VAX
    76   : 'EM_CRIS',          # Axis Communications 32-bit embedded processor
    77   : 'EM_JAVELIN',       # Infineon Technologies 32-bit embedded processor
    78   : 'EM_FIREPATH',      # Element 14 64-bit DSP Processor
    79   : 'EM_ZSP',           # LSI Logic 16-bit DSP Processor
    80   : 'EM_MMIX',          # Donald Knuth's educational 64-bit processor
    81   : 'EM_HUANY',         # Harvard University machine-independent object files
    82   : 'EM_PRISM',         # SiTera Prism
    83   : 'EM_AVR',           # Atmel AVR 8-bit microcontroller
    84   : 'EM_FR30',          # Fujitsu FR30
    85   : 'EM_D10V',          # Mitsubishi D10V
    86   : 'EM_D30V',          # Mitsubishi D30V
    87   : 'EM_V850',          # NEC v850
    88   : 'EM_M32R',          # Mitsubishi M32R
    89   : 'EM_MN10300',       # Matsushita MN10300
    90   : 'EM_MN10200',       # Matsushita MN10200
    91   : 'EM_PJ',            # picoJava
    92   : 'EM_OPENRISC',      # OpenRISC 32-bit embedded processor
    93   : 'EM_ARC_COMPACT',   # ARC International ARCompact processor (old spelling/synonym: EM_ARC_A5)
    94   : 'EM_XTENSA',        # Tensilica Xtensa Architecture
    95   : 'EM_VIDEOCORE',     # Alphamosaic VideoCore processor
    96   : 'EM_TMM_GPP',       # Thompson Multimedia General Purpose Processor
    97   : 'EM_NS32K',         # National Semiconductor 32000 series
    98   : 'EM_TPC',           # Tenor Network TPC processor
    99   : 'EM_SNP1K',         # Trebia SNP 1000 processor
    100  : 'EM_ST200',         # STMicroelectronics (www.st.com) ST200 microcontroller
    101  : 'EM_IP2K',          # Ubicom IP2xxx microcontroller family
    102  : 'EM_MAX',           # MAX Processor
    103  : 'EM_CR',            # National Semiconductor CompactRISC microprocessor
    104  : 'EM_F2MC16',        # Fujitsu F2MC16
    105  : 'EM_MSP430',        # Texas Instruments embedded microcontroller msp430
    106  : 'EM_BLACKFIN',      # Analog Devices Blackfin (DSP) processor
    107  : 'EM_SE_C33',        # S1C33 Family of Seiko Epson processors
    108  : 'EM_SEP',           # Sharp embedded microprocessor
    109  : 'EM_ARCA',          # Arca RISC Microprocessor
    110  : 'EM_UNICORE',       # Microprocessor series from PKU-Unity Ltd. and MPRC of Peking University
    111  : 'EM_EXCESS',        # eXcess: 16/32/64-bit configurable embedded CPU
    112  : 'EM_DXP',           # Icera Semiconductor Inc. Deep Execution Processor
    113  : 'EM_ALTERA_NIOS2',  # Altera Nios II soft-core processor
    114  : 'EM_CRX',           # National Semiconductor CompactRISC CRX microprocessor
    115  : 'EM_XGATE',         # Motorola XGATE embedded processor
    116  : 'EM_C166',          # Infineon C16x/XC16x processor
    117  : 'EM_M16C',          # Renesas M16C series microprocessors
    118  : 'EM_DSPIC30F',      # Microchip Technology dsPIC30F Digital Signal Controller
    119  : 'EM_CE',            # Freescale Communication Engine RISC core
    120  : 'EM_M32C',          # Renesas M32C series microprocessors
    131  : 'EM_TSK3000',       # Altium TSK3000 core
    132  : 'EM_RS08',          # Freescale RS08 embedded processor
    134  : 'EM_ECOG2',         # Cyan Technology eCOG2 microprocessor
    135  : 'EM_SCORE7',        # Sunplus S+core7 RISC processor
    136  : 'EM_DSP24',         # New Japan Radio (NJR) 24-bit DSP Processor
    137  : 'EM_VIDEOCORE3',    # Broadcom VideoCore III processor
    138  : 'EM_LATTICEMICO32', # RISC processor for Lattice FPGA architecture
    139  : 'EM_SE_C17',        # Seiko Epson C17 family
    140  : 'EM_TI_C6000',      # The Texas Instruments TMS320C6000 DSP family
    141  : 'EM_TI_C2000',      # The Texas Instruments TMS320C2000 DSP family
    142  : 'EM_TI_C5500',      # The Texas Instruments TMS320C55x DSP family
    160  : 'EM_MMDSP_PLUS',    # STMicroelectronics 64bit VLIW Data Signal Processor
    161  : 'EM_CYPRESS_M8C',   # Cypress M8C microprocessor
    162  : 'EM_R32C',          # Renesas R32C series microprocessors
    163  : 'EM_TRIMEDIA',      # NXP Semiconductors TriMedia architecture family
    164  : 'EM_QDSP6',         # QUALCOMM DSP6 Processor
    165  : 'EM_8051',          # Intel 8051 and variants
    166  : 'EM_STXP7X',        # STMicroelectronics STxP7x family of configurable and extensible RISC processors
    167  : 'EM_NDS32',         # Andes Technology compact code size embedded RISC processor family
    168  : 'EM_ECOG1',         # Cyan Technology eCOG1X family
    168  : 'EM_ECOG1X',        # Cyan Technology eCOG1X family
    169  : 'EM_MAXQ30',        # Dallas Semiconductor MAXQ30 Core Micro-controllers
    170  : 'EM_XIMO16',        # New Japan Radio (NJR) 16-bit DSP Processor
    171  : 'EM_MANIK',         # M2000 Reconfigurable RISC Microprocessor
    172  : 'EM_CRAYNV2',       # Cray Inc. NV2 vector architecture
    173  : 'EM_RX',            # Renesas RX family
    174  : 'EM_METAG',         # Imagination Technologies META processor architecture
    175  : 'EM_MCST_ELBRUS',   # MCST Elbrus general purpose hardware architecture
    176  : 'EM_ECOG16',        # Cyan Technology eCOG16 family
    177  : 'EM_CR16',          # National Semiconductor CompactRISC CR16 16-bit microprocessor
    178  : 'EM_ETPU',          # Freescale Extended Time Processing Unit
    179  : 'EM_SLE9X',         # Infineon Technologies SLE9X core
    185  : 'EM_AVR32',         # Atmel Corporation 32-bit microprocessor family
    186  : 'EM_STM8',          # STMicroeletronics STM8 8-bit microcontroller
    187  : 'EM_TILE64',        # Tilera TILE64 multicore architecture family
    188  : 'EM_TILEPRO',       # Tilera TILEPro multicore architecture family
    189  : 'EM_MICROBLAZE',    # Xilinx MicroBlaze 32-bit RISC soft processor core
    190  : 'EM_CUDA',          # NVIDIA CUDA architecture
    191  : 'EM_TILEGX',        # Tilera TILE-Gx multicore architecture family
    192  : 'EM_CLOUDSHIELD',   # CloudShield architecture family
})                   