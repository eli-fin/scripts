'''
Get/Set monitor brightness
(doesn't work on all monitors, usually won't work on laptop monitors)
This will act on the monitor on which this window is

Usage: <script> [new percentage]

Author: Eli Finkel - eyfinkel@gmail.com
'''

from ctypes import windll, c_ulong, byref
from monitorLib import monitorLib
from sys import argv

GetBright        = windll.dxva2.GetMonitorBrightness
SetBright        = windll.dxva2.SetMonitorBrightness
GetConsoleWindow = windll.kernel32.GetConsoleWindow

# Get window hanlde
win_hwnd = GetConsoleWindow()

def get_brightness():
    """
    Return the minimum, current and maximum brightness of the monitor which the console window is on
    """
    physHMon, physMonInfoArr, physMonArrSize = monitorLib.get_handle(win_hwnd)
    minBright, curBright, maxBright = c_ulong(), c_ulong(), c_ulong()
    if not GetBright(physHMon, byref(minBright), byref(curBright), byref(maxBright)):
        raise WindowsError('Failed to get brightness')
    monitorLib.destroy_handle(physMonInfoArr, physMonArrSize)
    return minBright, curBright, maxBright
    
def set_brightness(new_val):
    """
    Sets brightness  of the monitor which the console window is on
    Values can be 0-100
    """
    physHMon, physMonInfoArr, physMonArrSize = monitorLib.get_handle(win_hwnd)
    if not SetBright(physHMon, new_val):
        raise WindowsError('Failed to set brightness')
    monitorLib.destroy_handle(physMonInfoArr, physMonArrSize)


if __name__ == '__main__':
    # Print current brighness
    print('Current brightness is: ' + str(get_brightness()[1]))
    # Try to set brightness
    try:
        set_brightness(int(argv[1]))
        print('Brightness set to ' + argv[1])
    except ValueError: # Not a number
        pass
    except IndexError: # No argument
        pass
