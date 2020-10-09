import math
import io

from util import *

class MSFFile(object):
    '''
    Represents an MSF file.
    MSF is a container file (Multistream File, a file that contains a number of streams)
    
    Format documentation used: https://llvm.org/docs/PDB/MsfFile.html
    '''
    
    def __init__(self, readable):
        ''' Initialize from readable (or file name) '''
        
        if not hasattr(readable, 'read'):
            readable = open(readable, 'rb')
        
        self.fname = readable.name if hasattr(readable, 'name') else '<unknown>'
        
        # read the superblock
        self.magic = Util.read_magic(readable, b'Microsoft C/C++ MSF 7.00\r\n\x1A\x44\x53\x00\x00\x00')
        
        self.block_size = Util.read_le_unsigned(readable, 4)
        assert self.block_size in (512, 1024, 2048, 4096), 'Invalid block size ' + str(self.block_size)
        
        self.free_block_map_block  = Util.read_le_unsigned(readable, 4)
        assert self.free_block_map_block in (1, 2), 'Invalid free block map block ' + str(self.free_block_map_block)
        
        self.num_blocks = Util.read_le_unsigned(readable, 4)
        
        self.num_directory_bytes = Util.read_le_unsigned(readable, 4)
        
        self.unknown = Util.read_le_unsigned(readable, 4)
        
        self.block_map_addr = Util.read_le_unsigned(readable, 4)
        
        # now read till the end of the super block
        Util.read_bytes(readable, self.block_size-len(self.magic)-4-4-4-4-4-4)
        
        # Read all blocks
        self.blocks = [None] # None to represent the first stream
        for _ in range(self.num_blocks-1):
            self.blocks.append(Util.read_bytes(readable, self.block_size))
        assert readable.read() == b'', 'Extra bytes at the end of the file'
        
        # See how many blocks the stream directory occupies
        num_of_stream_directory_blocks = math.ceil(self.num_directory_bytes / self.block_size)
        stream_directory_block_addrs = []
        block_map = io.BytesIO(self.blocks[self.block_map_addr])
        for _ in range(num_of_stream_directory_blocks):
            stream_directory_block_addrs.append(Util.read_le_unsigned(block_map, 4))
        
        # Stream of all stream directory blocks
        stream_directories_stream = Util.ConcatByteStreams([self.blocks[b] for b in stream_directory_block_addrs])
        self.stream_sizes = []
        self.streams = []
        
        # Populate stream_sizes
        num_streams = Util.read_le_unsigned(stream_directories_stream, 4)
        for _ in range(num_streams):
            self.stream_sizes.append(Util.read_le_unsigned(stream_directories_stream, 4))

        # Populate streams
        for size in self.stream_sizes:
            blocks_per_stream = math.ceil(size / self.block_size)
            stream_blocks = []
            for _ in range(blocks_per_stream):
                stream_blocks.append(Util.read_le_unsigned(stream_directories_stream, 4))
            self.streams.append(stream_blocks)
    
    def get_stream(self, stream_number):
        ''' Get all stream blocks as a single stream '''
        return Util.ConcatByteStreams([self.blocks[b] for b in self.streams[stream_number]])
