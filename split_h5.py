####!/usr/bin/python

import numpy
import h5py

import sys #-> argv
import os #-> file checks
import getopt #-> input parameters

########################################################## ARGUMENT PROCESSING

#--------------------------------------------------- USAGE
def usage():
	print(str(sys.argv[0])+" -i <h5file>")
	print("split the .h5 file into a directory with subfiles")
	print("options:")
	print("-h --help")
	print("-i --inputfile")

#--------------------------------------------------- GETOPTS

try:
	(opts, args) = getopt.getopt(sys.argv[1:], "hi:", ["help","inputfile="])
except getopt.GetoptError:
	usage()
	sys.exit(1)

#--------------------------------------------------- NO OPTIONS -> NOTHING TO DO
if opts.__len__()==0:
	usage()
	sys.exit()

inputfile=""

for (opt, arg) in opts:
#--------------------------------------------------- PRINT USAGE
	if opt in ("-h","--help"):
		usage()
		sys.exit()
#--------------------------------------------------- SPECIFY RUNFILE
	elif opt in ("-i", "--inputfile"):
		if os.path.isfile(arg) and (arg.split(".")[-1] == "h5"):
			inputfile=arg
		else:
			print("error: inputfile does not exist or is not a .h5 file.")
			sys.exit(1)
#--------------------------------------------------- SOMETHING WENT REALLY WRONG
	else:
		print("error: unexpected option")
		sys.exit(1)


#---------------------------------------------------- TEST IF OUTFILE CAN BE CREATED

outputdir=inputfile.split(".h5")[0]

if os.path.exists(outputdir):
	print("error: "+outputdir+" already exists.")
	sys.exit(1)

#---------------------------------------------------- CHECK FOR DUPLICATES
if "" in (inputfile,outputdir):
	print("error: one or multiple files missing.")
	usage()
	sys.exit(1)


os.makedirs(outputdir)
if not os.path.exists(outputdir):
	print("error: directory "+outputdir+" could not be created.")

########################################################## MAIN

input_FILE=h5py.File(inputfile,'r')

for key in input_FILE:
	if input_FILE[key].__class__.__name__ == 'Group':
		sub_FILE=h5py.File(outputdir+"/"+str(key)+".h5",'w')
		for subkey in input_FILE[key]:
			input_FILE[key].copy(subkey,sub_FILE)
		sub_FILE.flush()
		sub_FILE.close()
		print("copied: "+str(key))

input_FILE.close()

