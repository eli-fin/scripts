'''
 This script will allow you to start multiple instances of the windows task manager

 The task manager uses CreateMutex to check if an instance has been started.
 If it has, the process will close.

 We can find that mutex, duplicate it to our process (and close the original during the duplication),
 then we can close the mutex handle we got.
 That way, the new instance won't know that an instance was already started and will start normally
 
 The mutex seems to always be as following:
    \Sessions\1\BaseNamedObjects\TASKMGR.879e4d63-6c0e-4544-97f2-1244bd3f6de0 in Win7
    \Sessions\1\BaseNamedObjects\TM.750ce7b0-e5fd-454f-9fad-2f66513dfa1b in Win10
    ('process explorer' and 'handle' can be used to find this)
 The 'handle' tool is expected to be available in your path to find the mutex handle dynamically
 
 Admin privileges are required to close handles of other processes
 
 Tested on windows7x64, Windows10x64.
 
 Have fun!
 
 Author: Eli Finkel - eyfinkel@gmail.com
'''

import subprocess
import os
import platform
from ctypes import *

# This function expects a retcode and function name
# If retcode zero, a messagebox with GetLastError() value and funcName will be shown
# and exit(1) will be called.
def WINAPI_RETCODE_CHECK(ret, funcName):
    if ret == 0:
        err = windll.kernel32.GetLastError()
        msg = 'WINAPI Error: func:' + funcName + ', error:' + str(err)
        windll.user32.MessageBoxW(None, msg, 'Error', None)
        exit(1)


# WINAPI Cosnts
PROCESS_DUP_HANDLE = 0x0040
DUPLICATE_CLOSE_SOURCE = 0x1


# Check for admin rights
retcode = os.system('net session > nul 2>&1')
if retcode != 0:
    windll.user32.MessageBoxW(None, 'You are not an admin', 'Error', None)
    exit(1)

# find pid of most recently opened taskmanager
try:
    tskMgrPid = subprocess.Popen(
            'tasklist /FI "IMAGENAME eq TASKMGR.EXE" 2>&1',
            stdout=subprocess.PIPE,
            shell=True)\
        .stdout.readlines()[-1].split()[1]
    tskMgrPid = int(tskMgrPid)
except ValueError:
    # Nothing yet, open a new one
    os.system('start taskmgr')
    exit(0)

# Find the mutex handle
# This requires sysinternals handle tool to be in your path
# Check if handle is available
handlePath = subprocess.Popen(
        'where handle.exe 2>nul',
        stdout=subprocess.PIPE,
        shell=True)\
    .stdout.read().strip()
if len(handlePath) == 0:
    windll.user32.MessageBoxW(
        None,
        'Can\'t find SysInternals \'handle\' tool',
        'Error',
        None)
    exit(1)
else:
    try:
        if platform.platform().startswith('Windows-7'):
            mtxHandle = int(subprocess.Popen(
                    'handle /accepteula -a -p ' + str(tskMgrPid) + ' 2>&1 | findstr TASKMGR.',
                    stdout=subprocess.PIPE,
                    shell=True)\
                .stdout.read().decode().split(':')[0], 16)
        elif platform.platform().startswith('Windows-10'):
            mtxHandle = int(subprocess.Popen(
                    'handle /accepteula -a -p ' + str(tskMgrPid) + ' 2>&1 | findstr TM.',
                    stdout=subprocess.PIPE,
                    shell=True)\
                .stdout.read().decode().split(':')[0], 16)
        else:
            raise Exception('Unknown platform. Never tested')
    except Exception as e: # error
        raise Exception('Can\'t get TaskManager mutex handle - ' + str(e))
    
# Get my process pid 
myPid = windll.kernel32.GetCurrentProcessId()
WINAPI_RETCODE_CHECK(myPid, 'GetCurrentProcessId')

# Get process handles for the task manager and for the current process
taskMgrProc = windll.kernel32.OpenProcess(
    PROCESS_DUP_HANDLE,
    False,
    tskMgrPid)
WINAPI_RETCODE_CHECK(taskMgrProc, 'OpenProcess')

currProc = windll.kernel32.OpenProcess(
    PROCESS_DUP_HANDLE,
    False,
    myPid)
WINAPI_RETCODE_CHECK(currProc, 'OpenProcess')

# Define a handle for the mutex
myMtxHandle = c_void_p()

# Duplicate the handle
retcode = windll.kernel32.DuplicateHandle(
    taskMgrProc,
    mtxHandle,
    currProc,
    byref(myMtxHandle),
    PROCESS_DUP_HANDLE,
    False,
    DUPLICATE_CLOSE_SOURCE)
WINAPI_RETCODE_CHECK(retcode, 'DuplicateHandle')

# Close the handle
retcode = windll.kernel32.CloseHandle(myMtxHandle)
WINAPI_RETCODE_CHECK(retcode, 'CloseHandle')

# Open another instance of the task manager
os.system('start taskmgr')
