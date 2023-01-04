import os, sys, struct
import zlib # for crc calculation

# Written by Chippy

# RKV1
# file entries come before directory entries
# go to directory entries by adding file entry array size to file entry offset

# common functions to read from binary file

def read_byte_big(fd):
    return struct.unpack('>b', fd.read(1))[0]
    
def read_short_big(fd):
    return struct.unpack('>h', fd.read(2))[0]

def read_int_big(fd):
    return struct.unpack('>i', fd.read(4))[0]

def read_uint_big(fd):
    return struct.unpack('>I', fd.read(4))[0]

def read_byte_little(fd):
    return struct.unpack('<b', fd.read(1))[0]
    
def read_short_little(fd):
    return struct.unpack('<h', fd.read(2))[0]

def read_int_little(fd):
    return struct.unpack('<i', fd.read(4))[0]

def read_uint_little(fd):
    return struct.unpack('<I', fd.read(4))[0]

def read_string(fd):
    res = ''
    byte = fd.read(1)
    while byte != b'\x00':
        res += (byte.decode('ascii'))
        byte = fd.read(1)
    return res

def read_string_len(fd, len):
    res = ''
    while len != 0:
        byte = fd.read(1)
        res += (byte.decode('ascii'))
        len -= 1
    return res

# end common functions

def dump_filenames(fd, outFd):
    fd.seek(0, 2) # go to end of the file
    fileSize = fd.tell()
    #print(fileSize)
    fd.seek(-0x20, 2) # go header from end of the file
    fd.seek(0x18, 1) # go to entry count address
    nmbrOfEntries = read_int_little(fd) # read entry count
    nmbrOfDirectories = read_int_little(fd) # read directory count
    
    entryLength = nmbrOfEntries * 0x40 + nmbrOfDirectories * 0x100
    #print(entryLength)
    entryDataStartOffset = fileSize - (entryLength + 8)
    
    currEntryOffset = entryDataStartOffset
    print(entryDataStartOffset)
    fd.seek(entryDataStartOffset, 0)
    
    i = 0
    for i in range(nmbrOfEntries):
        fileName = read_string(fd)
        outFd.write(fileName + '\n')
        currEntryOffset += 0x40
        fd.seek(currEntryOffset, 0)
    
#end of dump_filenames

def dump_filenames_RKV2(fd, outFd):
    #RKV2 file entry size is 0x14
    fd.seek(4, 0) # seek to file entry count
    nmbrOfEntries = read_int_little(fd) # read entry count
    print(nmbrOfEntries)
    entryNameLength = read_int_little(fd) # read name length
    unused = read_int_little(fd)
    unused = read_int_little(fd)
    entryOffset = read_int_little(fd)
    stringTableOffset = entryOffset + (nmbrOfEntries * 0x14)
    
    currEntryOffset = entryOffset
    fd.seek(entryOffset, 0) # seek to first entry
    print(entryOffset)
    i = 0
    for i in range(nmbrOfEntries):
        fileNameAddr = read_int_little(fd) # read string offset
        #print(fileNameAddr)
        fd.seek(stringTableOffset + fileNameAddr, 0)
        fileName = read_string(fd)
        outFd.write(fileName + '\n')
        currEntryOffset += 0x14
        fd.seek(currEntryOffset, 0)
    
#end of dump_filenames_RKV2

# this function prints the directory of the file after the file in filelist.txt
def dump_filenames_directories(fd, outFd):
    fd.seek(0, 2) # go to end of the file
    fileSize = fd.tell()
    #print(fileSize)
    fd.seek(-0x20, 2) # go header from end of the file
    fd.seek(0x18, 1) # go to entry count address
    nmbrOfEntries = read_int_little(fd) # read entry count
    nmbrOfDirectories = read_int_little(fd) # read directory count

    entryLength = nmbrOfEntries * 0x40 + nmbrOfDirectories * 0x100
    #print(entryLength)
    entryDataStartOffset = fileSize - (entryLength + 8)

    directoryEntryOffset = entryDataStartOffset + (nmbrOfEntries * 0x40)
    currEntryOffset = entryDataStartOffset
    print(entryDataStartOffset)
    fd.seek(entryDataStartOffset, 0)

    i = 0
    for i in range(nmbrOfEntries):
        fileName = read_string(fd)
        fd.seek(currEntryOffset, 0)
        fd.seek(0x20, 1)
        dirIdx = read_int_little(fd)
        fd.seek(directoryEntryOffset + (dirIdx * 0x100), 0)
        outFd.write(fileName + ' ' + read_string(fd) + '\n')
        currEntryOffset += 0x40
        fd.seek(currEntryOffset, 0)

