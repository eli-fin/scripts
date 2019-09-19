'''
Calculate hash of files

Usage: <script> file1, file2, ...

Author: Eli Finkel - eyfinkel@gmail.com
'''

import hashlib
import sys
import time

DEFAULT_ALGO     = 'md5'         # Default hashing algorithm
ALGO_ARG_PREFIX  = '-hash='      # Prefix for algorithm argument
BYTES_TO_READ    = 1024*1024*512 # Half a GB chunks
output_str       = '''
----------------------------------------------------------
| File Name:     %s
| File Size:     %s bytes
| Hash:          %s
| Total Seconds: %s
----------------------------------------------------------

'''

def main():
    if len(sys.argv) == 1:
        print('\nNo files found...\n')
        print('This script will print the selected hash for each file passed as an argument')
        print('You can select the hash algorithm by passing ' + ALGO_ARG_PREFIX + 'value')
        print('The available hashes are:\n"' + ', '.join(set([x.lower() for x in hashlib.algorithms_available])) + '"')
        print('Default hash: ' + DEFAULT_ALGO)
        print('e.g. <script> <file1> <file2> ...')
    
    hashAlgorithm = DEFAULT_ALGO
    print('\n')
    
    # Get hash algorithm from user
    algo = [x for x in sys.argv[1:] if x.startswith(ALGO_ARG_PREFIX)]
    if algo:
        hashAlgorithm = algo[0].replace(ALGO_ARG_PREFIX, '')
        sys.argv.remove(algo[0])
    
    for fname in sys.argv[1:]:
        try:
            hash = hashlib.new(hashAlgorithm)
        except ValueError:
            print('ERROR: No support for "'+hashAlgorithm+'" algorithm')
            exit()
            
        f = open(fname, 'rb')
        startTime = time.time()
        filesize = 0
        
        chunk = f.read(BYTES_TO_READ) # Process large file by chunks
        while chunk:
            filesize+=len(chunk)
            hash.update(chunk)
            del chunk # Don't wait for GC
            chunk = f.read(BYTES_TO_READ)
        
        endTime = time.time()
        print(output_str % (fname, '{:,}'.format(filesize), hashAlgorithm+': '+hash.hexdigest().upper(), endTime-startTime))

if __name__ == '__main__':
    main()
    