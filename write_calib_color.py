
import numpy
import h5py

import sys #-> argv
import os #-> file checks
import getopt #-> input parameters

########################################################## HELPER FUNCTIONS
#--------------------------------------------------- IMPORT LIST FROM FILE
def ImportList(**kwargs):
#-------------------------------------------------- read text from file
	file_FD=open(kwargs["file_"],'r')
	txt=file_FD.read()
	file_FD.close()
#--------------------------------------------------- split text into lines
	lines=txt.split("\n")
	trimmed_lines=[line.strip() for line in lines]
	return trimmed_lines

########################################################## ARGUMENT PROCESSING

#--------------------------------------------------- USAGE
def usage():
	print(str(sys.argv[0])+" -l <filelist.lst> -s <file.spectrum.h5>[-v]")
	print("write the color energies from <file.spectrum.h5> into each .h5 file in filelist.lst")
	print("options:")
	print("-h --help")
	print("-l --filelist")
	print("-s --spectrumfile")
	print("-v --verbose")

#--------------------------------------------------- GETOPTS

try:
	(opts, args) = getopt.getopt(sys.argv[1:], "hl:s:v", ["help","filelist=","spectrumfile=","verbose"])
except getopt.GetoptError:
	usage()
	sys.exit(1)

#--------------------------------------------------- NO OPTIONS -> NOTHING TO DO
if opts.__len__()==0:
	usage()
	sys.exit()
#################################################### ARGUMENT VARIABLES
filelist=""
spectrumfile=""
verboseFLAG=False

#################################################### ARGUMENT PARSING
for (opt, arg) in opts:
#--------------------------------------------------- PRINT USAGE
	if opt in ("-h","--help"):
		usage()
		sys.exit()
#--------------------------------------------------- SPECIFY FILELIST
	elif opt in ("-l", "--filelist"):
		if os.path.isfile(arg) and (arg.split(".")[-1] == "lst"):
			filelist=arg
		else:
			print("error: filelist does not exist or is not a .lst file.")
			sys.exit(1)
#--------------------------------------------------- SPECIFY FILE WITH SPECTRA
	elif opt in ("-s", "--spectrumfile"):
		if os.path.isfile(arg) and (arg.split(".")[-2:] == ["spectra","h5"]):
			spectrumfile=arg
		else:
			print("error: spectrumfile does not exist or is not a .spectra.h5 file.")
			sys.exit(1)
#--------------------------------------------------- SPECIFY FILELIST
	elif opt in ("-v", "--verbose"):
		verboseFLAG=True
#--------------------------------------------------- SOMETHING WENT REALLY WRONG
	else:
		print("error: unexpected option")
		sys.exit(1)

if "" in {filelist,spectrumfile}:
	print("error: one or more arguments missing given.")
	sys.exit(1)
########################################################## HELPER FUNCTIONS
#--------------------------------------------------------- retrieve the tagnumber from filename
def filepath2tag(**kwargs):
	return kwargs["filepath_"].split("/")[-1].split(".")[0].split("-")[1]

########################################################## MAIN
#---------------------------------------------------- IMPORT NAMES OF FILES TO PROCESS
try:
	files=ImportList(file_=filelist)
except:
	print("error: could not import filelist.")
	sys.exit(1)


#---------------------------------------------------- GET THE SPECTRUM INFORMATION

spectrumfile_FD=h5py.File(spectrumfile,'r')

#---------------------------------------------------- GET THE 9 DIGIT TAGS
tags=[str(tag) for tag in spectrumfile_FD['/tags'][:]]
#---------------------------------------------------- GET SPECTRUM INFORMATION FOR TAGS
color1_energy_eV=spectrumfile_FD['/color1_energy_eV'][:]
color1_wavelength_A=spectrumfile_FD['/color1_wavelength_A'][:]
color2_energy_eV=spectrumfile_FD['/color2_energy_eV'][:]
color2_wavelength_A=spectrumfile_FD['/color2_wavelength_A'][:]
Amp1=spectrumfile_FD['/Amp1'][:]
Amp2=spectrumfile_FD['/Amp2'][:]
Const=spectrumfile_FD['/Const'][:]
Peak1=spectrumfile_FD['/Peak1'][:]
Peak2=spectrumfile_FD['/Peak2'][:]
Width1=spectrumfile_FD['/Width1'][:]
Width2=spectrumfile_FD['/Width2'][:]

spectrumfile_FD.close()

######################################################## apply calibration functions
#-------------------------------------- convert from angstrom to electron volt
def ang2ev(**kwargs):
	return numpy.pi*2*197.3269788*10/kwargs["ang_"]
#-------------------------------------- convert from electron volt to angstrom
def ev2ang(**kwargs):
	return numpy.pi*2*197.3269788*10/kwargs["ev_"]