#end of dump_filenames_directories

def dump_directories(fd, outFd):
    fd.seek(0, 2) # go to end of the file
    fileSize = fd.tell()
    print(fileSize)
    fd.seek(-0x20, 2) # go header from end of the file
    fd.seek(0x18, 1) # go to entry count address
    nmbrOfEntries = read_int_little(fd) # read entry count
    nmbrOfDirectories = read_int_little(fd) # read directory count
    
    entryLength = nmbrOfEntries * 0x40 + nmbrOfDirectories * 0x100
    print(entryLength)
    entryDataStartOffset = fileSize - (entryLength + 8)
    
    directoryEntryOffset = entryDataStartOffset + (nmbrOfEntries * 0x40)
    print(entryDataStartOffset + (nmbrOfEntries * 0x40)) # print offset of directory entries
    fd.seek(directoryEntryOffset, 0)
    
    i = 0
    for i in range(nmbrOfDirectories):
        fileName = read_string(fd)
        outFd.write(fileName + '\n')
        directoryEntryOffset += 0x100
        fd.seek(directoryEntryOffset, 0)
    
#end of dump_directories

def find_FileEntry(fd, filename):
    fd.seek(0, 2) # go to end of the file
    fileSize = fd.tell()
    #print(fileSize)
    #print(fd, fileSize)
    fd.seek(-0x20, 2) # go header from end of the file
    fd.seek(0x18, 1) # go to entry count address
    nmbrOfEntries = read_int_little(fd) # read entry count
    nmbrOfDirectories = read_int_little(fd) # read directory count
    
    entryLength = nmbrOfEntries * 0x40 + nmbrOfDirectories * 0x100
    #print(entryLength)
    entryDataStartOffset = fileSize - (entryLength + 8)
    
    currEntryOffset = entryDataStartOffset
    print(entryDataStartOffset)
    fd.seek(entryDataStartOffset, 0)
    
    i = 0
    for i in range(nmbrOfEntries):
        if read_string(fd) == filename:
            return currEntryOffset # if the name is the same as the entry name, return the entry offset
        
        currEntryOffset += 0x40
        fd.seek(currEntryOffset, 0)
    
    return 0 # return 0 if the file doesn't exist

#end of find_FileEntry

def find_FileEntry_RKV2(fd, filename):
    #RKV2 file entry size is 0x14
    fd.seek(4, 0) # seek to file entry count
    nmbrOfEntries = read_int_little(fd) # read entry count
    print(nmbrOfEntries)
    entryNameLength = read_int_little(fd) # read name length
    unused = read_int_little(fd)
    unused = read_int_little(fd)
    entryOffset = read_int_little(fd)
    stringTableOffset = entryOffset + (nmbrOfEntries * 0x14)
    
    currEntryOffset = entryOffset
    fd.seek(entryOffset, 0) # seek to first entry
    print(entryOffset)
    i = 0
    for i in range(nmbrOfEntries):
        fileNameAddr = read_int_little(fd) # read string offset
        #print(fileNameAddr)
        fd.seek(stringTableOffset + fileNameAddr, 0)
        if read_string(fd) == filename:
            return currEntryOffset
        
        currEntryOffset += 0x14
        fd.seek(currEntryOffset, 0)
     
    return 0 # return 0 if the file doesn't exist

#end of find_FileEntry_RKV2

# function to extract file from RKV1
def ExtractFile(fd, filename):
    entryOffset = find_FileEntry(fd, filename)
    print(entryOffset)
    if entryOffset != 0:
        file_name = os.path.dirname(sys.argv[0]) + "\%s" % filename
        print(file_name)
        fd.seek(entryOffset, 0) # seek to entry from beginning of the file
        fd.seek(0x24, 1) # seek to file data length
        dataLength = read_int_little(fd)
        if dataLength != 0 or dataLength != -1: # is it possible to have a length of 0xFFFFFFFF?
            fd.seek(entryOffset, 0)
            fd.seek(0x2C, 1) # seek to data offset value
            dataOffset = read_int_little(fd)
            if dataOffset != -1:
                print(dataOffset, dataLength)
                fd.seek(dataOffset, 0) # seek to beginning of data
                filedata = fd.read(dataLength)
                calculatedChecksum = zlib.crc32(filedata)
                fd.seek(entryOffset, 0) # seek to beginning of entry
                fd.seek(0x30, 1) # seek to crc value of file
                if read_uint_little(fd) != calculatedChecksum:
                    print("Bad Dump!\nCRC does not match!")
                outFile = open(file_name, "w+b")
                outFile.write(filedata)
                outFile.close() # close file
            else:
                print("Bad File Offset for %s" % file_name)
        else:
            print("Bad File Length for %s" % file_name)
    else:
        print("%s not found" % filename)

