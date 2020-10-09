import sys
import datetime
import uuid
import collections

from msf import MSFFile
from util import *
from enums import *

# Format documentation used: https://llvm.org/docs/PDB/ , https://github.com/Microsoft/microsoft-pdb

class SerializedHashTable(object):
    ''' Represent a serialized hash table (https://llvm.org/docs/PDB/HashTable.html ) '''

    def __init__(self, stream, value_width, value_mapper):
        ''' Initialize from stream (pass value width and callable to map from bytes to value) '''
        
        # Read size and capacity
        self.size = Util.read_le_unsigned(stream, 4)
        self.capacity = Util.read_le_unsigned(stream, 4)
        assert self.size <= self.capacity, 'invalid hash table size'
        
        # Read present bit vector
        self.present_word_count = Util.read_le_unsigned(stream, 4)
        self.present_bit_vector = []
        for _ in range(self.present_word_count):
            self.present_bit_vector += Util.num_to_bit_vector(Util.read_le_unsigned(stream, 4), 32)[::-1]
        assert self.present_bit_vector.count(True) == self.size, 'invalid hash table capacity bits'
        
        # Read deleted bit vector
        self.deleted_word_count = Util.read_le_unsigned(stream, 4)
        self.deleted_bit_vector = []
        for _ in range(self.deleted_word_count):
            self.deleted_bit_vector += Util.num_to_bit_vector(Util.read_le_unsigned(stream, 4), 32)[::-1]
        
        self.buckets = [None] * self.capacity # array of capacity elements (with only present buckets filled)
        entry_type = collections.namedtuple('HashTableEntry', ('key', 'value'))
        for i in range(self.capacity):
            if self.present_bit_vector[i]:
                key = Util.read_le_unsigned(stream, 4)
                val = value_mapper(Util.read_bytes(stream, value_width))
                self.buckets[i] = entry_type(key, val)
    
    def values(self):
        ''' Get list of present values '''
        return list(filter(None, self.buckets))


