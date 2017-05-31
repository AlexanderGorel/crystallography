#####!/usr/bin/python

import numpy
import h5py

import sys #-> argv
import os #-> file checks
import getopt #-> input parameters

########################################################## USAGE

#--------------------------------------------------- USAGE
def usage():
	print(str(sys.argv[0])+" -1 <streamh5file1> -2 <streamh5file2> -o <h5outputpath> [-v]")
	print("subtract reflections in <streamh5file2> from peaks in <streamh5file1> which are in vicinity of 10pix and write these at <h5outputpath> into the respective .h5 files.")
	print("options:")
	print("-h --help")
	print("-1 --streamh5file1")
	print("-2 --streamh5file2")
	print("-o --h5outputpath")
	print("-v --verbose")

#--------------------------------------------------- GETOPTS

try:
	(opts, args) = getopt.getopt(sys.argv[1:], "h1:2:o:v", ["help","streamh5file1=","streamh5file2=","h5outputpath=","verbose"])
except getopt.GetoptError:
	usage()
	sys.exit(1)

#--------------------------------------------------- NO OPTIONS -> NOTHING TO DO
if opts.__len__()==0:
	usage()
	sys.exit()
########################################################## INPUT ARG VARIABLES
streamh5file1=""
streamh5file2=""
h5outputpath=""
verboseFLAG=False

########################################################## ARGUMENT PROCESSING
for (opt, arg) in opts:
#--------------------------------------------------- PRINT USAGE
	if opt in ("-h","--help"):
		usage()
		sys.exit()
#--------------------------------------------------- SPECIFY STREAMH5FILE1
	elif opt in ("-1", "--streamh5file1"):
		if os.path.isfile(arg) and (arg.split(".")[-2:] == ["stream","h5"]):
			streamh5file1=arg
		else:
			print("error: streamh5file1 does not exist or is not a .stream.h5 file.")
			sys.exit(1)
#--------------------------------------------------- SPECIFY STREAMH5FILE2
	elif opt in ("-2", "--streamh5file2"):
		if os.path.isfile(arg) and (arg.split(".")[-2:] == ["stream","h5"]):
			streamh5file2=arg
		else:
			print("error: streamh5file2 does not exist or is not a .stream.h5 file.")
			sys.exit(1)
#--------------------------------------------------- SPECIFY H5OUTPUTPATH
	elif opt in ("-o", "--h5outputpath"):
		h5outputpath=arg
#--------------------------------------------------- SPECIFY H5OUTPUTPATH
	elif opt in ("-v", "--verbose"):
		verboseFLAG=True
#--------------------------------------------------- SOMETHING WENT REALLY WRONG
	else:
		print("error: unexpected option")
		sys.exit(1)
######################################################### ARGUMENT CHECKS
#---------------------------------------------------- CHECK FOR DUPLICATES
if "" in (streamh5file1,streamh5file2,h5outputpath):
	print("error: one or multiple argument missing.")
	usage()
	sys.exit(1)
elif streamh5file1 == streamh5file2:
	print("error: duplicate filenames.")
	print(streamh5file1 +" "+streamh5file2)
	sys.exit(1)

########################################################## USEFUL FUNCTIONS
#------------------------------------------------------------ HELPER FUNCTION TO CALCULATE THE DISTANCE TO CLOSEST POINT FROM LIST

def dist_of_nearest(**kwargs):
	"""args: point_, points_ """
	distances=numpy.array([numpy.sqrt(numpy.dot(x-kwargs["point_"],x-kwargs["point_"])) for x in kwargs["points_"]])
	return distances.min()

########################################################## MAIN
#------------------------------------------------------------ OPEN THE FILES WITH THE INFORMATION
streamh5file1_FD=h5py.File(streamh5file1,'r')
streamh5file2_FD=h5py.File(streamh5file2,'r')

#------------------------------------------------------------ GET THE PEAKS FROM THE STREAM
streamh5file1_imagefilenames=streamh5file1_FD['/CHUNK/image_filename'][:]
streamh5file1_points=[zip(fs_idx[:],ss_idx[:]) for (fs_idx,ss_idx) in zip(streamh5file1_FD['/PEAK/fs'],streamh5file1_FD['/PEAK/ss'])]
streamh5file1_file_points_DICT=dict(zip(streamh5file1_imagefilenames,streamh5file1_points))

#------------------------------------------------------------ GET THE NAME OF THE INDEXED FILES
streamh5file2_imagefilenames=streamh5file2_FD['/CHUNK/image_filename'][:]
streamh5file2_indexedby=streamh5file2_FD['/CHUNK/indexed_by'][:]
streamh5file2_file_indexed_DICT=dict(zip(streamh5file2_imagefilenames,streamh5file2_indexedby))
streamh5file2_indexed_imagefilenames=filter(lambda x: streamh5file2_file_indexed_DICT[x]!="none",streamh5file2_imagefilenames)

#------------------------------------------------------------ GET THE REFLECTIONS TO SUBTRACT
streamh5file2_points=[zip(fs_idx[:],ss_idx[:]) for (fs_idx,ss_idx) in zip(streamh5file2_FD['/REFLECTION/fs'],streamh5file2_FD['/REFLECTION/ss'])]
streamh5file2_file_points_DICT=dict(zip(streamh5file2_imagefilenames,streamh5file2_points))

#------------------------------------------------------------ CLOSE THE FILES
streamh5file1_FD.close()
streamh5file2_FD.close()

#------------------------------------------------------------ SUBTRACT THE REFLECTIONS FROM THE PEAKS

for imagefilename in streamh5file1_imagefilenames:
	if imagefilename in streamh5file2_indexed_imagefilenames:
		if verboseFLAG:print(imagefilename)
		tmp_FD=h5py.File(imagefilename,'a')
		if h5outputpath in tmp_FD:
			del tmp_FD[h5outputpath]
#------------------------------------------------------------ WRITE THE PEAKS WHICH ARE MORE THAN 10 PIX AWAY FROM THE REFLECTIONS
		tmp_FD[h5outputpath]=numpy.array([(numpy.round(fs),numpy.round(ss),100.) for (fs,ss) in filter(lambda x: dist_of_nearest(point_=numpy.array(x),points_=streamh5file2_file_points_DICT[imagefilename])>10,streamh5file1_file_points_DICT[imagefilename])])
		tmp_FD.flush()
		tmp_FD.close()


