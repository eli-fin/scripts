'''
The script will search the folder recursively for any zip/jar files
and print all entries in jar contain the filter

Usage: <script> <folder-path> <zip-entry-filter>

Author: Eli Finkel - eyfinkel@gmail.com
'''

import sys, os, zipfile, traceback

def _print(str): print(str, flush=True)
def _dbg(str):
    if '-debug' in sys.argv:
        _print(str)

def iszip(f):
    return f.endswith('.zip') or f.endswith('.jar')

def handle_folder(folder, entry_filter):
    _dbg('Folder: ' + folder)
    lst = os.listdir(folder)
    for f in lst:
        fname = folder+'/'+f
        try:
            if os.path.isdir(fname):
                handle_folder(fname, entry_filter)
            elif iszip(f):
                print_zip_entries(fname, entry_filter)
            else:
                _dbg('Skipping ' + fname)
        except Exception:
            _print('Error handling: ' + fname)
            traceback.print_exc()

def print_zip_entries(fname, entry_filter):
    z=zipfile.ZipFile(fname)
    for e in z.namelist():
        if entry_filter in e:
            _print(fname+': '+e)

def main():
    _print('Expecting args: folder-path, zip-entry-filter')
    folder = sys.argv[1]
    entry_filter = sys.argv[2]
    handle_folder(folder, entry_filter)
    
if __name__ == '__main__':
    main()
