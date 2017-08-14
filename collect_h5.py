#recommended module versions
#h5py==2.5.0
#numpy==1.10.4
#scipy==0.17.0


import numpy
import h5py

import sys #-> argv
import os #-> file checks
import getopt #-> input parameters

########################################################## ARGUMENT PROCESSING

#--------------------------------------------------- USAGE
def usage():
	print(str(sys.argv[0])+" -d <dir>")
	print("collect .h5 files from a directory into a single .h5 file.")
	print("options:")
	print("-h --help")
	print("-d --dir")

#--------------------------------------------------- GETOPTS

try:
	(opts, args) = getopt.getopt(sys.argv[1:], "hd:", ["help","dir="])
except getopt.GetoptError:
	usage()
	sys.exit(1)

#--------------------------------------------------- NO OPTIONS -> NOTHING TO DO
if opts.__len__()==0:
	usage()
	sys.exit()

inputdir=""

for (opt, arg) in opts:
#--------------------------------------------------- PRINT USAGE
	if opt in ("-h","--help"):
		usage()
		sys.exit()
#--------------------------------------------------- SPECIFY RUNFILE
	elif opt in ("-d", "--dir"):
		if os.path.exists(arg) and os.path.isdir(arg):
			inputdir=arg
		else:
			print("error: inputdir does not exist.")
			sys.exit(1)
#--------------------------------------------------- SOMETHING WENT REALLY WRONG
	else:
		print("error: unexpected option")
		sys.exit(1)


#---------------------------------------------------- TEST IF OUTFILE CAN BE CREATED

outputfile=inputdir+".h5"
if os.path.exists(outputfile):
	print("error: "+outputfile+" already exists.")
	sys.exit(1)

########################################################## MAIN

#---------------------------------------------------- FIND ALL .h5 FILES IN DIR
dirfiles = [path for path in os.listdir(inputdir) if os.path.isfile(inputdir+"/"+path)]

#---------------------------------------------------- CREATE OUTPUT FILE
output_FILE=h5py.File(outputfile,'w')

#---------------------------------------------------- COPY ALL .h5 FILES FROM DIR INTO FILE
for file in dirfiles:
	if file.split(".")[-1]=="h5":
		print("copied: "+file)
		output_FILE.create_group(file.split(".h5")[0])
		sub_FILE=h5py.File(inputdir+"/"+file,'r')
		for key in sub_FILE:
			sub_FILE.copy(key,output_FILE[file.split(".h5")[0]])
		sub_FILE.close()
#---------------------------------------------------- WRITE AND CLOSE
output_FILE.flush()
output_FILE.close()