def main(file):
    pdb = MSFFile(file)
    
    def read_pdb_info_stream(pdb):
        ''' see https://llvm.org/docs/PDB/PdbStream.html '''
        
        pdb_info_stream = pdb.get_stream(1) # always at stream 1
        
        version = Util.read_le_unsigned(pdb_info_stream, 4)
        version = Enums.PdbInfoStreamVersion(version)
        signature = Util.read_le_unsigned(pdb_info_stream, 4)
        local_time_zone = datetime.datetime.now().astimezone().tzinfo
        # for CPP pdb files, the signature is a timestampt. For .NET however it's not
        signature_time = datetime.datetime.fromtimestamp(signature, local_time_zone).strftime('%Y-%m-%d %H:%M:%S (%Z)')
        age = Util.read_le_unsigned(pdb_info_stream, 4)
        unique_id = str(uuid.UUID(bytes_le=Util.read_bytes(pdb_info_stream, 16))).upper()
        
        print(f'\n'\
              f'  file       :  {pdb.fname}\n'\
              f'  version    :  {repr(version)}\n'\
              f'  signature  :  0x{signature:X} - {signature_time}\n'\
              f'  age        :  {age}\n'\
              f'  uuid       :  {{{unique_id}}}\n')
        
        # Read string data
        named_stream_string_data_len = Util.read_le_unsigned(pdb_info_stream, 4)
        named_stream_string_data = Util.read_bytes(pdb_info_stream, named_stream_string_data_len)
        
        # Read stream table
        named_stream_table = SerializedHashTable(pdb_info_stream, 4, lambda buf: Util.read_le_unsigned(io.BytesIO(buf), len(buf)))
        for key, val in named_stream_table.values():
            stream_name = Util.get_null_terminated_str(named_stream_string_data, key)
            stream = pdb.get_stream(val)
            print(stream_name)
            #print(stream.read())
        
        # Read feature flag (not sure if I did this right and what to do with it)
        
        # Flags (just read ints till the end)
        has_ipi_stream = False
        no_type_merge = False
        minimal_debug_info = False
        while len(pdb_info_stream.peek(4))==4:
            val = Util.read_le_unsigned(pdb_info_stream, 4)
            if val == Enums.PdbInfoStreamFeature.VC110.value:
                has_ipi_stream = True
                break # no more flags
            if val == Enums.PdbInfoStreamFeature.VC140.value:
                has_ipi_stream = True
            if val == Enums.PdbInfoStreamFeature.NoTypeMerge.value:
                no_type_merge = True
            if val == Enums.PdbInfoStreamFeature.MinimalDebugInfo.value:
                minimal_debug_info = True
    
    def read_tpi_stream(pdb):
        ''' see https://llvm.org/docs/PDB/TpiStream.html '''
        
        tpi_stream = pdb.get_stream(2) # always at stream 2
        
        version = Util.read_le_unsigned(tpi_stream, 4)
        version = Enums.TpiStreamVersion(version)
        header_size = Util.read_le_unsigned(tpi_stream, 4)
        assert header_size == 56, 'unknown header'
        type_index_begin = Util.read_le_unsigned(tpi_stream, 4)
        assert type_index_begin == 0x1000, 'unexpected begin index'
        type_index_end = Util.read_le_unsigned(tpi_stream, 4)
        type_record_bytes = Util.read_le_unsigned(tpi_stream, 4)
        hash_stream_index = Util.read_le_signed(tpi_stream, 2)
        hash_aux_stream_index = Util.read_le_signed(tpi_stream, 2)
        hash_key_size = Util.read_le_unsigned(tpi_stream, 4)
        num_hash_buckets = Util.read_le_unsigned(tpi_stream, 4)
        hash_value_buffer_offset = Util.read_le_unsigned(tpi_stream, 4)
        hash_value_buffer_length = Util.read_le_unsigned(tpi_stream, 4)
        assert hash_value_buffer_length == (type_index_end-type_index_begin)*4
        index_offset_buffer_offset = Util.read_le_unsigned(tpi_stream, 4)
        index_offset_buffer_length = Util.read_le_unsigned(tpi_stream, 4)
        hash_adj_buffer_offset = Util.read_le_unsigned(tpi_stream, 4)
        hash_adj_buffer_length = Util.read_le_unsigned(tpi_stream, 4)
        
        # Read type records (see handling in microsoft-pdb strForTypeTi())
        print(f'parsing {(type_index_end-type_index_begin)} records')
        for i in range(type_index_begin, type_index_end):
            print(f'parsing record: {i}')
            record_len = Util.read_le_unsigned(tpi_stream, 2)
            assert record_len >= 2, 'corrupt record'
            record_kind = Util.read_le_unsigned(tpi_stream, 2)
            if record_kind < type_index_begin:
                pass # primitive impl
            record_kind = Enums.CodeView.LEAF_ENUM(record_kind)
            record_data = Util.read_bytes(tpi_stream, record_len-2)
            record_stream = Util.ConcatByteStreams([record_data])
            
            print('record: ' + str(i), record_len, record_kind, record_data)
            
            def str_from_numeric_val(stream):
                attributes = Util.read_le_unsigned(stream, 2)
                kind = Util.read_le_unsigned(stream, 2)
                if kind < Enums.CodeView.LEAF_ENUM.LF_NUMERIC.value:
                    ret = str(kind)+f':s16'
                else:
                    kind = Enums.CodeView.LEAF_ENUM(kind)
                    if kind == Enums.CodeView.LEAF_ENUM.LF_CHAR: ret = str(Util.read_le_unsigned(stream, 1))+':u8'
                    elif kind == Enums.CodeView.LEAF_ENUM.LF_SHORT: ret = str(Util.read_le_signed(stream, 2))+':s16'
                    elif kind == Enums.CodeView.LEAF_ENUM.LF_USHORT: ret = str(Util.read_le_unsigned(stream, 2))+':u16'
                    elif kind == Enums.CodeView.LEAF_ENUM.LF_LONG: ret = str(Util.read_le_signed(stream, 4))+':s32'
                    elif kind == Enums.CodeView.LEAF_ENUM.LF_ULONG: ret = str(Util.read_le_unsigned(stream, 4))+':u32'
                    elif kind == Enums.CodeView.LEAF_ENUM.LF_QUADWORD: ret = str(Util.read_le_signed(stream, 8))+':s64'
                    elif kind == Enums.CodeView.LEAF_ENUM.LF_UQUADWORD: ret = str(Util.read_le_unsigned(stream, 8))+':u64'
                    else: assert False, f'unexpected numeric leaf: {kind}'
                
                return ret + f' (attrs: {Enums.CodeView.CV_fldattr_to_str(attributes)})'
                
            def str_from_leaf_enumerate(stream):
                value = str_from_numeric_val(stream)
                name = Util.read_null_terminated_str(stream)
                return f'{name.decode()} = {value}'
                
            
            if record_kind == Enums.CodeView.LEAF_ENUM.LF_FIELDLIST:
                expected_inner_kind = None # In a field list, we expect all elements to be of the same kind,
                                           # so once we determine the kind of the first element, check that all match
                first_print = True
                while True:
                    next_char = record_stream.peek(1)
                    if not next_char:
                        break # end of stream
                    if Enums.CodeView.LEAF_ENUM.LF_PAD0.value <= next_char[0] <= Enums.CodeView.LEAF_ENUM.LF_PAD15.value:
                        record_stream.read(1) # skip padding (see microsoft-pdb strForFieldList())
                        #print(f'skip {record_stream.read(1)}') # skip padding (see microsoft-pdb strForFieldList())
                        continue
                        
                    inner_record_kind = Util.read_le_unsigned(record_stream, 2)
                    inner_record_kind = Enums.CodeView.LEAF_ENUM(inner_record_kind)
                    if expected_inner_kind == None: expected_inner_kind = inner_record_kind
                    assert inner_record_kind == expected_inner_kind, 'all elements of LF_FIELDLIST must be the same'
                    if inner_record_kind == Enums.CodeView.LEAF_ENUM.LF_ENUMERATE:
                        if first_print:
                            print(inner_record_kind)
                            first_print = False
                        print('  ' + str_from_leaf_enumerate(record_stream))
                    else:
                        print('cant handle inner: ' + str(inner_record_kind))
                        #break
                        exit(1)
            
            elif record_kind == Enums.CodeView.LEAF_ENUM.LF_ENUM:
                element_count = Util.read_le_unsigned(record_stream, 2)
                property_attributes = Util.read_le_unsigned(record_stream, 2)
                underlying_type = Util.read_le_unsigned(record_stream, 4)
                underlying_type = Enums.CodeView.TYPE_ENUM(underlying_type)
                field_list_index = Util.read_le_unsigned(record_stream, 4)
                name = Util.read_null_terminated_str(record_stream)
                mangled_name = Util.read_null_terminated_str(record_stream)
                print(f'enum {name.decode()} ({mangled_name.decode()}):\n'\
                      f'  element count    :  {element_count}\n'\
                      f'  elements index   :  0x{field_list_index:X}\n'\
                      f'  underlying type  :  {repr(underlying_type)}\n'\
                      f'  attributes       :  {Enums.CodeView.CV_prop_to_str(property_attributes)}')
            elif record_kind == Enums.CodeView.LEAF_ENUM.LF_MODIFIER:
                underlying_type = Util.read_le_unsigned(record_stream, 4)
                underlying_type = Enums.CodeView.TYPE_ENUM(underlying_type)
                attributes = Util.read_le_unsigned(record_stream, 2)
                attributes = Enums.CodeView.CV_modifier_to_str(attributes)
                print(underlying_type, attributes)
            else:
                print('cant handle: ' + str(record_kind))
                exit(1)

            
        
    read_pdb_info_stream(pdb)
    read_tpi_stream(pdb)
    
    return read_tpi_stream,pdb

if __name__ == '__main__':
    main(sys.argv[1])
