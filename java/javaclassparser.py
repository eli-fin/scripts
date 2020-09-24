'''
This is a simple Java Class file parser.
It allows you to parse a class file into an object.
You can inspect it in memory, change it and save it to a class file.
(format verification is not really performed, so you should know what you're doing.
 for example if you add an entry to constant_pool, you should update constant_pool_count.
 However you can edit strings freely and they will be saved with the correct length)

Java class file documentation: https://docs.oracle.com/javase/specs/jvms/se7/html/jvms-4.html

Usage:
   to parse a class file:                             cls = ClassFile(open('x.class', 'rb'))
   to save the class file:                            cls.save(open('x2.class', 'wb'))
   
   to view the class and it's member type/name/info:  HelperMethods.PrintClassAndMemberInfo(cls)
   to view the class and member attributes:           HelperMethods.PrintAttributeNames(cls)
   
   the fields and their names basically match the oracle documentation above, so you should be able to
   access all the information you want about the class and build scripts on top of this
   
   You can also use this as a script to view the output of PrintClassAndMemberInfo and PrintAttributeNames.
   Just pass a class file as an argument: <script> x.class
   
Author: Eli Finkel - eyfinkel@gmail.com
'''

class ClassFile(object):
    ''' Represents a Java class file '''
    
    def __init__(self, readable):
        ''' Initialize from readable (or file name) '''
        
        if not hasattr(readable, 'read'):
            readable = open(readable, 'rb')
        
        self.magic = Util.readMagic(readable)
        
        self.minor_version = Util.readUnsigned(readable, 2)
        self.major_version = Util.readUnsigned(readable, 2)
        
        self.constant_pool_count = Util.readUnsigned(readable, 2)
        self.constant_pool = []
        for i in range(1, self.constant_pool_count):
            if len(self.constant_pool) and self.constant_pool[-1] != None and self.constant_pool[-1].tag in (5,6): # skip index
                self.constant_pool.append(None)
            else:
                self.constant_pool.append(cp_info(readable, i, self.constant_pool_count))
        
        self.access_flags = Util.readUnsigned(readable, 2)
        self.this_class = Util.readUnsigned(readable, 2)
        self.super_class = Util.readUnsigned(readable, 2)
        self.interfaces_count = Util.readUnsigned(readable, 2)
        self.interfaces = []
        for i in range(self.interfaces_count):
            self.interfaces.append(Util.readUnsigned(readable, 2))
        self.fields_count = Util.readUnsigned(readable, 2)
        self.fields = []
        for i in range(self.fields_count):
            self.fields.append(member_info(readable, 'field', self.constant_pool_count))
        self.methods_count = Util.readUnsigned(readable, 2)
        self.methods = []
        for i in range(self.methods_count):
            self.methods.append(member_info(readable, 'method', self.constant_pool_count))
        self.attributes_count = Util.readUnsigned(readable, 2)
        self.attributes = []
        for i in range(self.attributes_count):
            self.attributes.append(attribute_info(readable, self.constant_pool_count))
        
        assert readable.read() == b'', 'Extra bytes at the end of the file'
    
    def __str__(self):
        version = f'{self.major_version}.{self.minor_version} ({HelperMethods.MajorClassVersionToJavaVersion(self.major_version)})'
        className = self.constant_pool[self.constant_pool[self.this_class-1].name_index-1].bytes
        actualConstants = len([x for x in self.constant_pool if x is not None])
        return f'Java ClassFile {className} v{version}, ' + \
               f'{self.constant_pool_count} constants (actual {actualConstants})'
    
    __repr__ = __str__
    
    def save(self, writable):
        ''' Write the class to writable (or file name) '''
        
        if not hasattr(writable, 'write'):
            writable = open(writable, 'wb')
        
        Util.writeUnsigned(writable, self.magic, 4)
        
        Util.writeUnsigned(writable, self.minor_version, 2)
        Util.writeUnsigned(writable, self.major_version, 2)
        
        Util.writeUnsigned(writable, self.constant_pool_count, 2)
        for cpinf in self.constant_pool:
            if cpinf is not None:
                cpinf.save(writable)
        
        Util.writeUnsigned(writable, self.access_flags, 2)
        Util.writeUnsigned(writable, self.this_class, 2)
        Util.writeUnsigned(writable, self.super_class, 2)
        Util.writeUnsigned(writable, self.interfaces_count, 2)
        for intf in self.interfaces:
            Util.writeUnsigned(writable, intf, 2)
        Util.writeUnsigned(writable, self.fields_count, 2)
        for fld in self.fields:
            fld.save(writable)
        Util.writeUnsigned(writable, self.methods_count, 2)
        for meth in self.methods:
            meth.save(writable)
        Util.writeUnsigned(writable, self.attributes_count, 2)
        for attr in self.attributes:
            attr.save(writable)


