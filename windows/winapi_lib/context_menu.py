'''
Author: Eli Finkel - eyfinkel@gmail.com
'''

import ctypes
from ctypes import windll, wintypes, byref
from types import FunctionType

class ContextMenu():
    '''
    This class can be used to create and show a popup (context) menu
    Create an instance, add items and show it.
    Note: You must have an existing window in your process to be the parent of this
    '''
    
    # WinApi defines
    MF_BYPOSITION      = 0x400
    MF_STRING          = 0x0
    TPM_BOTTOMALIGN    = 0x20
    TPM_LEFTALIGN      = 0x0
    TPM_NONOTIFY       = 0x80
    TPM_RETURNCMD      = 0x100
    
    # Used function defs
    __GetLastError               = windll.kernel32.GetLastError
    __CreatePopupMenu            = windll.user32.CreatePopupMenu
    __DestroyMenu                = windll.user32.DestroyMenu
    __InsertMenuW                = windll.user32.InsertMenuW
    __TrackPopupMenu             = windll.user32.TrackPopupMenu
    __GetCursorPos               = windll.user32.GetCursorPos
    __SetForegroundWindow        = windll.user32.SetForegroundWindow
    
    
    def __init__(self):
        self.__menu, err = self.__CreatePopupMenu(), self.__GetLastError()
        if self.__menu == 0:
            raise ctypes.WinError(err)
        self.__item_index = 1
        self.__callbacks = {}
        
    def __del__(self):
        ret, err = self.__DestroyMenu(self.__menu), self.__GetLastError()
        if ret == 0:
            raise ctypes.WinError(err)
        
    def add_item(self, text, callback):
        '''
        Add an item to the menu. Items get added in order.
        -
        param text:     the text to display for this item
        param callback: the function to call (with no args), if this item is selected
        '''
        
        assert type(text)      == str,          'text must be an str, not '+str(type(text).__name__)
        assert type(callback)  == FunctionType, 'callback must be a FunctionType, not '+str(type(callback).__name__)
        
        ret, err = self.__InsertMenuW(self.__menu, self.__item_index, self.MF_BYPOSITION | self.MF_STRING, self.__item_index, text), \
                   self.__GetLastError()
        if ret == 0:
            raise ctypes.WinError(err)
        self.__callbacks[self.__item_index] = callback
        self.__item_index+=1
        
    def show(self, hWnd, x=None, y=None):
        '''
        Show the menu.
        This will block until an item is selected or the menu looses focus and closes.
        -
        param hWnd: the window which will be the parent of this menu
        param x/y:  location for showing the menu. If None, current mouse position will be used
        '''
        
        assert type(hWnd)   == int, 'hWnd must be an int, not '+str(type(hWnd).__name__)
        
        if None in (x,y):
            p = wintypes.POINT()
            ret, err = self.__GetCursorPos(byref(p)), self.__GetLastError()
            if ret == 0:
                raise ctypes.WinError(err)
            x,y = p.x, p.y
        
        self.__SetForegroundWindow(hWnd) # No error check. This failes sometimes, but it's not really a failure
                                         # and it's normal
        # ret will be the selected item, or 0 if nothing was selected.
        # If there's an error, 0 is returned, so there's no way of knowing if there was an error
        # or if the menu was just dismissed, so no error checking is done
        ret = self.__TrackPopupMenu(self.__menu, self.TPM_BOTTOMALIGN | self.TPM_LEFTALIGN | self.TPM_NONOTIFY | self.TPM_RETURNCMD, x, y, 0, hWnd, 0)
        
        if ret > 0:
            self.__callbacks[ret]()
        
    