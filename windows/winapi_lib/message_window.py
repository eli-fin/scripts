'''
Author: Eli Finkel - eyfinkel@gmail.com
'''

import ctypes
from ctypes import wintypes, windll, c_int, c_voidp, c_wchar, byref, sizeof
from winapi_lib.winapi_structs import WNDCLASSEX, WNDPROC

class MessageWindow():
    '''
    A Win32 message only window which can be used for constructs that require a window
    for message processing (hotkeys, notification icons, context menus, etc.)
    -
    the hWnd attribute is the window handle
    '''
    
    # WinApi defines
    HWND_MESSAGE       = -3
    WM_QUIT            = 0x12
    
    # Used function defs
    __GetLastError              = windll.kernel32.GetLastError
    __RegisterClassExW          = windll.user32.RegisterClassExW
    __UnregisterClassW          = windll.user32.UnregisterClassW
    __UnregisterClassW.argtypes = [c_voidp, c_voidp]
    __CreateWindowExW           = windll.user32.CreateWindowExW
    __DestroyWindow             = windll.user32.DestroyWindow
    __DefWindowProcW            = windll.user32.DefWindowProcW
    __DefWindowProcW.argtypes   = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
    __GetMessageW               = windll.user32.GetMessageW
    __DispatchMessageW          = windll.user32.DispatchMessageW
    __DispatchMessageW.argtypes = [c_voidp]

    
    __class_counter = 0 # A class counter, so every message window has a different class name
    
    def __init__(self, WndProc):
        '''
        param WndProc:  The Window Procedure callback that will handle the window messages.
                        This usually looks something like this:
                        
                        def WndProc(hWnd, uMsg, wParam, lParam):
                            if uMsg == SOMETHING_I_HADLE:
                                if EXIT_FLAG (depending on the setup):
                                    windll.user32.PostQuitMessage(exit_code) # This is to end the message loop
                                else:
                                    handle()
                                return 1 # handled
                        
                            else: # Return the default handler
                                return windll.user32.DefWindowProcW(hWnd, uMsg, wParam, lParam)
        '''
        
        self.__win_class = WNDCLASSEX()
        self.__win_class.lpfnWndProc = WNDPROC(WndProc)
        self.__win_class.lpszClassName = "my_msg_win"+str(MessageWindow.__class_counter)
        MessageWindow.__class_counter+=1
        
        ret, err = self.__RegisterClassExW(byref(self.__win_class)), self.__GetLastError()
        if ret == 0:
            raise ctypes.WinError(err)
        self.hWnd, err = self.__CreateWindowExW(None, self.__win_class.lpszClassName, None, None, None, None, None, None, self.HWND_MESSAGE, None, None, None),\
                         self.__GetLastError()
        if self.hWnd == 0:
            raise ctypes.WinError(err)
        
    def __del__(self):
        ret, err = self.__DestroyWindow(self.hWnd), self.__GetLastError()
        if ret == 0:
            raise ctypes.WinError(err)
        ret, err = self.__UnregisterClassW(self.__win_class.lpszClassName, None), self.__GetLastError()
        if ret == 0:
            raise ctypes.WinError(err)
    
    def loop(self):
        '''
        Run the message loop
        '''
        msg = wintypes.MSG()
        while True:
            ret = self.__GetMessageW(byref(msg), self.hWnd, 0, 0)
            if ret == 0: # Error or WM_QUIT
                break
            if ret > 0:
                if msg.message == self.WM_QUIT:
                    break
                self.__DispatchMessageW(byref(msg)) # Send to WndProc
            elif ret < 0: # Some other error
                raise Exception('Error in message loop of window '+self.__win_class.lpszClassName)
    
        
    