#end of ExtractFile

# function to extract file from RKV2
def ExtractFile_RKV2(fd, filename):
    entryOffset = find_FileEntry_RKV2(fd, filename)
    print(entryOffset)
    if entryOffset != 0:
        file_name = os.path.dirname(sys.argv[0]) + "\%s" % filename
        print(file_name)
        fd.seek(entryOffset, 0) # seek to entry from beginning of the file
        fd.seek(0x8, 1) # seek to file data length
        dataLength = read_int_little(fd)
        if dataLength != 0 or dataLength != -1: # is it possible to have a length of 0xFFFFFFFF?
            fd.seek(entryOffset, 0)
            fd.seek(0xC, 1) # seek to data offset value
            dataOffset = read_int_little(fd)
            if dataOffset != -1:
                print(dataOffset, dataLength)
                fd.seek(dataOffset, 0) # seek to beginning of data
                filedata = fd.read(dataLength)
                calculatedChecksum = zlib.crc32(filedata)
                fd.seek(entryOffset, 0) # seek to beginning of entry
                fd.seek(0x10, 1) # seek to crc value of file
                if read_uint_little(fd) != calculatedChecksum:
                    print("Bad Dump!\nCRC does not match!")
                outFile = open(file_name, "w+b")
                outFile.write(filedata)
                outFile.close() # close file
            else:
                print("Bad File Offset for %s" % file_name)
        else:
            print("Bad File Length for %s" % file_name)
    else:
        print("%s not found" % filename)

#end of ExtractFile_RKV2

def main():
    args = sys.argv[1:] # remove first argument which is always the path to this python file
    
    if len(args) == 0:
        print("Usage:\nRKV Path required as first arg\nOptional:\n'-dumpNames' dumps a list of all files\n'-extract %s' extracts a given file\n'-dumpDirectories' dumps a list of directories")
        return
    
    rkvPath = args[0] # get RKV path
    print(rkvPath)
    
    rkvFd = open(rkvPath, "rb") # open RKV
    
    if read_int_big(rkvFd) == 0x524B5632: # "RKV2"
        # if the RKV is an RKV2
        # only allow for file name dumping currently
        if len(args) > 1 and args[1] == "-dumpNames":
            # extension should be the last data within path
            splitPath = rkvPath.split("\\")[-1].split(".")[0] # include archive's name in fileList file name
            fileList = os.path.dirname(sys.argv[0]) + "\\" + splitPath + "_fileList.txt"
            listFd = open(fileList, "w")
            print("RKV2!")
            dump_filenames_RKV2(rkvFd, listFd)
            listFd.close() # close list file
            
        if len(args) > 2 and args[1] == "-extract":
            ExtractFile_RKV2(rkvFd, args[2])
    else:
        if len(args) > 1 and args[1] == "-dumpNames":
            # extension should be the last data within path
            splitPath = rkvPath.split("\\")[-1].split(".")[0] # include archive's name in fileList file name
            fileList = os.path.dirname(sys.argv[0]) + "\\" + splitPath + "_fileList.txt"
            listFd = open(fileList, "w")
            rkvFd.seek(0, 0)
            dump_filenames(rkvFd, listFd)
            listFd.close() # close list file
        
        if len(args) > 1 and args[1] == "-dumpDirectories":
            directoryList = os.path.dirname(sys.argv[0]) + "\\directoryList.txt"
            listFd = open(directoryList, "w")
            dump_directories(rkvFd, listFd)
            listFd.close() # close list file
    
        if len(args) > 2 and args[1] == "-extract":
            ExtractFile(rkvFd, args[2])
    
    rkvFd.close() # close RKV
    
#end of main

if __name__ == "__main__":
    main()