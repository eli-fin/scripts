'''
register and unregister function for winapi hot keys
the modifier codes are also defined here

Author: Eli Finkel - eyfinkel@gmail.com
'''

import ctypes
from ctypes import windll

# WinApi defines
MOD_ALT          = 0x0001
MOD_CONTROL      = 0x0002
MOD_SHIFT        = 0x0004
MOD_WIN          = 0x0008

# Used function defs
_GetLastError        = windll.kernel32.GetLastError
_RegisterHotKey      = windll.user32.RegisterHotKey
_UnregisterHotKey    = windll.user32.UnregisterHotKey

def register(hWnd, id, mod, virtual_key):
    '''
    Register a hotkey
    -
    param hWnd:         the window to which the hotkey messages will be posted to.
                        (this can be 0, if you intend to process the messages in a message loop yourself
                         from the current thread)
    param id:           an id for this specific hotkey. needed for removal
    param mod:          the virtual key modifier
    param virtual_key:  the virtual key
    '''
    ret, err = _RegisterHotKey(hWnd, id, mod, virtual_key), _GetLastError()
    if ret == 0:
        raise ctypes.WinError(err)
    
def unregister(hWnd, id):
    '''
    Unregister a hotkey
    -
    param hWnd: the window
    param id:   the id
    '''
    ret, err = _UnregisterHotKey(hWnd, id), _GetLastError()
    if ret == 0:
        raise ctypes.WinError(err)
    
