'''
Get/Set monitor brightness
(doesn't work on all monitors, usually won't work on laptop monitors)
This will act on the monitor on which this window is

Usage: <script> [new percentage]

Author: Eli Finkel - eyfinkel@gmail.com
'''

from ctypes import windll, c_ulong, byref, WinError
from monitorLib import monitorLib
from sys import argv
from os import system
from traceback import print_exc

GetBright        = windll.dxva2.GetMonitorBrightness
SetBright        = windll.dxva2.SetMonitorBrightness
GetConsoleWindow = windll.kernel32.GetConsoleWindow
GetLastError     = windll.kernel32.GetLastError

# Get window hanlde
win_hwnd = GetConsoleWindow()

def get_brightness():
    """
    Return the minimum, current and maximum brightness of the monitor which the console window is on
    """
    HMon = monitorLib.get_handle(win_hwnd)
    physHMon, physMonInfoArr, physMonArrSize = monitorLib.get_physical_handle(HMon)
    minBright, curBright, maxBright = c_ulong(), c_ulong(), c_ulong()
    ret,err = GetBright(physHMon, byref(minBright), byref(curBright), byref(maxBright)), GetLastError()
    if not ret:
        raise WindowsError('Failed to get brightness', WinError(err))
    monitorLib.destroy_handle(physMonInfoArr, physMonArrSize)
    return minBright, curBright, maxBright
    
def set_brightness(new_val):
    """
    Sets brightness of the monitor which the console window is on
    Values can be 0-100
    """
    HMon = monitorLib.get_handle(win_hwnd)
    physHMon, physMonInfoArr, physMonArrSize = monitorLib.get_physical_handle(HMon)
    ret,err = SetBright(physHMon, new_val), GetLastError()
    if not ret:
        raise WindowsError('Failed to set brightness', WinError(err))
    monitorLib.destroy_handle(physMonInfoArr, physMonArrSize)


def wmi_get_brightness():
    """
    Print the current brightness of the monitor (won't behave if multiple monitors support WMI brightness)
    """
    cmd = r'wmic /NAMESPACE:\\root\wmi PATH WmiMonitorBrightness GET CurrentBrightness'
    system(cmd)
    # expected output: 'CurrentBrightness  \n\n100                 \n\n\n\n'
    #level = popen(cmd).read().strip().splitlines()[-1]
    #return int(level)


def wmi_set_brightness(new_val):
    """
    Sets brightness of the monitor (won't behave if multiple monitors support WMI brightness)
    Values can be 0-100 (might be different for other monitors, haven't really tested)
    """
    cmd = r'wmic /NAMESPACE:\\root\wmi PATH WmiMonitorBrightnessMethods WHERE "Active=TRUE" '\
           'CALL WmiSetBrightness Brightness='+str(new_val)+' Timeout=0'
    system(cmd)


if __name__ == '__main__':
    def do():
        # Print current brighness
        print('Current brightness is: ' + str(get_func()))
        # Try to set brightness
        if len(argv) >=2 and argv[1].isdigit():
            set_func(int(argv[1]))
            print('Brightness set to ' + argv[1])

    try:
        get_func=lambda:get_brightness()[1]
        set_func=set_brightness
        do()
    except WindowsError:
        print_exc()
        print('Error using WINAPI, falling back on WMI')
        get_func=wmi_get_brightness
        set_func=wmi_set_brightness
        do()
