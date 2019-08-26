'''
Prevent computer from sleeping

Author: Eli Finkel - eyfinkel@gmail.com
'''

import ctypes, time

ES_CONTINUOUS       = 0x80000000
ES_DISPLAY_REQUIRED = 0x00000002
ES_SYSTEM_REQUIRED  = 0x00000001

def dontSleep():
    print("Preventing sleep (ctrl+c to stop) ...")
    try:
        while True: # Sleep for a minute and call SetThreadExecutionState
            for i in range(60): # Sleep in seconds, to allow interruptions
                time.sleep(1)
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS|ES_DISPLAY_REQUIRED|ES_SYSTEM_REQUIRED)
    except KeyboardInterrupt: # Restore status
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    print("Stopped")

dontSleep()
