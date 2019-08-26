'''
Sample usage of ReadProcessMemory/WriteProcessMemory

Author: Eli Finkel - eyfinkel@gmail.com
'''

from ctypes import *
lastErr = windll.kernel32.GetLastError
OpenProcess = windll.kernel32.OpenProcess
OpenProcess.restype = c_void_p
PROCESS_ALL_ACCESS=0x1F0FFF
readMem=windll.kernel32.ReadProcessMemory
readMem.argtypes=[c_void_p,c_void_p,c_void_p,c_size_t,c_void_p]
writeMem=windll.kernel32.WriteProcessMemory
writeMem.argtypes=[c_void_p,c_void_p,c_void_p,c_size_t,c_void_p]

# read example
pid = <pid>
addrInProc = <addr>
bufLen = 10

buf = (c_ubyte*bufLen)();bufWritten = c_size_t()
p,err=OpenProcess(PROCESS_ALL_ACCESS, 0, pid),lastErr()
ret,err=readMem(p, addrInProc, buf, len(buf), byref(bufWritten)),lastErr()
[hex(x) for x in buf]

# write example
data = b'abc'
ret,err=writeMem(p, addrInProc, data, len(data), byref(bufWritten)),lastErr()
