'''
Author: Eli Finkel - eyfinkel@gmail.com
'''

import ctypes
from ctypes import wintypes, windll, c_int, c_voidp, c_wchar, byref, sizeof
from winapi_lib.winapi_structs import NOTIFYICONDATA

class NotifyIcon():
    '''
    The class can be used to create a taskbar notification icon
    '''
    
    # WinApi defines
    IMAGE_ICON         = 1
    LR_LOADFROMFILE    = 0x10
    NIF_ICON           = 0x2
    NIF_TIP            = 0x4
    NIF_INFO           = 0x10
    NIF_MESSAGE        = 0x1
    NIF_REALTIME       = 0x40
    NOTIFYICON_VERSION = 3
    NIIF_INFO          = 0x1
    NIM_ADD            = 0x0
    NIM_SETVERSION     = 0x4
    NIM_MODIFY         = 0x1
    NIM_DELETE         = 0x2

    # Used function defs
    __GetLastError                          = windll.kernel32.GetLastError
    __LoadImageW                            = windll.user32.LoadImageW
    __LoadImageW.argtypes                   = [c_voidp, c_voidp, wintypes.UINT, c_int, c_int, wintypes.UINT]
    __LoadImageW.restype                    = c_voidp
    __DestroyIcon                           = windll.user32.DestroyIcon
    __DestroyIcon.argtypes                  = [c_voidp]
    __Shell_NotifyIconW                     = windll.Shell32.Shell_NotifyIconW
    __Shell_NotifyIconW.argtypes            = [wintypes.DWORD, c_voidp]
    
    
    
    def __init__(self, icon_path, hWnd, id, callback_id, tip, popup_info, popup_title):
        '''
        param icon_path:    a path to a valid 32x32 ico file to be used as an icon
        param hWnd:         the window that will receive the notifications
        param id:           a user defined id for this notification icon (to allow more than one per window)
        param callback_id:  a user defined id which is passed to the WndProc of the associated window
                            (this should be > WM_APP(0x8000))
        param tip:          the tooltip text to be displayed for the notification icon
        param popup_info:   the text to show on the popup
        param popup_title:  the title of the popup
        '''
        assert type(icon_path)   == str, 'icon_path must be an str, not '+str(type(icon_path).__name__)
        assert type(hWnd)        == int, 'hWnd must be an int, not '+str(type(hWnd).__name__)
        assert type(id)          == int, 'id must be an int, not '+str(type(id).__name__)
        assert type(callback_id) == int, 'callback_id must be an int, not '+str(type(callback_id).__name__)
        assert type(tip)         == str, 'tip must be an str, not '+str(type(tip).__name__)
        assert type(popup_info)  == str, 'popup_info must be an str, not '+str(type(popup_info).__name__)
        assert type(popup_title) == str, 'popup_title must be an str, not '+str(type(popup_title).__name__)

        # Get icon
        hIcon,err = self.__LoadImageW(None, icon_path, self.IMAGE_ICON, 32, 32, self.LR_LOADFROMFILE),self.__GetLastError()
        if hIcon == None:
            raise ctypes.WinError(err)
        
        self.__ni_data = NOTIFYICONDATA()
        # Populate ni fields
        self.__ni_data.hWnd = hWnd
        self.__ni_data.uID = id
        self.__ni_data.uFlags = self.NIF_ICON | self.NIF_TIP | self.NIF_INFO | self.NIF_MESSAGE | self.NIF_REALTIME
        self.__ni_data.uCallbackMessage = callback_id
        self.__ni_data.hIcon = hIcon
        self.__ni_data.szTip = tip
        self.__ni_data.szInfo = popup_info
        self.__ni_data.uVersion = self.NOTIFYICON_VERSION;
        self.__ni_data.szInfoTitle = popup_title
        self.__ni_data.dwInfoFlags = self.NIIF_INFO;
    
        # Add field to tray
        ret, err = self.__Shell_NotifyIconW(self.NIM_ADD, byref(self.__ni_data)),self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
        ret, err = self.__Shell_NotifyIconW(self.NIM_SETVERSION, byref(self.__ni_data)),self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
    
    def __del__(self):
        # delete the notification icon
        ret, err = self.__Shell_NotifyIconW(self.NIM_DELETE, byref(self.__ni_data)),self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
        # destroy the icon
        ret, err = self.__DestroyIcon(self.__ni_data.hIcon),self.__GetLastError()
        if ret == 0:
            raise ctypes.WinError(err)
        
    def popup(self, popup_info, popup_title):
        '''
        Show a popup
        -
        param popup_info:   the text to show on the popup
        param popup_title:  the title of the popup
        '''
        assert type(popup_info)  == str, 'popup_info must be an str, not '+str(type(popup_info).__name__)
        assert type(popup_title) == str, 'popup_title must be an str, not '+str(type(popup_title).__name__)
        
        self.__ni_data.szInfo = popup_info
        self.__ni_data.szInfoTitle = popup_title

        ret, err = self.__Shell_NotifyIconW(self.NIM_MODIFY, byref(self.__ni_data)),self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
    
    def update_icon(self, icon_path):
        '''
        param icon_path:    a path to a valid 32x32 ico file to be used as an icon
        '''
        assert type(icon_path)   == str, 'icon_path must be an str, not '+str(type(icon_path).__name__)
        
        # Get icon
        hIcon,err = self.__LoadImageW(None, icon_path, self.IMAGE_ICON, 32, 32, self.LR_LOADFROMFILE),self.__GetLastError()
        if hIcon == None:
            raise ctypes.WinError(err)
        
        old_hIcon = self.__ni_data.hIcon
        self.__ni_data.hIcon = hIcon
        
        ret, err = self.__Shell_NotifyIconW(self.NIM_MODIFY, byref(self.__ni_data)),self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
        
        # destroy the icon
        ret, err = self.__DestroyIcon(old_hIcon),self.__GetLastError()
        if ret == 0:
            raise ctypes.WinError(err)
