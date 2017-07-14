####!/usr/bin/python

import numpy
import h5py

import sys #-> argv
import os #-> file checks
import getopt #-> input parameters

########################################################## USAGE

#--------------------------------------------------- USAGE
def usage():
	print(str(sys.argv[0])+" -1 <streamh5file1> -r <runfile> -o <outputfile.lst>")
	print("extracts all filenames of indexed images from <runfile> given indexing result from <streamh5file1> and writes them to <outputfile>.")
	print("options:")
	print("-h --help")
	print("-1 --streamh5file1")
	print("-r --runfile")
	print("-o --outputfile")

#--------------------------------------------------- GETOPTS

try:
	(opts, args) = getopt.getopt(sys.argv[1:], "h1:r:o:", ["help","streamh5file1=","runfile=","outputfile="])
except getopt.GetoptError:
	usage()
	sys.exit(1)

#--------------------------------------------------- NO OPTIONS -> NOTHING TO DO
if opts.__len__()==0:
	usage()
	sys.exit()
#################################################### INPUT ARG VARIABLES
streamh5file1=""
runfile=""
outputfile=""

#################################################### ARGUMENT PROCESSING
for (opt, arg) in opts:
#--------------------------------------------------- PRINT USAGE
	if opt in ("-h","--help"):
		usage()
		sys.exit()
#--------------------------------------------------- SPECIFY STREAMFILE
	elif opt in ("-1", "--streamh5file1"):
		if os.path.isfile(arg) and (arg.split(".")[-2:] == ["stream","h5"]):
			streamh5file1=arg
		else:
			print("error: streamh5file1 does not exist or is not a .stream.h5 file.")
			sys.exit(1)
#--------------------------------------------------- SPECIFY RUNFILE
	elif opt in ("-r", "--runfile"):
		if os.path.isfile(arg) and (arg.split(".")[-1] == "h5"):
			runfile=arg
		else:
			print("error: runfile does not exist or is not a .h5 file.")
			sys.exit(1)
#--------------------------------------------------- SPECIFY OUTPUTFILE
	elif opt in ("-o", "--outputfile"):
		if (not os.path.isfile(arg)) and (arg.split(".")[-1] == "lst"):
			outputfile=arg
		else:
			print("error: outputfile already exist or is not a .lst file.")
			sys.exit(1)
#--------------------------------------------------- SOMETHING WENT REALLY WRONG
	else:
		print("error: unexpected option")
		sys.exit(1)

##################################################### ARGUMENT CHECKS
#---------------------------------------------------- CHECK FOR DUPLICATES
if "" in (streamh5file1,runfile,outputfile):
	print("error: one or multiple files missing.")
	usage()
	sys.exit(1)
elif streamh5file1 in (runfile,outputfile):
	print("error: duplicate filenames.")
	print(streamh5file1 +" "+runfile+" "+outpufile)
	sys.exit(1)


########################################################## MAIN

#------------------------------------------------------- RETRIEVE THE INDEXING STATUS OF IMAGES
streamh5file1_FD= h5py.File(streamh5file1,'r')

indexedby=streamh5file1_FD['/CHUNK/indexed_by'][:]
imagefilenames=streamh5file1_FD['/CHUNK/image_filename'][:]

streamh5file1_FD.close()
#------------------------------------------------------- WRITE THE NAMES OF INDEXED IMAGES
outputfile_FD=open(outputfile,'w')

for (indexedFLAG,imagefilename) in zip(indexedby,imagefilenames):
	if not "none" in indexedFLAG:
		outputfile_FD.write(imagefilename+"\n")

outputfile_FD.close()