class cp_info(object):
    ''' Represents a constant '''
    
    def __init__(self, readable, index, cp_info_count):
        ''' Initialize from readable '''
        
        self.tag = Util.readUnsigned(readable, 1)
        self.index = index
        if self.tag == 7:
            self.type = 'Class'
            self.name_index = Util.readUnsigned(readable, 2)
            assert 0 < self.name_index < cp_info_count, 'Invalid name_index'
        elif self.tag == 9:
            self.type = 'Fieldref'
            self.name_index = Util.readUnsigned(readable, 2)
            assert 0 < self.name_index < cp_info_count, 'Invalid name_index'
            self.name_and_type_index = Util.readUnsigned(readable, 2)
            assert 0 < self.name_and_type_index < cp_info_count, 'Invalid name_and_type_index'
        elif self.tag == 10:
            self.type = 'Methodref'
            self.name_index = Util.readUnsigned(readable, 2)
            assert 0 < self.name_index < cp_info_count, 'Invalid name_index'
            self.name_and_type_index = Util.readUnsigned(readable, 2)
            assert 0 < self.name_and_type_index < cp_info_count, 'Invalid name_and_type_index'
        elif self.tag == 11:
            self.type = 'InterfaceMethodref'
            self.name_index = Util.readUnsigned(readable, 2)
            assert 0 < self.name_index < cp_info_count, 'Invalid name_index'
            self.name_and_type_index = Util.readUnsigned(readable, 2)
            assert 0 < self.name_and_type_index < cp_info_count, 'Invalid name_and_type_index'
        elif self.tag == 8:
            self.type = 'String'
            self.string_index = Util.readUnsigned(readable, 2)
            assert 0 < self.string_index < cp_info_count, 'Invalid string_index'
        elif self.tag == 3:
            self.type = 'Integer'
            self.bytes = Util.readSigned(readable, 4)
        elif self.tag == 4:
            self.type = 'Float'
            self.bytes = Util.readFloat(readable)
        elif self.tag == 5:
            self.type = 'Long'
            self.bytes = Util.readSigned(readable, 8)
        elif self.tag == 6:
            self.type = 'Double'
            self.bytes = Util.readDouble(readable)
        elif self.tag == 12:
            self.type = 'NameAndType'
            self.name_index = Util.readUnsigned(readable, 2)
            assert 0 < self.name_index < cp_info_count, 'Invalid name_index'
            self.descriptor_index = Util.readUnsigned(readable, 2)
            assert 0 < self.descriptor_index < cp_info_count, 'Invalid descriptor_index'
        elif self.tag == 1:
            self.type = 'Utf8'
            self.bytes = Util.readUtf8(readable)
        elif self.tag == 15:
            self.type = 'MethodHandle'
            self.reference_kind = Util.readUnsigned(readable, 1)
            assert 1 <= self.reference_kind <= 9, 'Invalid reference_kind'
            self.reference_index = Util.readUnsigned(readable, 2)
            assert 0 < self.reference_index < cp_info_count, 'Invalid reference_index'
        elif self.tag == 16:
            self.type = 'MethodType'
            self.descriptor_index = Util.readUnsigned(readable, 2)
            assert 0 < self.descriptor_index < cp_info_count, 'Invalid descriptor_index'
        elif self.tag == 18:
            self.type = 'InvokeDynamic'
            self.bootstrap_method_attr_index = Util.readUnsigned(readable, 2) # must be a valid index to bootstrap_methods, but we can't verify this now
            self.name_and_type_index = Util.readUnsigned(readable, 2)
            assert 0 < self.name_and_type_index < cp_info_count, 'Invalid name_and_type_index'
        else:
            raise Exception('cp_info: unknown tag value')
        
    def __str__(self):
        fields = [f for f in dir(self) if not f.startswith('__') and f not in ('tag', 'type', 'index')]
        ret = f'cp_info#{self.index} {self.type}({self.tag}): '
        for f in fields:
            if not callable(getattr(self, f)):
                ret += f'{f}=({getattr(self, f)}), '
        return ret.rstrip(', ')
    __repr__ = __str__
    
    
    def save(self, writable):
        ''' Write the cp_info to writable '''
        Util.writeUnsigned(writable, self.tag, 1)
        if self.tag == 7:
            Util.writeUnsigned(writable, self.name_index, 2)
        elif self.tag == 9:
            Util.writeUnsigned(writable, self.name_index, 2)
            Util.writeUnsigned(writable, self.name_and_type_index, 2)
        elif self.tag == 10:
            Util.writeUnsigned(writable, self.name_index, 2)
            Util.writeUnsigned(writable, self.name_and_type_index, 2)
        elif self.tag == 11:
            Util.writeUnsigned(writable, self.name_index, 2)
            Util.writeUnsigned(writable, self.name_and_type_index, 2)
        elif self.tag == 8:
            Util.writeUnsigned(writable, self.string_index, 2)
        elif self.tag == 3:
            Util.writeSigned(writable, self.bytes, 4)
        elif self.tag == 4:
            Util.writeFloat(writable, self.bytes)
        elif self.tag == 5:
            Util.writeSigned(writable, self.bytes, 8)
        elif self.tag == 6:
            Util.writeDouble(writable, self.bytes)
        elif self.tag == 12:
            Util.writeUnsigned(writable, self.name_index, 2)
            Util.writeUnsigned(writable, self.descriptor_index, 2)
        elif self.tag == 1:
            Util.writeUtf8(writable, self.bytes)
        elif self.tag == 15:
            Util.writeUnsigned(writable, self.reference_kind, 1)
            Util.writeUnsigned(writable, self.reference_index, 2)
        elif self.tag == 16:
            Util.writeUnsigned(writable, self.descriptor_index, 2)
        elif self.tag == 18:
            Util.writeUnsigned(writable, self.bootstrap_method_attr_index, 2)
            Util.writeUnsigned(writable, self.name_and_type_index, 2)
        else:
            raise Exception('cp_info: unknown tag value')


