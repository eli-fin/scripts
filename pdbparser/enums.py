import enum
import io

from util import *

class Enums(object):
    ''' All the enums '''
    
    class PdbInfoStreamVersion(enum.Enum):
        VC2 = 19941610
        VC4 = 19950623
        VC41 = 19950814
        V50 = 19960307
        VC98 = 19970604
        VC70Dep = 19990604
        VC70 = 20000404
        VC80 = 20030901
        VC110 = 20091201
        VC140 = 20140508
    
    
    class PdbInfoStreamFeature(enum.Enum):
        VC110 = 20091201
        VC140 = 20140508
        NoTypeMerge = 0x4D544F4E
        MinimalDebugInfo = 0x494E494D
    
    
    class TpiStreamVersion(enum.Enum):
        V40 = 19950410
        V41 = 19951122
        V50 = 19961031
        V70 = 19990903
        V80 = 20040203
    
    
    class CodeView(object):
        ''' CodeView enums '''
        
        class PointerKind(enum.Enum):
            Near16 = 0x00
            Far16 = 0x01
            Huge16 = 0x02
            BasedOnSegment = 0x03
            BasedOnValue = 0x04
            BasedOnSegmentValue = 0x05
            BasedOnAddress = 0x06
            BasedOnSegmentAddress = 0x07
            BasedOnType = 0x08
            BasedOnSelf = 0x09
            Near32 = 0x0a
            Far32 = 0x0b
            Near64 = 0x0c
        
        
        class PointerMode(enum.Enum):
            Pointer = 0x00
            LValueReference = 0x01
            PointerToDataMember = 0x02
            PointerToMemberFunction = 0x03
            RValueReference = 0x04
        
        
        class PointerModifiers(enum.Enum):
            NONE = 0x00
            Flat32 = 0x01
            Volatile = 0x02
            Const = 0x04
            Unaligned = 0x08
            Restrict = 0x10
        
        
        class PointerFlags(enum.Enum):
            WinRTSmartPointer = 0x01
            LValueRefThisPointer = 0x02
            RValueRefThisPointer = 0x04
        
        
        class LEAF_ENUM(enum.Enum):
            ''' from microsoft-pdb\include\cvinfo.h '''
            
            # leaf indices starting records but referenced from symbol records
            
            LF_MODIFIER_16t     = 0x0001
            LF_POINTER_16t      = 0x0002
            LF_ARRAY_16t        = 0x0003
            LF_CLASS_16t        = 0x0004
            LF_STRUCTURE_16t    = 0x0005
            LF_UNION_16t        = 0x0006
            LF_ENUM_16t         = 0x0007
            LF_PROCEDURE_16t    = 0x0008
            LF_MFUNCTION_16t    = 0x0009
            LF_VTSHAPE          = 0x000a
            LF_COBOL0_16t       = 0x000b
            LF_COBOL1           = 0x000c
            LF_BARRAY_16t       = 0x000d
            LF_LABEL            = 0x000e
            LF_NULL             = 0x000f
            LF_NOTTRAN          = 0x0010
            LF_DIMARRAY_16t     = 0x0011
            LF_VFTPATH_16t      = 0x0012
            LF_PRECOMP_16t      = 0x0013       # not referenced from symbol
            LF_ENDPRECOMP       = 0x0014       # not referenced from symbol
            LF_OEM_16t          = 0x0015       # oem definable type string
            LF_TYPESERVER_ST    = 0x0016       # not referenced from symbol
            
            # leaf indices starting records but referenced only from type records
            
            LF_SKIP_16t         = 0x0200
            LF_ARGLIST_16t      = 0x0201
            LF_DEFARG_16t       = 0x0202
            LF_LIST             = 0x0203
            LF_FIELDLIST_16t    = 0x0204
            LF_DERIVED_16t      = 0x0205
            LF_BITFIELD_16t     = 0x0206
            LF_METHODLIST_16t   = 0x0207
            LF_DIMCONU_16t      = 0x0208
            LF_DIMCONLU_16t     = 0x0209
            LF_DIMVARU_16t      = 0x020a
            LF_DIMVARLU_16t     = 0x020b
            LF_REFSYM           = 0x020c
            
            LF_BCLASS_16t       = 0x0400
            LF_VBCLASS_16t      = 0x0401
            LF_IVBCLASS_16t     = 0x0402
            LF_ENUMERATE_ST     = 0x0403
            LF_FRIENDFCN_16t    = 0x0404
            LF_INDEX_16t        = 0x0405
            LF_MEMBER_16t       = 0x0406
            LF_STMEMBER_16t     = 0x0407
            LF_METHOD_16t       = 0x0408
            LF_NESTTYPE_16t     = 0x0409
            LF_VFUNCTAB_16t     = 0x040a
            LF_FRIENDCLS_16t    = 0x040b
            LF_ONEMETHOD_16t    = 0x040c
            LF_VFUNCOFF_16t     = 0x040d
            
            # 2-bit type index versions of leaves, all have the 0x1000 bit set
            
            LF_TI16_MAX         = 0x1000
            
            LF_MODIFIER         = 0x1001
            LF_POINTER          = 0x1002
            LF_ARRAY_ST         = 0x1003
            LF_CLASS_ST         = 0x1004
            LF_STRUCTURE_ST     = 0x1005
            LF_UNION_ST         = 0x1006
            LF_ENUM_ST          = 0x1007
            LF_PROCEDURE        = 0x1008
            LF_MFUNCTION        = 0x1009
            LF_COBOL0           = 0x100a
            LF_BARRAY           = 0x100b
            LF_DIMARRAY_ST      = 0x100c
            LF_VFTPATH          = 0x100d
            LF_PRECOMP_ST       = 0x100e       # not referenced from symbol
            LF_OEM              = 0x100f       # oem definable type string
            LF_ALIAS_ST         = 0x1010       # alias (typedef) type
            LF_OEM2             = 0x1011       # oem definable type string
            
            # leaf indices starting records but referenced only from type records
            
            LF_SKIP             = 0x1200
            LF_ARGLIST          = 0x1201
            LF_DEFARG_ST        = 0x1202
            LF_FIELDLIST        = 0x1203
            LF_DERIVED          = 0x1204
            LF_BITFIELD         = 0x1205
            LF_METHODLIST       = 0x1206
            LF_DIMCONU          = 0x1207
            LF_DIMCONLU         = 0x1208
            LF_DIMVARU          = 0x1209
            LF_DIMVARLU         = 0x120a
            
            LF_BCLASS           = 0x1400
            LF_VBCLASS          = 0x1401
            LF_IVBCLASS         = 0x1402
            LF_FRIENDFCN_ST     = 0x1403
            LF_INDEX            = 0x1404
            LF_MEMBER_ST        = 0x1405
            LF_STMEMBER_ST      = 0x1406
            LF_METHOD_ST        = 0x1407
            LF_NESTTYPE_ST      = 0x1408
            LF_VFUNCTAB         = 0x1409
            LF_FRIENDCLS        = 0x140a
            LF_ONEMETHOD_ST     = 0x140b
            LF_VFUNCOFF         = 0x140c
            LF_NESTTYPEEX_ST    = 0x140d
            LF_MEMBERMODIFY_ST  = 0x140e
            LF_MANAGED_ST       = 0x140f
            
            # Types w/ SZ names
            
            LF_ST_MAX           = 0x1500
            
            LF_TYPESERVER       = 0x1501       # not referenced from symbol
            LF_ENUMERATE        = 0x1502
            LF_ARRAY            = 0x1503
            LF_CLASS            = 0x1504
            LF_STRUCTURE        = 0x1505
            LF_UNION            = 0x1506
            LF_ENUM             = 0x1507
            LF_DIMARRAY         = 0x1508
            LF_PRECOMP          = 0x1509       # not referenced from symbol
            LF_ALIAS            = 0x150a       # alias (typedef) type
            LF_DEFARG           = 0x150b
            LF_FRIENDFCN        = 0x150c
            LF_MEMBER           = 0x150d
            LF_STMEMBER         = 0x150e
            LF_METHOD           = 0x150f
            LF_NESTTYPE         = 0x1510
            LF_ONEMETHOD        = 0x1511
            LF_NESTTYPEEX       = 0x1512
            LF_MEMBERMODIFY     = 0x1513
            LF_MANAGED          = 0x1514
            LF_TYPESERVER2      = 0x1515
            
            LF_STRIDED_ARRAY    = 0x1516    # same as LF_ARRAY, but with stride between adjacent elements
            LF_HLSL             = 0x1517
            LF_MODIFIER_EX      = 0x1518
            LF_INTERFACE        = 0x1519
            LF_BINTERFACE       = 0x151a
            LF_VECTOR           = 0x151b
            LF_MATRIX           = 0x151c
            
            LF_VFTABLE          = 0x151d      # a virtual function table
            LF_ENDOFLEAFRECORD  = LF_VFTABLE
            
            LF_TYPE_LAST        = LF_ENDOFLEAFRECORD + 1 # one greater than the last type record
            LF_TYPE_MAX         = LF_TYPE_LAST - 1
            
            LF_FUNC_ID          = 0x1601    # global func ID
            LF_MFUNC_ID         = 0x1602    # member func ID
            LF_BUILDINFO        = 0x1603    # build info: tool, version, command line, src/pdb file
            LF_SUBSTR_LIST      = 0x1604    # similar to LF_ARGLIST, for list of sub strings
            LF_STRING_ID        = 0x1605    # string ID
            
            LF_UDT_SRC_LINE     = 0x1606    # source and line on where an UDT is defined
                                            # only generated by compiler
            
            LF_UDT_MOD_SRC_LINE = 0x1607    # module, source and line on where an UDT is defined
                                            # only generated by linker
            
            LF_ID_LAST          = LF_UDT_MOD_SRC_LINE + 1 # one greater than the last ID record
            LF_ID_MAX           = LF_ID_LAST - 1
            
            LF_NUMERIC          = 0x8000
            LF_CHAR             = 0x8000
            LF_SHORT            = 0x8001
            LF_USHORT           = 0x8002
            LF_LONG             = 0x8003
            LF_ULONG            = 0x8004
            LF_REAL32           = 0x8005
            LF_REAL64           = 0x8006
            LF_REAL80           = 0x8007
            LF_REAL128          = 0x8008
            LF_QUADWORD         = 0x8009
            LF_UQUADWORD        = 0x800a
            LF_REAL48           = 0x800b
            LF_COMPLEX32        = 0x800c
            LF_COMPLEX64        = 0x800d
            LF_COMPLEX80        = 0x800e
            LF_COMPLEX128       = 0x800f
            LF_VARSTRING        = 0x8010
            
            LF_OCTWORD          = 0x8017
            LF_UOCTWORD         = 0x8018
            
            LF_DECIMAL          = 0x8019
            LF_DATE             = 0x801a
            LF_UTF8STRING       = 0x801b
            
            LF_REAL16           = 0x801c
            
            LF_PAD0             = 0xf0
            LF_PAD1             = 0xf1
            LF_PAD2             = 0xf2
            LF_PAD3             = 0xf3
            LF_PAD4             = 0xf4
            LF_PAD5             = 0xf5
            LF_PAD6             = 0xf6
            LF_PAD7             = 0xf7
            LF_PAD8             = 0xf8
            LF_PAD9             = 0xf9
            LF_PAD10            = 0xfa
            LF_PAD11            = 0xfb
            LF_PAD12            = 0xfc
            LF_PAD13            = 0xfd
            LF_PAD14            = 0xfe
            LF_PAD15            = 0xff
        
        
        class TYPE_ENUM(enum.Enum):
            ''' from microsoft-pdb\include\cvinfo.h '''
            
            #      Special Types
            
            T_NOTYPE        = 0x0000   # uncharacterized type (no type)
            T_ABS           = 0x0001   # absolute symbol
            T_SEGMENT       = 0x0002   # segment type
            T_VOID          = 0x0003   # void
            T_HRESULT       = 0x0008   # OLE/COM HRESULT
            T_32PHRESULT    = 0x0408   # OLE/COM HRESULT __ptr32 *
            T_64PHRESULT    = 0x0608   # OLE/COM HRESULT __ptr64 *
            
            T_PVOID         = 0x0103   # near pointer to void
            T_PFVOID        = 0x0203   # far pointer to void
            T_PHVOID        = 0x0303   # huge pointer to void
            T_32PVOID       = 0x0403   # 32 bit pointer to void
            T_32PFVOID      = 0x0503   # 16:32 pointer to void
            T_64PVOID       = 0x0603   # 64 bit pointer to void
            T_CURRENCY      = 0x0004   # BASIC 8 byte currency value
            T_NBASICSTR     = 0x0005   # Near BASIC string
            T_FBASICSTR     = 0x0006   # Far BASIC string
            T_NOTTRANS      = 0x0007   # type not translated by cvpack
            T_BIT           = 0x0060   # bit
            T_PASCHAR       = 0x0061   # Pascal CHAR
            T_BOOL32FF      = 0x0062   # 32-bit BOOL where true is 0xffffffff
            
            #      Character types
            
            T_CHAR          = 0x0010     # 8 bit signed
            T_PCHAR         = 0x0110     # 16 bit pointer to 8 bit signed
            T_PFCHAR        = 0x0210     # 16:16 far pointer to 8 bit signed
            T_PHCHAR        = 0x0310     # 16:16 huge pointer to 8 bit signed
            T_32PCHAR       = 0x0410     # 32 bit pointer to 8 bit signed
            T_32PFCHAR      = 0x0510     # 16:32 pointer to 8 bit signed
            T_64PCHAR       = 0x0610     # 64 bit pointer to 8 bit signed
            
            T_UCHAR         = 0x0020     # 8 bit unsigned
            T_PUCHAR        = 0x0120     # 16 bit pointer to 8 bit unsigned
            T_PFUCHAR       = 0x0220     # 16:16 far pointer to 8 bit unsigned
            T_PHUCHAR       = 0x0320     # 16:16 huge pointer to 8 bit unsigned
            T_32PUCHAR      = 0x0420     # 32 bit pointer to 8 bit unsigned
            T_32PFUCHAR     = 0x0520     # 16:32 pointer to 8 bit unsigned
            T_64PUCHAR      = 0x0620     # 64 bit pointer to 8 bit unsigned
            
            #      really a character types
            
            T_RCHAR         = 0x0070     # really a char
            T_PRCHAR        = 0x0170     # 16 bit pointer to a real char
            T_PFRCHAR       = 0x0270     # 16:16 far pointer to a real char
            T_PHRCHAR       = 0x0370     # 16:16 huge pointer to a real char
            T_32PRCHAR      = 0x0470     # 32 bit pointer to a real char
            T_32PFRCHAR     = 0x0570     # 16:32 pointer to a real char
            T_64PRCHAR      = 0x0670     # 64 bit pointer to a real char
            
            #      really a wide character types
            
            T_WCHAR         = 0x0071     # wide char
            T_PWCHAR        = 0x0171     # 16 bit pointer to a wide char
            T_PFWCHAR       = 0x0271     # 16:16 far pointer to a wide char
            T_PHWCHAR       = 0x0371     # 16:16 huge pointer to a wide char
            T_32PWCHAR      = 0x0471     # 32 bit pointer to a wide char
            T_32PFWCHAR     = 0x0571     # 16:32 pointer to a wide char
            T_64PWCHAR      = 0x0671     # 64 bit pointer to a wide char
            
            #      really a 16-bit unicode char
            
            T_CHAR16         = 0x007a     # 16-bit unicode char
            T_PCHAR16        = 0x017a     # 16 bit pointer to a 16-bit unicode char
            T_PFCHAR16       = 0x027a     # 16:16 far pointer to a 16-bit unicode char
            T_PHCHAR16       = 0x037a     # 16:16 huge pointer to a 16-bit unicode char
            T_32PCHAR16      = 0x047a     # 32 bit pointer to a 16-bit unicode char
            T_32PFCHAR16     = 0x057a     # 16:32 pointer to a 16-bit unicode char
            T_64PCHAR16      = 0x067a     # 64 bit pointer to a 16-bit unicode char
            
            #      really a 32-bit unicode char
            
            T_CHAR32         = 0x007b     # 32-bit unicode char
            T_PCHAR32        = 0x017b     # 16 bit pointer to a 32-bit unicode char
            T_PFCHAR32       = 0x027b     # 16:16 far pointer to a 32-bit unicode char
            T_PHCHAR32       = 0x037b     # 16:16 huge pointer to a 32-bit unicode char
            T_32PCHAR32      = 0x047b     # 32 bit pointer to a 32-bit unicode char
            T_32PFCHAR32     = 0x057b     # 16:32 pointer to a 32-bit unicode char
            T_64PCHAR32      = 0x067b     # 64 bit pointer to a 32-bit unicode char
            
            #      8 bit int types
            
            T_INT1          = 0x0068     # 8 bit signed int
            T_PINT1         = 0x0168     # 16 bit pointer to 8 bit signed int
            T_PFINT1        = 0x0268     # 16:16 far pointer to 8 bit signed int
            T_PHINT1        = 0x0368     # 16:16 huge pointer to 8 bit signed int
            T_32PINT1       = 0x0468     # 32 bit pointer to 8 bit signed int
            T_32PFINT1      = 0x0568     # 16:32 pointer to 8 bit signed int
            T_64PINT1       = 0x0668     # 64 bit pointer to 8 bit signed int
            
            T_UINT1         = 0x0069     # 8 bit unsigned int
            T_PUINT1        = 0x0169     # 16 bit pointer to 8 bit unsigned int
            T_PFUINT1       = 0x0269     # 16:16 far pointer to 8 bit unsigned int
            T_PHUINT1       = 0x0369     # 16:16 huge pointer to 8 bit unsigned int
            T_32PUINT1      = 0x0469     # 32 bit pointer to 8 bit unsigned int
            T_32PFUINT1     = 0x0569     # 16:32 pointer to 8 bit unsigned int
            T_64PUINT1      = 0x0669     # 64 bit pointer to 8 bit unsigned int
            
            #      16 bit short types
            
            T_SHORT         = 0x0011     # 16 bit signed
            T_PSHORT        = 0x0111     # 16 bit pointer to 16 bit signed
            T_PFSHORT       = 0x0211     # 16:16 far pointer to 16 bit signed
            T_PHSHORT       = 0x0311     # 16:16 huge pointer to 16 bit signed
            T_32PSHORT      = 0x0411     # 32 bit pointer to 16 bit signed
            T_32PFSHORT     = 0x0511     # 16:32 pointer to 16 bit signed
            T_64PSHORT      = 0x0611     # 64 bit pointer to 16 bit signed
            
            T_USHORT        = 0x0021     # 16 bit unsigned
            T_PUSHORT       = 0x0121     # 16 bit pointer to 16 bit unsigned
            T_PFUSHORT      = 0x0221     # 16:16 far pointer to 16 bit unsigned
            T_PHUSHORT      = 0x0321     # 16:16 huge pointer to 16 bit unsigned
            T_32PUSHORT     = 0x0421     # 32 bit pointer to 16 bit unsigned
            T_32PFUSHORT    = 0x0521     # 16:32 pointer to 16 bit unsigned
            T_64PUSHORT     = 0x0621     # 64 bit pointer to 16 bit unsigned
            
            #      16 bit int types
            
            T_INT2          = 0x0072     # 16 bit signed int
            T_PINT2         = 0x0172     # 16 bit pointer to 16 bit signed int
            T_PFINT2        = 0x0272     # 16:16 far pointer to 16 bit signed int
            T_PHINT2        = 0x0372     # 16:16 huge pointer to 16 bit signed int
            T_32PINT2       = 0x0472     # 32 bit pointer to 16 bit signed int
            T_32PFINT2      = 0x0572     # 16:32 pointer to 16 bit signed int
            T_64PINT2       = 0x0672     # 64 bit pointer to 16 bit signed int
            
            T_UINT2         = 0x0073     # 16 bit unsigned int
            T_PUINT2        = 0x0173     # 16 bit pointer to 16 bit unsigned int
            T_PFUINT2       = 0x0273     # 16:16 far pointer to 16 bit unsigned int
            T_PHUINT2       = 0x0373     # 16:16 huge pointer to 16 bit unsigned int
            T_32PUINT2      = 0x0473     # 32 bit pointer to 16 bit unsigned int
            T_32PFUINT2     = 0x0573     # 16:32 pointer to 16 bit unsigned int
            T_64PUINT2      = 0x0673     # 64 bit pointer to 16 bit unsigned int
            
            #      32 bit long types
            
            T_LONG          = 0x0012     # 32 bit signed
            T_ULONG         = 0x0022     # 32 bit unsigned
            T_PLONG         = 0x0112     # 16 bit pointer to 32 bit signed
            T_PULONG        = 0x0122     # 16 bit pointer to 32 bit unsigned
            T_PFLONG        = 0x0212     # 16:16 far pointer to 32 bit signed
            T_PFULONG       = 0x0222     # 16:16 far pointer to 32 bit unsigned
            T_PHLONG        = 0x0312     # 16:16 huge pointer to 32 bit signed
            T_PHULONG       = 0x0322     # 16:16 huge pointer to 32 bit unsigned
            
            T_32PLONG       = 0x0412     # 32 bit pointer to 32 bit signed
            T_32PULONG      = 0x0422     # 32 bit pointer to 32 bit unsigned
            T_32PFLONG      = 0x0512     # 16:32 pointer to 32 bit signed
            T_32PFULONG     = 0x0522     # 16:32 pointer to 32 bit unsigned
            T_64PLONG       = 0x0612     # 64 bit pointer to 32 bit signed
            T_64PULONG      = 0x0622     # 64 bit pointer to 32 bit unsigned
            
            #      32 bit int types
            
            T_INT4          = 0x0074     # 32 bit signed int
            T_PINT4         = 0x0174     # 16 bit pointer to 32 bit signed int
            T_PFINT4        = 0x0274     # 16:16 far pointer to 32 bit signed int
            T_PHINT4        = 0x0374     # 16:16 huge pointer to 32 bit signed int
            T_32PINT4       = 0x0474     # 32 bit pointer to 32 bit signed int
            T_32PFINT4      = 0x0574     # 16:32 pointer to 32 bit signed int
            T_64PINT4       = 0x0674     # 64 bit pointer to 32 bit signed int
            
            T_UINT4         = 0x0075     # 32 bit unsigned int
            T_PUINT4        = 0x0175     # 16 bit pointer to 32 bit unsigned int
            T_PFUINT4       = 0x0275     # 16:16 far pointer to 32 bit unsigned int
            T_PHUINT4       = 0x0375     # 16:16 huge pointer to 32 bit unsigned int
            T_32PUINT4      = 0x0475     # 32 bit pointer to 32 bit unsigned int
            T_32PFUINT4     = 0x0575     # 16:32 pointer to 32 bit unsigned int
            T_64PUINT4      = 0x0675     # 64 bit pointer to 32 bit unsigned int
            
            #      64 bit quad types
            
            T_QUAD          = 0x0013     # 64 bit signed
            T_PQUAD         = 0x0113     # 16 bit pointer to 64 bit signed
            T_PFQUAD        = 0x0213     # 16:16 far pointer to 64 bit signed
            T_PHQUAD        = 0x0313     # 16:16 huge pointer to 64 bit signed
            T_32PQUAD       = 0x0413     # 32 bit pointer to 64 bit signed
            T_32PFQUAD      = 0x0513     # 16:32 pointer to 64 bit signed
            T_64PQUAD       = 0x0613     # 64 bit pointer to 64 bit signed
            
            T_UQUAD         = 0x0023     # 64 bit unsigned
            T_PUQUAD        = 0x0123     # 16 bit pointer to 64 bit unsigned
            T_PFUQUAD       = 0x0223     # 16:16 far pointer to 64 bit unsigned
            T_PHUQUAD       = 0x0323     # 16:16 huge pointer to 64 bit unsigned
            T_32PUQUAD      = 0x0423     # 32 bit pointer to 64 bit unsigned
            T_32PFUQUAD     = 0x0523     # 16:32 pointer to 64 bit unsigned
            T_64PUQUAD      = 0x0623     # 64 bit pointer to 64 bit unsigned
            
            #      64 bit int types
            
            T_INT8          = 0x0076     # 64 bit signed int
            T_PINT8         = 0x0176     # 16 bit pointer to 64 bit signed int
            T_PFINT8        = 0x0276     # 16:16 far pointer to 64 bit signed int
            T_PHINT8        = 0x0376     # 16:16 huge pointer to 64 bit signed int
            T_32PINT8       = 0x0476     # 32 bit pointer to 64 bit signed int
            T_32PFINT8      = 0x0576     # 16:32 pointer to 64 bit signed int
            T_64PINT8       = 0x0676     # 64 bit pointer to 64 bit signed int
            
            T_UINT8         = 0x0077     # 64 bit unsigned int
            T_PUINT8        = 0x0177     # 16 bit pointer to 64 bit unsigned int
            T_PFUINT8       = 0x0277     # 16:16 far pointer to 64 bit unsigned int
            T_PHUINT8       = 0x0377     # 16:16 huge pointer to 64 bit unsigned int
            T_32PUINT8      = 0x0477     # 32 bit pointer to 64 bit unsigned int
            T_32PFUINT8     = 0x0577     # 16:32 pointer to 64 bit unsigned int
            T_64PUINT8      = 0x0677     # 64 bit pointer to 64 bit unsigned int
            
            #      128 bit octet types
            
            T_OCT           = 0x0014    # 128 bit signed
            T_POCT          = 0x0114    # 16 bit pointer to 128 bit signed
            T_PFOCT         = 0x0214    # 16:16 far pointer to 128 bit signed
            T_PHOCT         = 0x0314    # 16:16 huge pointer to 128 bit signed
            T_32POCT        = 0x0414    # 32 bit pointer to 128 bit signed
            T_32PFOCT       = 0x0514    # 16:32 pointer to 128 bit signed
            T_64POCT        = 0x0614    # 64 bit pointer to 128 bit signed
            
            T_UOCT          = 0x0024    # 128 bit unsigned
            T_PUOCT         = 0x0124    # 16 bit pointer to 128 bit unsigned
            T_PFUOCT        = 0x0224    # 16:16 far pointer to 128 bit unsigned
            T_PHUOCT        = 0x0324    # 16:16 huge pointer to 128 bit unsigned
            T_32PUOCT       = 0x0424    # 32 bit pointer to 128 bit unsigned
            T_32PFUOCT      = 0x0524    # 16:32 pointer to 128 bit unsigned
            T_64PUOCT       = 0x0624    # 64 bit pointer to 128 bit unsigned
            
            #      128 bit int types
            
            T_INT16         = 0x0078     # 128 bit signed int
            T_PINT16        = 0x0178     # 16 bit pointer to 128 bit signed int
            T_PFINT16       = 0x0278     # 16:16 far pointer to 128 bit signed int
            T_PHINT16       = 0x0378     # 16:16 huge pointer to 128 bit signed int
            T_32PINT16      = 0x0478     # 32 bit pointer to 128 bit signed int
            T_32PFINT16     = 0x0578     # 16:32 pointer to 128 bit signed int
            T_64PINT16      = 0x0678     # 64 bit pointer to 128 bit signed int
            
            T_UINT16        = 0x0079     # 128 bit unsigned int
            T_PUINT16       = 0x0179     # 16 bit pointer to 128 bit unsigned int
            T_PFUINT16      = 0x0279     # 16:16 far pointer to 128 bit unsigned int
            T_PHUINT16      = 0x0379     # 16:16 huge pointer to 128 bit unsigned int
            T_32PUINT16     = 0x0479     # 32 bit pointer to 128 bit unsigned int
            T_32PFUINT16    = 0x0579     # 16:32 pointer to 128 bit unsigned int
            T_64PUINT16     = 0x0679     # 64 bit pointer to 128 bit unsigned int
            
            #      16 bit real types
            
            T_REAL16        = 0x0046     # 16 bit real
            T_PREAL16       = 0x0146     # 16 bit pointer to 16 bit real
            T_PFREAL16      = 0x0246     # 16:16 far pointer to 16 bit real
            T_PHREAL16      = 0x0346     # 16:16 huge pointer to 16 bit real
            T_32PREAL16     = 0x0446     # 32 bit pointer to 16 bit real
            T_32PFREAL16    = 0x0546     # 16:32 pointer to 16 bit real
            T_64PREAL16     = 0x0646     # 64 bit pointer to 16 bit real
            
            #      32 bit real types
            
            T_REAL32        = 0x0040     # 32 bit real
            T_PREAL32       = 0x0140     # 16 bit pointer to 32 bit real
            T_PFREAL32      = 0x0240     # 16:16 far pointer to 32 bit real
            T_PHREAL32      = 0x0340     # 16:16 huge pointer to 32 bit real
            T_32PREAL32     = 0x0440     # 32 bit pointer to 32 bit real
            T_32PFREAL32    = 0x0540     # 16:32 pointer to 32 bit real
            T_64PREAL32     = 0x0640     # 64 bit pointer to 32 bit real
            
            #      32 bit partial-precision real types
            
            T_REAL32PP      = 0x0045     # 32 bit PP real
            T_PREAL32PP     = 0x0145     # 16 bit pointer to 32 bit PP real
            T_PFREAL32PP    = 0x0245     # 16:16 far pointer to 32 bit PP real
            T_PHREAL32PP    = 0x0345     # 16:16 huge pointer to 32 bit PP real
            T_32PREAL32PP   = 0x0445     # 32 bit pointer to 32 bit PP real
            T_32PFREAL32PP  = 0x0545     # 16:32 pointer to 32 bit PP real
            T_64PREAL32PP   = 0x0645     # 64 bit pointer to 32 bit PP real
            
            #      48 bit real types
            
            T_REAL48        = 0x0044     # 48 bit real
            T_PREAL48       = 0x0144     # 16 bit pointer to 48 bit real
            T_PFREAL48      = 0x0244     # 16:16 far pointer to 48 bit real
            T_PHREAL48      = 0x0344     # 16:16 huge pointer to 48 bit real
            T_32PREAL48     = 0x0444     # 32 bit pointer to 48 bit real
            T_32PFREAL48    = 0x0544     # 16:32 pointer to 48 bit real
            T_64PREAL48     = 0x0644     # 64 bit pointer to 48 bit real
            
            #      64 bit real types
            
            T_REAL64        = 0x0041     # 64 bit real
            T_PREAL64       = 0x0141     # 16 bit pointer to 64 bit real
            T_PFREAL64      = 0x0241     # 16:16 far pointer to 64 bit real
            T_PHREAL64      = 0x0341     # 16:16 huge pointer to 64 bit real
            T_32PREAL64     = 0x0441     # 32 bit pointer to 64 bit real
            T_32PFREAL64    = 0x0541     # 16:32 pointer to 64 bit real
            T_64PREAL64     = 0x0641     # 64 bit pointer to 64 bit real
            
            #      80 bit real types
            
            T_REAL80        = 0x0042     # 80 bit real
            T_PREAL80       = 0x0142     # 16 bit pointer to 80 bit real
            T_PFREAL80      = 0x0242     # 16:16 far pointer to 80 bit real
            T_PHREAL80      = 0x0342     # 16:16 huge pointer to 80 bit real
            T_32PREAL80     = 0x0442     # 32 bit pointer to 80 bit real
            T_32PFREAL80    = 0x0542     # 16:32 pointer to 80 bit real
            T_64PREAL80     = 0x0642     # 64 bit pointer to 80 bit real
            
            #      128 bit real types
            
            T_REAL128       = 0x0043     # 128 bit real
            T_PREAL128      = 0x0143     # 16 bit pointer to 128 bit real
            T_PFREAL128     = 0x0243     # 16:16 far pointer to 128 bit real
            T_PHREAL128     = 0x0343     # 16:16 huge pointer to 128 bit real
            T_32PREAL128    = 0x0443     # 32 bit pointer to 128 bit real
            T_32PFREAL128   = 0x0543     # 16:32 pointer to 128 bit real
            T_64PREAL128    = 0x0643     # 64 bit pointer to 128 bit real
            
            #      32 bit complex types
            
            T_CPLX32        = 0x0050     # 32 bit complex
            T_PCPLX32       = 0x0150     # 16 bit pointer to 32 bit complex
            T_PFCPLX32      = 0x0250     # 16:16 far pointer to 32 bit complex
            T_PHCPLX32      = 0x0350     # 16:16 huge pointer to 32 bit complex
            T_32PCPLX32     = 0x0450     # 32 bit pointer to 32 bit complex
            T_32PFCPLX32    = 0x0550     # 16:32 pointer to 32 bit complex
            T_64PCPLX32     = 0x0650     # 64 bit pointer to 32 bit complex
            
            #      64 bit complex types
            
            T_CPLX64        = 0x0051     # 64 bit complex
            T_PCPLX64       = 0x0151     # 16 bit pointer to 64 bit complex
            T_PFCPLX64      = 0x0251     # 16:16 far pointer to 64 bit complex
            T_PHCPLX64      = 0x0351     # 16:16 huge pointer to 64 bit complex
            T_32PCPLX64     = 0x0451     # 32 bit pointer to 64 bit complex
            T_32PFCPLX64    = 0x0551     # 16:32 pointer to 64 bit complex
            T_64PCPLX64     = 0x0651     # 64 bit pointer to 64 bit complex
            
            #      80 bit complex types
            
            T_CPLX80        = 0x0052     # 80 bit complex
            T_PCPLX80       = 0x0152     # 16 bit pointer to 80 bit complex
            T_PFCPLX80      = 0x0252     # 16:16 far pointer to 80 bit complex
            T_PHCPLX80      = 0x0352     # 16:16 huge pointer to 80 bit complex
            T_32PCPLX80     = 0x0452     # 32 bit pointer to 80 bit complex
            T_32PFCPLX80    = 0x0552     # 16:32 pointer to 80 bit complex
            T_64PCPLX80     = 0x0652     # 64 bit pointer to 80 bit complex
            
            #      128 bit complex types
            
            T_CPLX128       = 0x0053     # 128 bit complex
            T_PCPLX128      = 0x0153     # 16 bit pointer to 128 bit complex
            T_PFCPLX128     = 0x0253     # 16:16 far pointer to 128 bit complex
            T_PHCPLX128     = 0x0353     # 16:16 huge pointer to 128 bit real
            T_32PCPLX128    = 0x0453     # 32 bit pointer to 128 bit complex
            T_32PFCPLX128   = 0x0553     # 16:32 pointer to 128 bit complex
            T_64PCPLX128    = 0x0653     # 64 bit pointer to 128 bit complex
            
            #      boolean types
            
            T_BOOL08        = 0x0030     # 8 bit boolean
            T_PBOOL08       = 0x0130     # 16 bit pointer to  8 bit boolean
            T_PFBOOL08      = 0x0230     # 16:16 far pointer to  8 bit boolean
            T_PHBOOL08      = 0x0330     # 16:16 huge pointer to  8 bit boolean
            T_32PBOOL08     = 0x0430     # 32 bit pointer to 8 bit boolean
            T_32PFBOOL08    = 0x0530     # 16:32 pointer to 8 bit boolean
            T_64PBOOL08     = 0x0630     # 64 bit pointer to 8 bit boolean
            
            T_BOOL16        = 0x0031     # 16 bit boolean
            T_PBOOL16       = 0x0131     # 16 bit pointer to 16 bit boolean
            T_PFBOOL16      = 0x0231     # 16:16 far pointer to 16 bit boolean
            T_PHBOOL16      = 0x0331     # 16:16 huge pointer to 16 bit boolean
            T_32PBOOL16     = 0x0431     # 32 bit pointer to 18 bit boolean
            T_32PFBOOL16    = 0x0531     # 16:32 pointer to 16 bit boolean
            T_64PBOOL16     = 0x0631     # 64 bit pointer to 18 bit boolean
            
            T_BOOL32        = 0x0032     # 32 bit boolean
            T_PBOOL32       = 0x0132     # 16 bit pointer to 32 bit boolean
            T_PFBOOL32      = 0x0232     # 16:16 far pointer to 32 bit boolean
            T_PHBOOL32      = 0x0332     # 16:16 huge pointer to 32 bit boolean
            T_32PBOOL32     = 0x0432     # 32 bit pointer to 32 bit boolean
            T_32PFBOOL32    = 0x0532     # 16:32 pointer to 32 bit boolean
            T_64PBOOL32     = 0x0632     # 64 bit pointer to 32 bit boolean
            
            T_BOOL64        = 0x0033     # 64 bit boolean
            T_PBOOL64       = 0x0133     # 16 bit pointer to 64 bit boolean
            T_PFBOOL64      = 0x0233     # 16:16 far pointer to 64 bit boolean
            T_PHBOOL64      = 0x0333     # 16:16 huge pointer to 64 bit boolean
            T_32PBOOL64     = 0x0433     # 32 bit pointer to 64 bit boolean
            T_32PFBOOL64    = 0x0533     # 16:32 pointer to 64 bit boolean
            T_64PBOOL64     = 0x0633     # 64 bit pointer to 64 bit boolean
            
            # ???
            
            T_NCVPTR        = 0x01f0     # CV Internal type for created near pointers
            T_FCVPTR        = 0x02f0     # CV Internal type for created far pointers
            T_HCVPTR        = 0x03f0     # CV Internal type for created huge pointers
            T_32NCVPTR      = 0x04f0     # CV Internal type for created near 32-bit pointers
            T_32FCVPTR      = 0x05f0     # CV Internal type for created far 32-bit pointers
            T_64NCVPTR      = 0x06f0     # CV Internal type for created near 64-bit pointers
        
        class CV_access(enum.Enum):
            ''' from microsoft-pdb\include\cvinfo.h '''
            CV_private   = 1
            CV_protected = 2
            CV_public    = 3
        
        class CV_methodprop(enum.Enum):
            ''' from microsoft-pdb\include\cvinfo.h '''
            CV_MTvanilla        = 0x00
            CV_MTvirtual        = 0x01
            CV_MTstatic         = 0x02
            CV_MTfriend         = 0x03
            CV_MTintro          = 0x04
            CV_MTpurevirt       = 0x05
            CV_MTpureintro      = 0x06
        
        class CV_HFA(enum.Enum):
            ''' from microsoft-pdb\include\cvinfo.h '''
            CV_HFA_none   =  0
            CV_HFA_float  =  1
            CV_HFA_double =  2
            CV_HFA_other  =  3
        
        class CV_MOCOM_UDT(enum.Enum):
            ''' from microsoft-pdb\include\cvinfo.h '''
            CV_MOCOM_UDT_none      = 0
            CV_MOCOM_UDT_ref       = 1
            CV_MOCOM_UDT_value     = 2
            CV_MOCOM_UDT_interface = 3
        
        #def __trim_flag_values(max_bits_set):
        #    class __modifier_meta(enum.EnumMeta):
        #        def __call__(cls, value, **kwargs):
        #            return enum.EnumMeta.__call__(cls, value & (2**max_bits_set)-1, **kwargs)
        #    return __modifier_meta
        #
        #class CV_modifier(enum.Flag, metaclass=__trim_flag_values(3)):
        #    ''' from microsoft-pdb\include\cvinfo.h '''
        #    # since this is really a bitfield where only the first 3 bits are used (even though higher bits can be set)
        #    # override the metaclass to make sure only the first 3 bits are set
        #    MOD_const       = 0b001
        #    MOD_volatile    = 0b010
        #    MOD_unaligned   = 0b100
        
        def CV_modifier_to_str(mod):
            ''' from microsoft-pdb\include\cvinfo.h, this is a bitfield '''
            ret = ''
            if mod & 0b001: ret += 'MOD_const,'
            if mod & 0b001: ret += 'MOD_volatile,'
            if mod & 0b100: ret += 'MOD_unaligned,'
            return ret[:-1] if ret else 'none'
        
        def CV_fldattr_to_str(attrs):
            ''' from microsoft-pdb\include\cvinfo.h, this is a bitfield '''
            ret = ''
            ret += 'access='+Enums.CodeView.CV_access(attrs&0b11).name+','
            ret += 'methodprop='+Enums.CodeView.CV_methodprop((attrs&0b11100)>>2).name+','
            if attrs & 0b100000: ret += 'pseudo,'
            if attrs & 0b1000000: ret += 'noinherit,'
            if attrs & 0b10000000: ret += 'noconstruct,'
            if attrs & 0b100000000: ret += 'compgenx,'
            if attrs & 0b1000000000: ret += 'sealed,'
            return ret[:-1]
        
        def CV_prop_to_str(props):
            ''' from microsoft-pdb\include\cvinfo.h, this is a bitfield '''
            ret = ''
            if props & 0b1: ret += 'packed,'
            if props & 0b10: ret += 'ctor,'
            if props & 0b100: ret += 'ovlops,'
            if props & 0b1000: ret += 'isnested,'
            if props & 0b10000: ret += 'cnested,'
            if props & 0b100000: ret += 'opassign,'
            if props & 0b1000000: ret += 'opcast,'
            if props & 0b10000000: ret += 'fwdref,'
            if props & 0b100000000: ret += 'scoped,'
            if props & 0b1000000000: ret += 'hasuniquename,'
            if props & 0b10000000000: ret += 'sealed,'
            ret += 'hfa='+Enums.CodeView.CV_HFA((props&0b1100000000000)>>11).name+','
            if props & 0b10000000000000: ret += 'intrinsic,'
            ret += 'mocom='+Enums.CodeView.CV_MOCOM_UDT((props&0b1100000000000000)>>13).name+','
            return ret[:-1]
        