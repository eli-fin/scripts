'''
A wrapper class to get a physical monitor handle  

Author: Eli Finkel - eyfinkel@gmail.com
'''

from ctypes import windll, Structure, c_void_p, c_wchar, c_ulong, byref

class monitorLib():
    """
    This class can be used to get and destroy a physical monitor handle
    """
    
    # note: all operations with physical hmonitors must be performed
    #       after getting them through the api in this session
    #       (you cannot use a handle from a previous excecution)

    # Functions
    NumOfPhysMonFromH = windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR
    PhysMonFromH = windll.dxva2.GetPhysicalMonitorsFromHMONITOR
    DestPhysMon = windll.dxva2.DestroyPhysicalMonitors
    MonFromWin = windll.user32.MonitorFromWindow

    # Defines 
    PHYSICAL_MONITOR_DESCRIPTION_SIZE = 128
    MONITOR_DEFAULTTONULL = 0x0

    @classmethod
    def get_handle(cls, win_hwnd):
        """
        Returns a physical monitor handle (not HMONITOR) for the monitor which win_hwnd is on
        IMPORTANT: After using the handle, you must return in by calling destroy_handle
        Returns a tupple of the physical handle, physical monitor array and array size
        """
        
        class PHYSICAL_MONITOR(Structure):
            """
            Physical monitor struct for GetPhysicalMonitorsFromHMONITOR
            """
            _fields_ =\
                [('hPhysicalMonitor', c_void_p),
                ('szPhysicalMonitorDescription',
                c_wchar * cls.PHYSICAL_MONITOR_DESCRIPTION_SIZE)]
            
        print('Getting physical handle for window ' + str(win_hwnd))
        
        HMon = cls.MonFromWin(win_hwnd, cls.MONITOR_DEFAULTTONULL)
        if HMon == 0:
            raise WindowsError('Failed to get HMONITOR')
        print('Got the following HMONITOR ' + str(HMon))
        physMonArrSize = c_ulong()
        # get size of physical monitor array for an hMonitor
        if not cls.NumOfPhysMonFromH(HMon, byref(physMonArrSize)):
            raise WindowsError('Failed to get number of monitors')
        # define an array by that size (first create a class of the array, then an instance)
        physMonInfoArr = (PHYSICAL_MONITOR * physMonArrSize.value)()
        # Get monitor info
        if not cls.PhysMonFromH(HMon, physMonArrSize, byref(physMonInfoArr)):
            raise WindowsError('Failed to get handle')
        
        # physical hMon for first physical screen
        physHMon = physMonInfoArr[0].hPhysicalMonitor
        print('Got the following physical handle ' + str(physHMon))
        # return handle, physMon array and arrSize to pass to destroy_handle
        return physHMon, physMonInfoArr, physMonArrSize
        
    @classmethod
    def destroy_handle(cls, physMonInfoArr, physMonArrSize):
        """ Destroy the physical handle """
        print('Destroying the following physical handle ' + str(physMonInfoArr[0].hPhysicalMonitor))
        # destroy physical monitor handle
        if not cls.DestPhysMon(physMonArrSize, byref(physMonInfoArr)):
            raise WindowsError('Failed to destroy handle')
    
