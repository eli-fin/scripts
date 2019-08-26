'''
Use this to start a process and immediately suspend it, then a popup will show, once you hit OK, the process will resume.
(useful if you want to debug/analyze something happening early in the process lifetime)

Usage: <script> <executable> args...

Author: Eli Finkel - eyfinkel@gmail.com
'''
# Start a process with args passed suspended and resume when user is ready


import ctypes
import time
from ctypes import wintypes
import sys

# winapi types needed
class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute",wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", wintypes.LPBYTE),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]

def main():
    # according to msdn, you can pass NULL for exe name and pass it as first arg
    cmd = ' '.join(sys.argv[1:]) # Pass exe+args in command line
    # create a buffer, because docs say it needs to be editable
    cmd = ctypes.create_unicode_buffer(cmd)
    
    start_info = STARTUPINFOW()
    proc_info = PROCESS_INFORMATION()
    proc_creation_flags = 0x4 # CREATE_SUSPENDED
    
    ret = ctypes.windll.kernel32.CreateProcessW(
        None, cmd, None, None, 0, proc_creation_flags, None,
        None, ctypes.byref(start_info), ctypes.byref(proc_info))
    print(f'Created process: "{cmd.value}", returned {ret}')
    
    ctypes.windll.user32.MessageBoxW(
        None, f'Process started suspended (pid={proc_info.dwProcessId}).\nClose box to resume',
        'Start Suspended...', 0x00001000) # topmost
    
    ret = ctypes.windll.kernel32.ResumeThread(proc_info.hThread)
    print(f'Resumed process: returned {ret}')
    
    ret = ctypes.windll.kernel32.WaitForSingleObject(proc_info.hProcess, 0xffffffff) # Wait for process exit infinitely
    print(f'Process WaitForSingleObject returned: {ret}')
    
if __name__ == '__main__':
    main()
    