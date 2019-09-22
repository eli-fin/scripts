'''
When running this, press CRRL+F1 to keep the foreground windows on top at all times (press again to undo)
You'll also get an icon in the taskbar, which you can use to exit.

Author: Eli Finkel - eyfinkel@gmail.com
'''

import os
from winapi_lib.message_window import MessageWindow
from winapi_lib.notify_icon import NotifyIcon
from winapi_lib.context_menu import ContextMenu
from winapi_lib import hotkey
from ctypes import windll, c_wchar, byref

# WinApi defines
GWL_EXSTYLE        = (-20)
WS_EX_TOPMOST      = 0x0008
HWND_TOPMOST       = (-1)
HWND_NOTOPMOST     = (-2)
SWP_NOSIZE         = 0x0001
SWP_NOMOVE         = 0x0002
WM_RBUTTONDOWN     = 0x204
WM_CONTEXTMENU     = 0x7b
WM_HOTKEY          = 0x0312
VK_F1              = 0x70

my_app_notifyicon_msg = 0x8000+1 # WM_APP+1
my_icon_path = os.path.dirname(os.path.realpath(__file__)) + '/_icons/topmost.ico' # Relative to script dir
my_icon_tip = f'CTRL+F1 to change window state'
TITLE_BUFFER_SIZE = 1000
icon = None
menu = None

# This function will be called when the hotkey is pressed
# It will handle setting or unsetting a window as topmost
def HandleWindowTopMostState():
    # Get current active window
    currWin = windll.user32.GetForegroundWindow()
    
    # Get window title
    winTitle = (c_wchar*TITLE_BUFFER_SIZE)()
    windll.user32.GetWindowTextW(currWin, byref(winTitle), TITLE_BUFFER_SIZE)
    
    # If currently not top most
    if (windll.user32.GetWindowLongW(currWin, GWL_EXSTYLE) & WS_EX_TOPMOST) == 0:
        # Set as topmost
        windll.user32.SetWindowPos(currWin, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
        icon.popup(winTitle.value, 'Made topmost')
    else:
        windll.user32.SetWindowPos(currWin, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
        icon.popup(winTitle.value, 'Made not topmost')
    
def WndProc(hWnd, uMsg, wParam, lParam):
    try:
        if uMsg == WM_HOTKEY:
            HandleWindowTopMostState()
            return 1 # handled
        
        # Notifyicon message
        elif uMsg == my_app_notifyicon_msg:
            # Both messages will open context menu
            if (lParam == WM_RBUTTONDOWN) or (lParam == WM_CONTEXTMENU):
                menu.show(hWnd)
                return 1 # handled
    except:
        windll.user32.PostQuitMessage(1)
        raise
    
    return windll.user32.DefWindowProcW(hWnd, uMsg, wParam, lParam)
    
def main():
    global icon, menu
    
    window = MessageWindow(WndProc)
    icon = NotifyIcon(my_icon_path, window.hWnd, 0, my_app_notifyicon_msg, my_icon_tip, 'Starting', 'TopMost setter')
    menu = ContextMenu()        
    menu.add_item('About', lambda:windll.user32.MessageBoxW(0, 'About me :-)', 'Top Most', 0))
    menu.add_item('Exit' , lambda:windll.user32.PostQuitMessage(0))
    
    hotkey.register(window.hWnd, 0, hotkey.MOD_CONTROL, VK_F1)
    
    window.loop()
    
    hotkey.unregister(window.hWnd, 0)
    del menu
    del icon
    del window
    

if __name__ == '__main__':
    main()
    