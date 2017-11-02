#!/bin/python
#
# Objective : Measure I/O performance for different journaling options
#             Four different types of writes were performed for validation
#             from sequential to random write on new and existing file.
# Author    : Saurabh Banerjee
# Usage     :
#            $ ./<scriptName> <filename to write> <filesize in bytes> <pattern to write>
#

import time
import os, sys
import subprocess
import random

blocksize = 4*1024
multi_round_count=10

#create dictionary for use in csv
keys = ['mode', 'File_write_time', 'File_sync_time']
stats_list = {"mode":[],"File_write_time":[],"File_sync_time":[]}

#file write function
#mode 0 is writing on new file 
#mode 1 is writing on existing file 
#mode 2 is writing multiple times on existing file 
#mode 3 is writing randomly on existing file 
def writer(filename,filesize,write_pattern,mode_write):
	write_pattern_size= len(write_pattern)
        blockcount = (int(filesize)) /blocksize
        lseek_shift_1 = blocksize - write_pattern_size
	mode=mode_write

        if mode == 0:
		if os.path.exists(filename):
            		os.remove(filename)
		fo = os.open(filename, os.O_RDWR|os.O_CREAT )
        else: 
        	fo = os.open(filename, os.O_RDWR )
	
	w_start= time.time()	
	#sequential write on new file
	#sequential_write on existing file 
        if mode == 0 or mode == 1:
                for x in xrange(blockcount):
                        os.write(fo,write_pattern)
                        os.lseek(fo, lseek_shift_1, 1)
        #sequential_multi write
        elif mode == 2:
        	for y in xrange(multi_round_count):
                	for x in xrange(blockcount/multi_round_count):
                        	os.write(fo,write_pattern)
                        	os.lseek(fo, lseek_shift_1, 1)
                	os.lseek(fo, 0, 0)
        #random write
        else:
                for x in xrange(blockcount):
                        random_num=random.randint(0,blockcount-1)
                        lseek_shift_1 = random_num*blocksize
                        os.write(fo,write_pattern + str(random_num))
                        os.lseek(fo, lseek_shift_1, 0)

	file_write_time = int((time.time()-w_start)*1000000)
	stats_list["File_write_time"].append(file_write_time)

	sync_start = time.time()
	os.fsync(fo)
	sync_time = int((time.time()-sync_start)*1000000)
	stats_list["File_sync_time"].append(sync_time)
	stats_list["mode"].append(mode)
	
	os.close(fo)

def print_statistics():
	header = stats_list.keys()
	no_rows = len(stats_list[list(header)[0]])
	stat_file = 'write_stats_%d.csv' % (os.getpid())
        fo = open(stat_file, "w+")

	for h in keys:
		fo.write("%s,"%(h))
		for x in xrange(no_rows):
			fo.write("%s,"%(stats_list[h][x]))
		fo.write("\n")
	fo.close()
	print "Created file: ", stat_file, " with statistics of the run"


def start_func():
	if len(sys.argv) != 4:
                print "Incorrect usage.\n\tUse as: " + sys.argv[0] + " <filename to write> <filesize in bytes> <pattern to write>"
                quit()
        filename=sys.argv[1]
        filesize=sys.argv[2] 
        write_pattern=sys.argv[3]
	print "Name of the file : %s of size : %s" %(filename, filesize)
        print "Pattern : %s will be written in every block of %s file" %(write_pattern, filename)
        writer(filename,filesize,write_pattern,0)
        writer(filename,filesize,write_pattern,1)
        writer(filename,filesize,write_pattern,2)
        writer(filename,filesize,write_pattern,3)
	print_statistics()

if  __name__ =='__main__':
        start_func()

