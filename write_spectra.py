
import sys #-> argv
import os #-> file checks
import getopt #-> input parameters


import numpy
import h5py
from scipy.optimize import curve_fit
import dailies

#####################################################

#--------------------------------------------------- USAGE
def usage():
	print(str(sys.argv[0])+" -r <runnumber>")
	print("extract information on spectra for <runnumber> into run<runnumber>.spectra.h5 file")
	print("options:")
	print("-h --help")
	print("-r --runnumber")

#--------------------------------------------------- GETOPTS

try:
	(opts, args) = getopt.getopt(sys.argv[1:], "hr:", ["help","runnumber="])
except getopt.GetoptError:
	usage()
	sys.exit(1)

#--------------------------------------------------- NO OPTIONS -> NOTHING TO DO
if opts.__len__()==0:
	usage()
	sys.exit()
########################################################## INPUT ARG VARIABLES

runNumber=""

########################################################## ARGUMENT PROCESSING
for (opt, arg) in opts:
#--------------------------------------------------- PRINT USAGE
	if opt in ("-h","--help"):
		usage()
		sys.exit()
#--------------------------------------------------- SPECIFY RUNNUMBER
	elif opt in ("-r", "--runnumber"):
		try:
			runNumber=int(arg)
		except:
			print("error: invalid runnumber:"+str(arg))
			sys.exit(1)
#--------------------------------------------------- SOMETHING WENT REALLY WRONG
	else:
		print("error: unexpected option")
		sys.exit(1)
######################################################### ARGUMENT CHECKS

outfile= "run"+str(runNumber)+".spectra.h5"

if os.path.isfile(outfile):
	print("error: outputfile already exists:"+outfile)
	sys.exit(1)

#################################################### MAIN

beamlineNumber=3
#---------------------------------------------------- get the high tag number
(err,taghi)= dailies.ReadHighTagNumber(beamlineNumber,runNumber)
#----------------------------------------------------get the tags
(err,tags)=dailies.ReadTagList(beamlineNumber,runNumber)
#---------------------------------------------------- get the pulse intensities
intensityfield="xfel_bl_3_st_4_bm_1_pd/charge"

(err,intensities) = dailies.ReadSyncDataListFloat(intensityfield,taghi,tags)
#---------------------------------------------------- get the pulse energies
energyfield="xfel_bl_3_tc_spec_1/energy"

(err,energies) = dailies.ReadSyncDataListFloat(energyfield,taghi,tags)
#---------------------------------------------------- get the spectra
ccdName="MPCCD-1-1-011"

spectra=list()
parameter=list()
residua=list()
xarr = numpy.arange(1024)

##################################################### functions for fitting
def Lorentzian(xArray, amplitude, center, gamma):
	center = float(center)
	width = float(gamma)
	lorent = amplitude / (1.0 + ((xArray - center) / gamma) ** 2)
	return lorent

def Lorentzian2WithC(xArray, amplitude1, center1, width1, amplitude2, center2, width2, const):
	return Lorentzian(xArray, amplitude1, center1, width1) + Lorentzian(xArray, amplitude2, center2, width2) + const
#####################################################

covariances=list()

for tagname in tags:
	(err,detData) = dailies.ReadDetData(ccdName,beamlineNumber,runNumber,taghi,tagname)
	spectrum = numpy.array(detData).sum(axis=1)
	spectra.append(spectrum)
	const = spectrum[500:600].mean()
	peak1 = spectrum[10:300].argmax() + 10
	peak2 = spectrum[700:1000].argmax() + 700
	guess = [spectrum[peak1], peak1, 25, spectrum[peak2], peak2, 25, const]
	try:
		(param,paramCov) = curve_fit(Lorentzian2WithC, xarr, spectrum, guess,maxfev=1500)
	except RuntimeError:
		print("bad fit.")
		paramCov=numpy.diag((1,1,1,1,1,1,1))
		param=(1,1,1,1,1,1,1)
	residuum=numpy.linalg.norm(numpy.subtract(spectrum,Lorentzian2WithC(xarr,param[0],param[1],param[2],param[3],param[4],param[5],param[6])))/spectrum.__len__()
	parameter.append(param)
	covariances.append(paramCov)
	residua.append(residuum)
	if (spectra.__len__() % 100 == 0): print(str(spectra.__len__())+"/"+str(tags.__len__()))

(Amp1,Peak1,Width1,Amp2,Peak2,Width2,Const)=numpy.transpose(parameter)
#--------------------------------------------------- conversion functions
#-------------------------------------- convert from angstrom to electron volt
def ang2ev(**kwargs):
	return numpy.pi*2*197.3269788*10/kwargs["ang_"]
#-------------------------------------- convert from electron volt to angstrom
def ev2ang(**kwargs):
	return numpy.pi*2*197.3269788*10/kwargs["ev_"]
#---------------------------------------------------apply calibration
#------------------------------------------calibration obtained from 7keV data
def peak_2_energy_eV_7keVrange(**kwargs):
	return 6739.8+1.9280*kwargs["peak_idx_"]

#------------------------------------------calibration obtained from 9keV data
def peak_2_energy_eV_9keVrange(**kwargs):
	return 6234.8+3.2138*kwargs["peak_idx_"]
#-------------------------------------------------- apply conversion peak position to energy
color1_energy_eV=[peak_2_energy_eV_7keVrange(peak_idx_=peak_idx) for peak_idx in Peak1]
#-------------------------------------------------- apply conversion energy to wavelength
color1_wavelength_A=[ev2ang(ev_=energy_ev) for energy_ev in color1_energy_eV]
#-------------------------------------------------- apply conversion peak position to energy
color2_energy_eV=[peak_2_energy_eV_9keVrange(peak_idx_=peak_idx) for peak_idx in Peak2]
#-------------------------------------------------- apply conversion energy to wavelength
color2_wavelength_A=[ev2ang(ev_=energy_ev) for energy_ev in color2_energy_eV]

#--------------------------------------------------- write into outfile

outfileFD=h5py.File(outfile,'w')

outfileFD['/tags']=tags
outfileFD['/energy_keV']=energies
outfileFD['/photo_diode_charge_C']=intensities
outfileFD['/spectrum']=spectra
outfileFD['/Amp1']=Amp1
outfileFD['/Peak1']=Peak1
outfileFD['/Width1']=Width1
outfileFD['/Amp2']=Amp2
outfileFD['/Peak2']=Peak2
outfileFD['/Width2']=Width2
outfileFD['/Const']=Const
outfileFD['/residua']=residua
outfileFD['/color1_energy_eV']=color1_energy_eV
outfileFD['/color1_wavelength_A']=color1_wavelength_A
outfileFD['/color2_energy_eV']=color2_energy_eV
outfileFD['/color2_wavelength_A']=color2_wavelength_A
outfileFD['/fit_parameter_covmat']=numpy.array(covariances)
outfileFD['/fit_parameter_covmat_ordering']="(Amp1,Peak1,Width1,Amp2,Peak2,Width2,Const)"

outfileFD.flush()
outfileFD.close()