########################################################## ADAPT THIS FOR EVERY CALIBRATION PERFORMED
##########################################################
#------------------------------------------calibration obtained from 7keV data
def peak_2_energy_eV_7keVrange(**kwargs):
	return 6589.8+2.9759*kwargs["peak_idx_"]
#	return 6739.8+1.9280*kwargs["peak_idx_"]

#------------------------------------------calibration obtained from 9keV data
def peak_2_energy_eV_9keVrange(**kwargs):
	return 5725.0+3.8066*kwargs["peak_idx_"]
#	return 6234.8+3.2138*kwargs["peak_idx_"]
##########################################################
##########################################################

#-------------------------------------------------- apply conversion peak position to energy
color1_energy_eV=[peak_2_energy_eV_7keVrange(peak_idx_=peak_idx) for peak_idx in Peak1]
#-------------------------------------------------- apply conversion energy to wavelength
color1_wavelength_A=[ev2ang(ev_=energy_ev) for energy_ev in color1_energy_eV]
#-------------------------------------------------- apply conversion peak position to energy
color2_energy_eV=[peak_2_energy_eV_9keVrange(peak_idx_=peak_idx) for peak_idx in Peak2]
#-------------------------------------------------- apply conversion energy to wavelength
color2_wavelength_A=[ev2ang(ev_=energy_ev) for energy_ev in color2_energy_eV]



#--------------------------------------------------- MAP TAGNUMBER TO ARRAY INDEX
tag_idx_DICT=dict(zip(tags,numpy.arange(tags.__len__())))

#---------------------------------------------------- WRITE THE SPECTRUM INFO INTO THE FILES

for filepath in files:
	if not os.path.isfile(filepath):
		print("error: could not open file:"+filepath)
		continue
	else:
		if verboseFLAG: 
			print(filepath)
		tmptag=filepath2tag(filepath_=filepath)
		data_FD=h5py.File(filepath,'a')
		try:
			if "/photon_energy_ev_color1" in data_FD: del data_FD["/photon_energy_ev_color1"]
			data_FD["/photon_energy_ev_color1"]=color1_energy_eV[tag_idx_DICT[tmptag]]

			if "/photon_wavelength_A_color1" in data_FD: del data_FD["/photon_wavelength_A_color1"]
			data_FD["/photon_wavelength_A_color1"]=color1_wavelength_A[tag_idx_DICT[tmptag]]

			if "/photon_energy_ev_color2" in data_FD: del data_FD["/photon_energy_ev_color2"]
			data_FD["/photon_energy_ev_color2"]=color2_energy_eV[tag_idx_DICT[tmptag]]

			if "/photon_wavelength_A_color2" in data_FD: del data_FD["/photon_wavelength_A_color2"]
			data_FD["/photon_wavelength_A_color2"]=color2_wavelength_A[tag_idx_DICT[tmptag]]

			if "/Amp1" in data_FD: del data_FD["/Amp1"]
			data_FD["/Amp1"]=Amp1[tag_idx_DICT[tmptag]]

			if "/Amp2" in data_FD: del data_FD["/Amp2"]
			data_FD["/Amp2"]=Amp2[tag_idx_DICT[tmptag]]

			if "/Const" in data_FD: del data_FD["/Const"]
			data_FD["/Const"]=Const[tag_idx_DICT[tmptag]]

			if "/Peak1" in data_FD: del data_FD["/Peak1"]
			data_FD["/Peak1"]=Peak1[tag_idx_DICT[tmptag]]

			if "/Peak2" in data_FD: del data_FD["/Peak2"]
			data_FD["/Peak2"]=Peak2[tag_idx_DICT[tmptag]]

			if "/Width1" in data_FD: del data_FD["/Width1"]
			data_FD["/Width1"]=Width1[tag_idx_DICT[tmptag]]

			if "/Width2" in data_FD: del data_FD["/Width2"]
			data_FD["/Width2"]=Width2[tag_idx_DICT[tmptag]]

			if "/color1_energy_eV" in data_FD: del data_FD["/color1_energy_eV"]
			data_FD["/color1_energy_eV"]=color1_energy_eV[tag_idx_DICT[tmptag]]

			if "/color2_energy_eV" in data_FD: del data_FD["/color2_energy_eV"]
			data_FD["/color2_energy_eV"]=color2_energy_eV[tag_idx_DICT[tmptag]]

			if "/color1_wavelength_A" in data_FD: del data_FD["/color1_wavelength_A"]
			data_FD["/color1_wavelength_A"]=color1_wavelength_A[tag_idx_DICT[tmptag]]

			if "/color2_wavelength_A" in data_FD: del data_FD["/color2_wavelength_A"]
			data_FD["/color2_wavelength_A"]=color2_wavelength_A[tag_idx_DICT[tmptag]]

		except:
			print("error:tag number:"+tmptag+" not found in spectrum file:"+spectrumfile)
		data_FD.flush()
		data_FD.close()



