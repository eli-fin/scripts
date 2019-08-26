'''
Start a command as administrator (you'll get a UAC popup to confirm)
(you can also pass an appname, like 'chrome' or 'notepad++', not only an exe name. leave empty for a cmd window)

Usage: <script> <exe> args...

Author: Eli Finkel - eyfinkel@gmail.com
'''
# run as admin the supplied command


def main():
    from ctypes import windll
    import sys, os
    
    if len(sys.argv) < 2: # For no args, just open cmd in current dir
        bin = 'cmd'
        args = f'/k cd {os.getcwd()}'
    else:
        bin = sys.argv[1]
        args = ' '.join([arg for arg in sys.argv[2:]])
    ret = windll.shell32.ShellExecuteW(0, "runas", bin, args, 0, 10, 0)
    
    if ret == 31: # exe file not found, start as non exe file (which will be opened by it's assciated handler)
        args = '' + args
        windll.shell32.ShellExecuteW(0, "runas", "cmd", r"/c start " + bin, 0, 10, 0)
        
    elif ret != 42: # not success
        print(f'Admin script: Some error ({ret})')

    
if __name__ == '__main__':
    main()
    