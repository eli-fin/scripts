'''
Author: Eli Finkel - eyfinkel@gmail.com
'''

import ctypes
from ctypes import wintypes, windll, c_voidp, c_wchar, byref, sizeof
from winapi_lib.winapi_structs import GUID, SP_DEVINFO_DATA, SP_PROPCHANGE_PARAMS

class DeviceManager():
    '''
    The class provides some methods to work with installed devices
    through the windows setup api
    '''
    
    # Used function defs
    __GetLastError                          = windll.kernel32.GetLastError
    __GetClassDevsW                         = windll.setupapi.SetupDiGetClassDevsW
    __GetClassDevsW.restype                 = c_voidp
    __GetClassDevsW.argtypes                = [c_voidp, c_voidp, c_voidp, wintypes.DWORD]
    __DestroyDeviceInfoList                 = windll.setupapi.SetupDiDestroyDeviceInfoList
    __DestroyDeviceInfoList.argtypes        = [c_voidp]
    __EnumDeviceInfo                        = windll.setupapi.SetupDiEnumDeviceInfo
    __EnumDeviceInfo.argtypes               = [c_voidp, wintypes.DWORD, c_voidp]
    __GetDeviceRegistryPropertyW            = windll.setupapi.SetupDiGetDeviceRegistryPropertyW
    __GetDeviceRegistryPropertyW.argtypes   = [c_voidp, c_voidp, wintypes.DWORD, c_voidp, c_voidp, wintypes.DWORD, c_voidp]
    __SetClassInstallParamsW                = windll.setupapi.SetupDiSetClassInstallParamsW
    __SetClassInstallParamsW.argtypes       = [c_voidp, c_voidp, c_voidp, wintypes.DWORD]
    __ChangeState                           = windll.setupapi.SetupDiChangeState
    __ChangeState.argtypes                  = [c_voidp, c_voidp]
    
    def __init__(self):
        # Get the HDEVINFO handle
        flags = 0x4 | 0x2 # DIGCF_ALLCLASSES | DIGCF_PRESENT
        self.__devices,err = self.__GetClassDevsW(None, None, None, flags),self.__GetLastError()
        if self.__devices == -1: # INVALID_HANDLE_VALUE (because default ctypes return is signed int)
            raise ctypes.WinError(err)
    
    def __del__(self):
        self.__DestroyDeviceInfoList(self.__devices)
    
    def enumerate(self):
        '''
        This function can be used to enumerate all available devices
        '''
        device = SP_DEVINFO_DATA()
        index = 0
        while (True):
            ret,err = self.__EnumDeviceInfo(self.__devices, index, byref(device)),self.__GetLastError()
            if ret == 1:
                index += 1
                
                # During testing, on a number of windows 10 x64 machines, after the device
                # 'Microsoft ACPI-Compliant System' was enumerated by EnumDeviceInfo, a
                # device with an empty GUID was given, which would make this entry invalid,
                # so this will just skip it
                if device.ClassGuid == GUID.from_string('{00000000-0000-0000-0000-000000000000}'):
                    continue
                yield device.copy()
            else:
                if err == 259: # ERROR_NO_MORE_ITEMS
                    break
                raise ctypes.WinError(err)
    
    def get_device_name(self, device):
        '''
        Get device class name
        NOTE: Those are class names and therefore, not always unique
        '''
        assert type(device) == SP_DEVINFO_DATA, 'other must be a SP_DEVINFO_DATA, not '+str(type(device).__name__)
        buf = (c_wchar*1000)()
        ret,err = \
            self.__GetDeviceRegistryPropertyW(self.__devices, byref(device), 0x0,  #SPDRP_DEVICEDESC
                                              None, byref(buf), sizeof(buf), None), \
            self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
        return buf.value
    
    def enable_device(self, device):
        '''
        Enable a device (requires admin)
        '''
        assert type(device) == SP_DEVINFO_DATA, 'other must be a SP_DEVINFO_DATA, not '+str(type(device).__name__)
        params = SP_PROPCHANGE_PARAMS()
        params.ClassInstallHeader.InstallFunction = 0x12 # DIF_PROPERTYCHANGE
        params.StateChange = 0x1 # DICS_ENABLE
        params.Scope = 0x1 # DICS_FLAG_GLOBAL;
        params.HwProfile = 0 # current hw profile
        
        ret, err = self.__SetClassInstallParamsW(self.__devices, byref(device), byref(params), sizeof(params)), \
                self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
        ret, err = self.__ChangeState(self.__devices, byref(device)),self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
    
    def disable_device(self, device):
        '''
        Disable a device (requires admin)
        '''
        assert type(device) == SP_DEVINFO_DATA, 'other must be a SP_DEVINFO_DATA, not '+str(type(device).__name__)
        params = SP_PROPCHANGE_PARAMS()
        params.ClassInstallHeader.InstallFunction = 0x12 # DIF_PROPERTYCHANGE
        params.StateChange = 0x2 # DICS_DISABLE
        params.Scope = 0x1 # DICS_FLAG_GLOBAL;
        params.HwProfile = 0 # current hw profile
        
        ret, err = self.__SetClassInstallParamsW(self.__devices, byref(device), byref(params), sizeof(params)), \
                   self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
        ret, err = self.__ChangeState(self.__devices, byref(device)),self.__GetLastError()
        if ret != 1:
            raise ctypes.WinError(err)
    
    