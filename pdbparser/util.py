import io

class Util(object):
    ''' Helper methods '''

    @staticmethod
    def read_magic(readable, magic):
        ''' Read and verify magic '''
        val = readable.read(len(magic))
        assert len(val) == len(magic), 'read_magic: Can\'t read from stream'
        assert type(val) == type(b''), 'read_magic: Not a byte stream'
        assert val == magic, 'read_magic: Not a valid magic'
        return magic
    
    @staticmethod
    def read_le_unsigned(readable, length):
        ''' Read an unsigned variable length number from a little-endian stream '''
        ret = 0
        n = length
        while n:
            val = readable.read(1)
            assert len(val) == 1, 'read_le_unsigned: Can\'t read from stream'
            val = ord(val)
            ret += val << (8*(length-n))
            n-=1
        return ret
    
    @staticmethod
    def read_le_signed(readable, length):
        ''' Read an signed variable length number from a little-endian stream '''
        ret = Util.read_le_unsigned(readable, length)
        if ret >> ((8*length)-1):
            ret = -((2**(8*length))-ret)
        return ret
    
    @staticmethod
    def read_bytes(readable, length):
        ''' read the bytes '''
        val = readable.read(length)
        assert len(val) == length, 'read_bytes: Can\'t read from stream'
        return val
    
    @staticmethod
    def read_null_terminated_str(readable):
        ''' read the chars '''
        val = b''
        while (b:=readable.read(1)) != b'\0': val += b
        return val
    
    @staticmethod
    def get_null_terminated_str(buf, index=0):
        ''' get null terminated string from buffer '''
        assert type(buf) is bytes, 'buf must be bytes'
        assert type(index) is int, 'buf must be bytes'
        
        end = buf.find(b'\x00', index)
        assert end != -1, 'buf is not a null terminated string'
        
        return buf[index:end]
    
    @staticmethod
    def num_to_bit_vector(n, width):
        return [bool(int(i)) for i in f'{n:0>{width}b}'] # get boolean array from boolean number
    
    class ConcatByteStreams(object):
        ''' Concatenate 1 or more byte streams or byte objects to a single stream '''
        
        def __init__(self, streams):
            assert hasattr(streams, '__iter__'), str(streams) + ' is not an iterable'
            streams = streams or [b''] # use empty bytes if none found
            for s in streams: assert hasattr(s, 'read') or type(s)==bytes, str(s) + ' is not a readable'
            self.streams = [io.BytesIO(s) if type(s)==bytes else s for s in streams] # convert byte objects to streams
        
        def read(self, n=-1):
            ret = b''
            to_read = n
            while len(ret) < n or n == -1:
                if not self.streams:
                    return ret
                more = self.streams[0].read(8192 if n == -1 else to_read)
                if not more:
                    self.streams.pop(0)
                to_read -= len(more)
                ret += more
            return ret
        
        def peek(self, n):
            ret = self.read(n)
            if ret:
                self.streams.insert(0, io.BytesIO(ret)) # push it back for the next read operation
            return ret