class member_info(object):
    ''' Represents a field '''
    
    def __init__(self, readable, type, cp_info_count):
        ''' Initialize from readable '''
        
        self.type = type
        self.access_flags = Util.readUnsigned(readable, 2)
        self.name_index = Util.readUnsigned(readable, 2)
        assert 0 < self.name_index < cp_info_count, 'Invalid name_index'
        self.descriptor_index = Util.readUnsigned(readable, 2)
        assert 0 < self.descriptor_index < cp_info_count, 'Invalid descriptor_index'
        self.attributes_count = Util.readUnsigned(readable, 2)
        self.attributes = []
        for i in range(self.attributes_count):
            self.attributes.append(attribute_info(readable, cp_info_count))
        
        
    def __str__(self):
        fields = [f for f in dir(self) if not f.startswith('__') and f not in ('type',)]
        ret = f'member_info ({self.type})#: '
        for f in fields:
            if not callable(getattr(self, f)):
                ret += f'{f}=({getattr(self, f)}), '
        return ret.rstrip(', ')
    __repr__ = __str__
    
    
    def save(self, writable):
        ''' Write the member_info to writable '''
        
        Util.writeUnsigned(writable, self.access_flags, 2)
        Util.writeUnsigned(writable, self.name_index, 2)
        Util.writeUnsigned(writable, self.descriptor_index, 2)
        Util.writeUnsigned(writable, self.attributes_count, 2)
        for attr in self.attributes:
            attr.save(writable)


class attribute_info(object):
    ''' Represents an attribute '''
    
    def __init__(self, readable, cp_info_count):
        ''' Initialize from readable '''
        
        self.attribute_name_index = Util.readUnsigned(readable, 2)
        assert 0 < self.attribute_name_index < cp_info_count, 'Invalid attribute_name_index'
        self.attribute_length = Util.readUnsigned(readable, 4)
        self.info = Util.readBytes(readable, self.attribute_length)
        
    def __str__(self):
        fields = [f for f in dir(self) if not f.startswith('__') and f not in ('info',)]
        ret = f'attribute_info#: '
        for f in fields:
            if not callable(getattr(self, f)):
                ret += f'{f}=({getattr(self, f)}), '
        return ret.rstrip(', ')
    __repr__ = __str__
    
    
    def save(self, writable):
        ''' Write the attribute_info to writable '''
        
        Util.writeUnsigned(writable, self.attribute_name_index, 2)
        Util.writeUnsigned(writable, self.attribute_length, 4)
        Util.writeBytes(writable, self.info)


