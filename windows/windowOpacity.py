'''
 This script changes the opacity of any window
 USAGE:
   Start the script with cursor located on the window you want to change
   and pass new opacity percentage <0-100> as first argument
   NOTE: If you set opacity to 0, window will be completely hidden
         and you will not be able to restore it using this script
         
Author: Eli Finkel - eyfinkel@gmail.com
'''

import sys
from ctypes import windll, byref, wintypes, create_string_buffer

# WinAPI defines
GWL_EXSTYLE   = -20
LWA_ALPHA     =  2
GA_ROOT       =  2
WS_EX_LAYERED =  0x00080000

def getWindowText(hwnd):
    ''' Return a string of the window title '''
    
    str = create_string_buffer(1000) # 1000 Should be long enough
    windll.user32.GetWindowTextA(hwnd, str, 1000)
    return str.value.decode('utf-8','ignore')

def setWindowOpacity(hwnd, percentage):
    ''' Set the window opacity to the percentage passed '''
    
    curLong = windll.user32.GetWindowLongA(hwnd, GWL_EXSTYLE)
    
    print('Current window long: {0}'.format(curLong))
    
    if not windll.user32.SetWindowLongA(hwnd, GWL_EXSTYLE, curLong | WS_EX_LAYERED):
        print('Can\'t modify this window.\n'
              'Maybe it belongs to an admin process and you arent\'nt admin?')
        exit(1)
    
    if not windll.user32.SetLayeredWindowAttributes(
        hwnd,
        0, # Not relevant
        int(255*(percentage/100.0)),
        LWA_ALPHA):
        print('Changing window opacity failed for some reason')
        exit(1)

def getWindowFromCursorPos():
    ''' Returns the handle of the top window where the cursor
        is currently located '''
    
    # Get current Cursor position
    point = wintypes.POINT()
    windll.user32.GetCursorPos(byref(point))
    print('Found Cursor location (x={0},y={1})'.format(point.x, point.y))
    
    # Get window handle from Cursor position
    hwnd = windll.user32.WindowFromPoint(point)
    print('Found window {0} ({1})'.format(hwnd, getWindowText(hwnd)))
    
    # The hwnd returned could be that of a button or any other sub-element
    # So get the top window of that element
    # (This should work with windows that aren't visually located under
    #  their parent)
    topHwnd = windll.user32.GetAncestor(hwnd, GA_ROOT)
    print('Found top window {0} ({1})'.format(topHwnd, getWindowText(topHwnd)))
    return topHwnd

def main():
    try:
        percentage = int(sys.argv[1])
        print('New percentage passed: {0}'.format(percentage))
        if not 0 <= percentage <= 100:
            print('New percentag must be 0 <= percentage <= 100')
            exit(1)
        hwnd = getWindowFromCursorPos()
        setWindowOpacity(hwnd, percentage)
        print('Set successfully')
    except IndexError:
        print('ERROR: You must pass a new percentage value')
    except ValueError:
        print('ERROR: New percentage value must be an integer')
    
if __name__ == '__main__':
    print('Window opacity setter (see file comment for more)')
    main()
    