# Rkv-Extractor
 A python program to extract files from Merkury Archives (RKV)
 
 This does not support writing files or building RKVs yet, just extracting files from them
 
 Extracted files are currently placed in the folder of the program
 
# Usage
 RKV path is required as the first argument

 '-dumpNames' creates a file that lists all files within the RKV
 
 '-extract %s' extracts a given file based on the name to the folder of the python program
 
 '-dumpDirectories' creates a file that lists all directories within the RKV
 
 python RkvExtractor.py Data_GC.rkv -extract z1.lv2