class Util(object):
    ''' Helper methods '''

    @staticmethod
    def readMagic(readable):
        ''' Read the magic constant '''
        val = readable.read(4)
        assert len(val) == 4, 'readMagic: Can\'t read from stream'
        assert type(val) == type(b''), 'readMagic: Not a byte stream'
        magic = (val[0] << 24) + (val[1] << 16) + (val[2] << 8) + val[3]
        assert magic == 0xCAFEBABE, 'readMagic: Not a valid class file'
        return magic
    
    @staticmethod
    def readUnsigned(readable, length):
        ''' Read an unsigned variable length number from a big-endian stream '''
        ret = 0
        while length:
            length-=1
            val = readable.read(1)
            assert len(val) == 1, 'readUnsigned: Can\'t read from stream'
            val = ord(val)
            ret += val << (8*length)
        return ret
    
    @staticmethod
    def writeUnsigned(writable, val, length):
        ''' Write an unsigned variable length number to a big-endian stream '''
        while length:
            length-=1
            written = writable.write(bytes([val >> (8*length) & 0xff]))
            assert written == 1, 'writeUnsigned: Can\'t write to stream'
    
    @staticmethod
    def readSigned(readable, length):
        ''' Read a signed variable length number from a big-endian stream '''
        ret = Util.readUnsigned(readable, length)
        if ret >> ((8*length)-1):
            ret = -((2**(8*length))-ret)
        return ret
    
    @staticmethod
    def writeSigned(writable, val, length):
        ''' Write a signed variable length number to a big-endian stream '''
        if val < 0:
            val = (2**(8*length))+val
        Util.writeUnsigned(writable, val, length)
    
    @staticmethod
    def readFloat(readable):
        ''' Read a float number from a big-endian stream '''
        import struct
        val = readable.read(4)
        assert len(val) == 4, 'readUnsigned: Can\'t read from stream'
        return struct.unpack('>f', val)[0]
    
    @staticmethod
    def writeFloat(writable, val):
        ''' Write a float number to a big-endian stream '''
        import struct
        written = writable.write(struct.pack('>f', val))
        assert written == 4, 'writeFloat: Can\'t write to stream'

    @staticmethod
    def readDouble(readable):
        ''' Read a double number from a big-endian stream '''
        import struct
        val = readable.read(8)
        assert len(val) == 8, 'readDouble: Can\'t read from stream'
        return struct.unpack('>d', val)[0]
    
    @staticmethod
    def writeDouble(writable, val):
        ''' Write a double number to a big-endian stream '''
        import struct
        written = writable.write(struct.pack('>d', val))
        assert written == 8, 'writeDouble: Can\'t write to stream'

    
    @staticmethod
    def readUtf8(readable):
        ''' Read a utf8 string prefixed by a 2 byte length '''
        length = Util.readUnsigned(readable, 2)
        val = readable.read(length)
        assert len(val) == length, 'readUtf8: Can\'t read from stream'
        return str(val, 'utf8')
    
    @staticmethod
    def writeUtf8(writable, val):
        ''' Write a utf8 string prefixed by a 2 byte length '''
        val = bytes(val, 'utf8')
        Util.writeUnsigned(writable, len(val), 2)
        written = writable.write(val)
        assert written == len(val), 'writeUtf8: Can\'t write to stream'
        
    @staticmethod
    def readBytes(readable, length):
        ''' read the bytes '''
        val = readable.read(length)
        assert len(val) == length, 'readBytes: Can\'t read from stream'
        return val
    
    @staticmethod
    def writeBytes(writable, val):
        ''' Write a utf8 string '''
        written = writable.write(val)
        assert written == len(val), 'writeBytes: Can\'t write to stream'


