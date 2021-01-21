'''
Switch monitor input source
(doesn't work on all monitors)
This will act on the monitor on which this window is

Usage: <script> new-source-index (Try values 0-15)

Author: Eli Finkel - eyfinkel@gmail.com
'''

from ctypes import windll, c_ulong, byref
from monitorLib import monitorLib
from sys import argv

SetVCPFeature_impl     = windll.dxva2.SetVCPFeature
GetConsoleWindow       = windll.kernel32.GetConsoleWindow

# Get window hanlde
win_hwnd = GetConsoleWindow()

VCP_INPUT_SELECT_CODE = 0x60

def SetVCPFeature(new_source):
    """
    Sets the input source to the new value
    (Try values 0-15)
    """
    HMon = monitorLib.get_handle(win_hwnd)
    physHMon, physMonInfoArr, physMonArrSize = monitorLib.get_physical_handle(HMon)
    if not SetVCPFeature_impl(physHMon, VCP_INPUT_SELECT_CODE, new_source):
        raise WindowsError('Failed to set VCP Feature')
    monitorLib.destroy_handle(physMonInfoArr, physMonArrSize)


if __name__ == '__main__':
    # Try to change source
    try:
        SetVCPFeature(int(argv[1]))
        print('Input source set to ' + argv[1])
    except ValueError: # Not a number
        pass
    except IndexError: # No argument
        pass
