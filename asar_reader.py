'''
List and extract content from asar archive files (see https://github.com/electron/asar)

Author: Eli Finkel - eyfinkel@gmail.com
'''


import sys
import json


class Asar():
    def __init__(self, path):
        # see binary format here:
        # https://github.com/electron/asar/blob/b1c8deb55f431275255a2eac9edcce6468983b92/lib/disk.js#L57
        
        self.f = open(path, 'rb')
        
        # read buf len
        # (don't really need this, as there's no need to preallocate)
        buf_len = self.__get_pickled()
        buf_len = int.from_bytes(buf_len, 'little')
        
        # read the buffer (which is again prefixed with )
        buf = self.__get_pickled()
        header_len = int.from_bytes(buf[:4], 'little')
        self.header = json.loads(buf[4:4+header_len].decode('utf-8'))
        self.read_base = self.f.tell()
        
        self.entries = {}
        self.__build_file_list('/', self.header['files'])
    
    def get_entries(self):
        return [f'{k} ({v["size"]} bytes)' for k,v in self.entries.items()]
    
    def get_entry(self, file):
        # normalize
        file = file.replace('\\', '/')
        if not file.startswith('/'):
            file = '/'+file
        
        try:
            info = self.entries[file]
        except KeyError:
            raise IOError('No such entry') from None
        
        self.f.seek(self.read_base+int(info['offset']))
        ret = self.__read_safe(info['size'])
        return ret
    
    def __get_pickled(self):
        length = self.__read_safe(4)
        length = int.from_bytes(length, 'little')
        ret = self.__read_safe(length)
        return ret
    
    def __read_safe(self, length):
        ret = self.f.read(length)
        if len(ret) != length:
            raise IOError('Error reading from file')
        return ret
    
    def __build_file_list(self, base_dir, node):
        for k, v in node.items():
            if 'files' in v:
                # folder
                self.__build_file_list(f'{base_dir}{k}/', v['files'])
            else:
                # file
                self.entries[f'{base_dir}{k}'] = v
    
    def __del__(self):
        if hasattr(self, 'f'):
            self.f.close()


def main():
    if len(sys.argv) <= 1 or len(sys.argv) > 3:
        print(
            'Usage:\n'\
            f'  List entries              : {sys.argv[0]} <asar_file>\n'\
            f'  Extract entry (to stdout) : {sys.argv[0]} <asar_file> <entry>\n')
        return 1
    
    asar = Asar(sys.argv[1])
    if len(sys.argv) == 2:
        print(*asar.get_entries(), sep='\n')
        return 0
    
    if len(sys.argv) == 3:
        f = asar.get_entry(sys.argv[2])
        sys.stdout.buffer.write(f)
        return 0
    
    return 'should never get here'

if __name__ == '__main__':
    exit(main())
