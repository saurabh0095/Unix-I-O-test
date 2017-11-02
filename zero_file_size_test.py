#!/usr/bin/python
# Objective: Analyze impact of "Delayed Allocation" in new file creation (ext4) 
# Author Karanjot Bhasin
#
# Process:
#  1. Contineously create a new file every second and write few bytes in it.
#  2. Crash to Linux by removing power cable
#  3. Check size of files created at step 1. At most one file should of size zero.
#     If more files of size zero is seen, they can be attributed to 'Delayed Allocation'
#     feature of ext4
#
# How to crash Linux in Hyper-V
#  Powershell:  Stop-VM -Name <VMName> -TurnOff
#
# Useful Reference
#  ext4 and data loss by Jonathan Corbet https://lwn.net/Articles/322823/
#  Linus Torvalds Upset over Ext3 and Ext4 http://www.linux-magazine.com/Online/News/Linus-Torvalds-Upset-over-Ext3-and-Ext4 


import os, time
sleep_time = 1         # Interval between file creation
max_file_count = 3600

def create_file(newFileName):        
        newFileDiscriptor = os.open(newFileName, os.O_RDWR|os.O_CREAT)
        os.write(newFileDiscriptor, "File Created successfuly \n")
        os.close(newFileDiscriptor)

def create_file_loop():
        timeStamp =  int(time.time()) #Time when script starts up (at system boot)
        newDirName = "zero_file_size_test_%s" %(timeStamp)
        os.mkdir(newDirName)

        print "Starting creation of files after every %d seconds in %s" %(sleep_time, newDirName)
        for counter in range(1, max_file_count+1):
                newFileName = "%s/file_%d.txt" %(newDirName, counter)
                create_file(newFileName)
                time.sleep(sleep_time)
        print "File creation completed"

if __name__ == "__main__":
        create_file_loop()