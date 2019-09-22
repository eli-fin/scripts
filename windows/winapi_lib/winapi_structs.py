'''
Some non-trivial WinApi structures

Author: Eli Finkel - eyfinkel@gmail.com
'''

import ctypes
from ctypes import wintypes, windll, sizeof, byref

# The WNDPROC callback prototype
WNDPROC = ctypes.CFUNCTYPE(ctypes.c_voidp, wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM)


class GUID(ctypes.Structure):
    '''
    WinApi GUID struct. Commonly used for various purposes.
    -
    implements equality, repr and from_string and provides a copy method
    '''
    _fields_ = [('Data1', wintypes.DWORD   ),
                ('Data2', wintypes.WORD    ),
                ('Data3', wintypes.WORD    ),
                ('Data4', wintypes.BYTE * 8)]
    
    def __eq__(self, other):
        ''' Check equality to other '''
        assert type(other) == GUID, 'other must be a GUID, not '+str(type(other).__name__)
        return self.Data1       == other.Data1          and \
               self.Data2       == other.Data2          and \
               self.Data3       == other.Data3          and \
               list(self.Data4) == list(other.Data4)
    
    def __repr__(self):
        p = ctypes.c_voidp()
        windll.ole32.StringFromCLSID(byref(self), byref(p))
        ret = ctypes.c_wchar_p(p.value).value
        windll.ole32.CoTaskMemFree.argtypes = [ctypes.c_voidp]
        windll.ole32.CoTaskMemFree(p.value)
        return ret
    
    @staticmethod
    def from_string(s):
        assert type(s) == str, 's must be an str, not '+str(type(s).__name__)
        val = GUID()
        ret = windll.ole32.CLSIDFromString(s, byref(val))
        if ret != 0: # HRESULT S_OK
            raise Exception("Invalid GUID string")
        return val
    
    def copy(self):
        new = GUID()
        new.Data1 = self.Data1
        new.Data2 = self.Data2
        new.Data3 = self.Data3
        for i in range(len(self.Data4)):
            new.Data4[i] = self.Data4[i]
        return new
    
    
class SP_DEVINFO_DATA(ctypes.Structure):
    '''
    WinApi class. This represents a single device in a HDEVINFO set.
    -
    cbSize is set
    provides a copy method
    '''
    _fields_ = [('cbSize'   , wintypes.DWORD),
                ('ClassGuid', GUID          ),
                ('DevInst'  , wintypes.DWORD),
                ('Reserved' , ctypes.c_voidp)] # this field ULONG_PTR -> __int3264, so c_voidp should be fine
    
    def __init__(self):
        super().__init__()
        self.cbSize = sizeof(self) # This always needs to be done before using the structure
    
    def copy(self):
        new = SP_DEVINFO_DATA()
        new.cbSize    = self.cbSize
        new.ClassGuid = self.ClassGuid.copy()
        new.DevInst   = self.DevInst
        new.Reserved  = self.Reserved
        return new
    
    
class SP_CLASSINSTALL_HEADER(ctypes.Structure):
    '''
    WinApi class. This is the first member of any class install parameters structure.
    -
    cbSize is set
    '''

    _fields_ = [('cbSize'         , wintypes.DWORD),
                ('InstallFunction', ctypes.c_uint )]
    
    def __init__(self):
        super().__init__()
        self.cbSize = sizeof(self) # This always needs to be done before using the structure
    
    
class SP_PROPCHANGE_PARAMS (ctypes.Structure):
    '''
    WinApi class. Used for class installation request.
    '''

    _fields_ = [('ClassInstallHeader', SP_CLASSINSTALL_HEADER),
                ('StateChange'       , wintypes.DWORD        ),
                ('Scope'             , wintypes.DWORD        ),
                ('HwProfile'         , wintypes.DWORD        )]
    
    
    def __init__(self):
        super().__init__()
        self.ClassInstallHeader.__init__() # Not sure why this doesn't happen by itself
    
    
class NOTIFYICONDATA(ctypes.Structure):
    '''
    WinApi class. Used for a notification icon.
    NOTE: This intended for use with W functions (unicode api)
    '''
    
    class _tmp_union(ctypes.Union):
        _fields_ = [('uTimeout', wintypes.UINT),
                    ('uVersion', wintypes.UINT)]
    
    _fields_ = [('cbSize'           , wintypes.DWORD      ),
                ('hWnd'             , wintypes.HWND       ),
                ('uID'              , wintypes.UINT       ),
                ('uFlags'           , wintypes.UINT       ),
                ('uCallbackMessage' , wintypes.UINT       ),
                ('hIcon'            , wintypes.HICON      ),
                ('szTip'            , wintypes.WCHAR * 128), # after win2000
                ('dwState'          , wintypes.DWORD      ),
                ('dwStateMask'      , wintypes.DWORD      ),
                ('szInfo'           , wintypes.WCHAR * 256),
                ('union'            , _tmp_union          ),
                ('szInfoTitle'      , wintypes.WCHAR * 64 ),
                ('dwInfoFlags'      , wintypes.DWORD      ),
                ('guidItem'         , GUID                ),
                ('hBalloonIcon'     , wintypes.HICON      )]
    
    def __init__(self):
        super().__init__()
        self.cbSize = sizeof(self) # This always needs to be done before using the structure
    
    
class WNDCLASSEX(ctypes.Structure):
    '''
    WinApi class. Used for a notification icon.
    NOTE: This intended for use with W functions (unicode api)
    '''
    
    _fields_ = [("cbSize"       , wintypes.UINT     ),
                ("style"        , wintypes.UINT     ),
                ("lpfnWndProc"  , WNDPROC           ),
                ("cbWndExtra"   , ctypes.c_int      ),
                ("cbClsExtra"   , ctypes.c_int      ),
                ("hInstance"    , wintypes.HINSTANCE),
                ("hIcon"        , wintypes.HICON    ),
                ("hCursor"      , wintypes.HICON    ),
                ("hbrBackground", wintypes.HBRUSH   ),
                ("lpszMenuName" , wintypes.LPCWSTR  ),
                ("lpszClassName", wintypes.LPCWSTR  ),
                ("hIconSm"      , wintypes.HICON    )]
    
    def __init__(self):
        super().__init__()
        self.cbSize = sizeof(self) # This always needs to be done before using the structure
    
    