class HelperMethods:
    
    @staticmethod
    def PrintAttributeNames(cls):
        assert isinstance(cls, ClassFile), 'cls must be a ClassFile'
        
        className = cls.constant_pool[cls.constant_pool[cls.this_class-1].name_index-1].bytes
        for attr in cls.attributes:
            attrName = cls.constant_pool[attr.attribute_name_index-1].bytes
            print(f'{className} attribute: type={attrName}, length={attr.attribute_length}')
        
        if cls.attributes:
            print()
        
        for field in cls.fields:
            fieldName = cls.constant_pool[field.name_index-1].bytes
            for attr in field.attributes:
                attrName = cls.constant_pool[attr.attribute_name_index-1].bytes
                print(f'\t{className}.{fieldName} attribute: type={attrName}, length={attr.attribute_length}')
        
        if cls.fields:
            print()
        
        for method in cls.methods:
            methodName = cls.constant_pool[method.name_index-1].bytes
            for attr in method.attributes:
                attrName = cls.constant_pool[attr.attribute_name_index-1].bytes
                print(f'\t{className}.{methodName}() attribute: type={attrName}, length={attr.attribute_length}')
    
    @staticmethod
    def PrintClassAndMemberInfo(cls):
        assert isinstance(cls, ClassFile), 'cls must be a ClassFile'
        
        version = f'{cls.major_version}.{cls.minor_version} ({HelperMethods.MajorClassVersionToJavaVersion(cls.major_version)})'
        accessFlags = HelperMethods.AccessFlagToStr(cls.access_flags, 'class')
        className = cls.constant_pool[cls.constant_pool[cls.this_class-1].name_index-1].bytes
        if cls.super_class == 0: # Must be object
            superClassName = '<no superclass>'
        else:
            superClassName = cls.constant_pool[cls.constant_pool[cls.super_class-1].name_index-1].bytes
        implementsNames = ''
        for i in cls.interfaces:
            implementsNames += cls.constant_pool[cls.constant_pool[i-1].name_index-1].bytes + ', '
        implementsNames = implementsNames.rstrip(', ')
        fields = []
        for f in cls.fields:
            fieldAccessFlags = HelperMethods.AccessFlagToStr(f.access_flags, 'field')
            fieldType = cls.constant_pool[f.descriptor_index-1].bytes
            fieldType = HelperMethods.ParseNativeMethodSignature(f'(){fieldType}')[0] # create a fake signature and use it's return type
            fieldName = cls.constant_pool[f.name_index-1].bytes
            fields.append(f'field {fieldAccessFlags} {fieldType} {fieldName}')
        methods = []
        for m in cls.methods:
            methodAccessFlags = HelperMethods.AccessFlagToStr(m.access_flags, 'method')
            methodSig = cls.constant_pool[m.descriptor_index-1].bytes
            methodSig = HelperMethods.ParseNativeMethodSignature(methodSig)
            methodRet = methodSig[-1]
            methodArgs = ','.join(methodSig[0:-1])
            methodName = cls.constant_pool[m.name_index-1].bytes
            methods.append(f'method {methodAccessFlags} {methodRet} {methodName}({methodArgs})')
        
        print(f'Class (version={version}) {accessFlags} {className} extends {superClassName} implements [{implementsNames}]')
        print()
        for f in fields:
            print('\t' + f)
        if fields:
            print()
        for m in methods:
            print('\t' + m)
        
        
    @staticmethod
    def AccessFlagToStr(flag, type):
        
        assert type.lower() in ('class', 'field', 'method', 'nested class'), 'Unknown type'
        
        str = ''
        
        if type.lower() == 'class':
            if flag & 0x0001: str += 'ACC_PUBLIC, '
            if flag & 0x0010: str += 'ACC_FINAL, '
            if flag & 0x0020: str += 'ACC_SUPER, '
            if flag & 0x0200: str += 'ACC_INTERFACE, '
            if flag & 0x0400: str += 'ACC_ABSTRACT, '
            if flag & 0x1000: str += 'ACC_SYNTHETIC, '
            if flag & 0x2000: str += 'ACC_ANNOTATION, '
            if flag & 0x4000: str += 'ACC_ENUM, '
            return str.rstrip(', ')
        elif type.lower() == 'field':
            if flag & 0x0001: str += 'ACC_PUBLIC, '
            if flag & 0x0002: str += 'ACC_PRIVATE, '
            if flag & 0x0004: str += 'ACC_PROTECTED, '
            if flag & 0x0008: str += 'ACC_STATIC, '
            if flag & 0x0010: str += 'ACC_FINAL, '
            if flag & 0x0040: str += 'ACC_VOLATILE, '
            if flag & 0x0080: str += 'ACC_TRANSIENT, '
            if flag & 0x1000: str += 'ACC_SYNTHETIC, '
            if flag & 0x4000: str += 'ACC_ENUM, '
            return str.rstrip(', ')
        elif type.lower() == 'method':
            if flag & 0x0001: str += 'ACC_PUBLIC, '
            if flag & 0x0002: str += 'ACC_PRIVATE, '
            if flag & 0x0004: str += 'ACC_PROTECTED, '
            if flag & 0x0008: str += 'ACC_STATIC, '
            if flag & 0x0010: str += 'ACC_FINAL, '
            if flag & 0x0020: str += 'ACC_SYNCHRONIZED, '
            if flag & 0x0040: str += 'ACC_BRIDGE, '
            if flag & 0x0080: str += 'ACC_VARARGS, '
            if flag & 0x0100: str += 'ACC_NATIVE, '
            if flag & 0x0400: str += 'ACC_ABSTRACT, '
            if flag & 0x0800: str += 'ACC_STRICT, '
            if flag & 0x1000: str += 'ACC_SYNTHETIC, '
            return str.rstrip(', ')
        elif type.lower() == 'nested class':
            if flag & 0x0001: str += 'ACC_PUBLIC, '
            if flag & 0x0002: str += 'ACC_PRIVATE, '
            if flag & 0x0004: str += 'ACC_PROTECTED, '
            if flag & 0x0008: str += 'ACC_STATIC, '
            if flag & 0x0010: str += 'ACC_FINAL, '
            if flag & 0x0200: str += 'ACC_INTERFACE, '
            if flag & 0x0400: str += 'ACC_ABSTRACT, '
            if flag & 0x1000: str += 'ACC_SYNTHETIC, '
            if flag & 0x2000: str += 'ACC_ANNOTATION, '
            if flag & 0x0400: str += 'ACC_ENUM, '
            return str.trim.rstrip(', ')
    
    @staticmethod
    def BasicTypeToName(type):
        if type == 'B': return 'byte'
        elif type == 'C': return 'char'
        elif type == 'D': return 'double'
        elif type == 'F': return 'float'
        elif type == 'I': return 'int'
        elif type == 'J': return 'long'
        elif type == 'S': return 'short'
        elif type == 'Z': return 'boolean'
        elif type == 'V': return 'void'
        else: raise Exception(f'Unknown basic type {type}')
    
    @staticmethod
    def MajorClassVersionToJavaVersion(version):
        assert 45 <= version <= 58, 'unknown java version'
        return 'Java ' + str(version-45+1)
    
    
    @staticmethod
    def ParseNativeMethodSignature(name):
        ''' Parse a string like '(I[[JLjava/lang/Object;[[[Ljava/lang/Object;)V'
            into an array of type names (last element will be return type) '''
            
        import io
        
        ret = []
        nameStream = io.StringIO(name)
        char = nameStream.read(1) # ignore (
        
        while True:
            char = nameStream.read(1)
            if char == '':
                break
            if char == ')':
                continue # end of args, skip and process ret type
            arrayDimentions = 0
            while char == '[':
                arrayDimentions+=1
                char = nameStream.read(1)
                assert char != ''
            if char in ('B', 'C', 'D', 'F', 'I', 'J', 'S', 'Z', 'V'):
                ret.append(HelperMethods.BasicTypeToName(char)+('[]'*arrayDimentions))
                continue
            assert char == 'L', f'If not basic or array, type must be reference (L, not {char})'
            char = nameStream.read(1) # ignore L
            name = ''
            while char != ';':
                name+=char
                char = nameStream.read(1)
                assert char != ''
            ret.append(name+('[]'*arrayDimentions))
    
        return ret
    
    @staticmethod
    def PrintClassStrings(cls):
        assert isinstance(cls, ClassFile), 'cls must be a ClassFile'
        for cp_info in cls.constant_pool:
            if cp_info and cp_info.type == 'Utf8':
                print(cp_info)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} x.class')
        exit(1)

    cls = ClassFile(sys.argv[1])
    HelperMethods.PrintClassAndMemberInfo(cls)
    print('\n----')
    HelperMethods.PrintAttributeNames(cls)
