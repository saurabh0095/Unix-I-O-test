#!/bin/python
#
# Objective	:This will check the latency of write for various values of dirty pages.
# Author	:Saurabh Banerjee
# Usage		:
#   		 $ ./<scriptName>  <filename to write>  <pattern to write>
#


import time
import os, sys
import subprocess

blocksize = 4*1024
min_dirty_bytes_size = 8*1024 # Minimum size supported in Linux

# Create dictionary for use in csv
keys = ['Set_dirty_bytes', 'dirty_bytes', 'File_write_time', 'File_sync_time', 'nr_dirty']
stats_list = {"Set_dirty_bytes":[],"dirty_bytes":[],"File_write_time":[],"File_sync_time":[],"nr_dirty":[]}


# File writer function
def write_pattern2file(filename, filesize, write_pattern):
	write_pattern_size= len(write_pattern)
	blockcount = (filesize) /blocksize
	lseek_shift_1 = blocksize - write_pattern_size
	fo = os.open(filename, os.O_RDWR)
			
	#Write pattern in every block of the file	
	write_start= time.time()
	for x in xrange(blockcount):
		os.write(fo,write_pattern)
		os.lseek(fo, lseek_shift_1, 1)
	file_write_time = int((time.time() - write_start)*1000000)
	stats_list["File_write_time"].append(file_write_time)
	
	# Retrive dirty pages in the system
	nr_dirty = ((subprocess.check_output('grep "dirty " /proc/vmstat', shell=True)).strip('\n')).split(' ',1)
	stats_list["nr_dirty"].append(nr_dirty[1])
    
	# Capture fsync time. fsync is called once after end of all writes in the file.
	sync_start = time.time()
	os.fsync(fo)
	sync_time = int((time.time()-sync_start)*1000000)
	stats_list["File_sync_time"].append(sync_time)
	
	os.close(fo)


def dirty_bytes_setup(dirty_bytes):
	# Set dirty_bytes in the system
	stats_list["Set_dirty_bytes"].append(dirty_bytes)
	subprocess.check_output('sysctl vm.dirty_bytes={}'.format(dirty_bytes), shell=True)
	# Check by retriving dirty_bytes from the system
	for line in open("/proc/sys/vm/dirty_bytes"):
		dirty_bytes_set = line.strip('\n')
	stats_list["dirty_bytes"].append(dirty_bytes_set)	

def print_statistics():
	header = stats_list.keys()
	no_rows = len(stats_list[list(header)[0]])

	stat_file = 'statistics_%d.csv' % (os.getpid())
	fo = open(stat_file, "w+")
	keys_unit = ['Set_dirty_bytes(b)', 'dirty_bytes(b)', 'File_write_time(us)', 'File_sync_time(us)', 'nr_dirty(page)']
	for k in keys_unit:
		fo.write("%s,"%k)
	fo.write("\n")

	for x in xrange(no_rows):
		for h in keys:
			fo.write("%s,"%(stats_list[h][x]))
		fo.write("\n") # New line after each row
	fo.close()
	print "Created file: ", stat_file, " with statistics of the run"

def start_func():
	if len(sys.argv) != 3:
                print "Incorrect usage.\n\tUse as: " + sys.argv[0] + " <filename to write> <pattern to write>"
                quit()
	filename=sys.argv[1]
	write_pattern=sys.argv[2]
	filesize = int(os.path.getsize(filename))
	print "Name of the file : %s of size : %s" %(filename, filesize)
	print "Pattern : %s will be written in every block of %s file" %(write_pattern, filename)

	dirty_bytes_size = min_dirty_bytes_size
	while ( dirty_bytes_size <= filesize ):
		dirty_bytes_setup(dirty_bytes_size)
		write_pattern2file(filename, filesize, write_pattern)
		dirty_bytes_size = dirty_bytes_size*2
	print_statistics()

if  __name__ =='__main__':
	start_func()

