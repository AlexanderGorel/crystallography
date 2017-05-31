

import sys #-> argv
import os #-> file checks
import getopt #-> input parameters

#-------------------------------------------------- calculation dependencies
import h5py
import numpy
import itertools
from scipy.ndimage.filters import median_filter


############################################################################ CONTENTS OF DETECTOR MODULE
############################################################ import detector parameters

class ImportDetector(object):
    def __init__(self,**kwargs):
        self.filename=kwargs["h5_file_"]
        h5_file_FD=h5py.File(self.filename,"r")
        self.panel=filter(lambda x: "fs" in h5_file_FD["GEOMETRY/"+x],h5_file_FD["GEOMETRY"].keys())
        self.fs = map(lambda x: h5_file_FD["GEOMETRY/"+x+"/fs"][0],self.panel)
        self.ss = map(lambda x: h5_file_FD["GEOMETRY/"+x+"/ss"][0],self.panel)
        self.min_fs = map(lambda x: h5_file_FD["GEOMETRY/"+x+"/min_fs"][0],self.panel)
        self.max_fs = map(lambda x: h5_file_FD["GEOMETRY/"+x+"/max_fs"][0],self.panel)
        self.min_ss = map(lambda x: h5_file_FD["GEOMETRY/"+x+"/min_ss"][0],self.panel)
        self.max_ss = map(lambda x: h5_file_FD["GEOMETRY/"+x+"/max_ss"][0],self.panel)
        self.corner_x = map(lambda x: h5_file_FD["GEOMETRY/"+x+"/corner_x"][0],self.panel)
        self.corner_y = map(lambda x: h5_file_FD["GEOMETRY/"+x+"/corner_y"][0],self.panel)
        h5_file_FD.close()
        self.max_panel_fs_idx=min(self.max_fs)
        self.max_panel_ss_idx=min(self.max_ss)
        self.max_fs_idx=max(self.max_fs)
        self.max_ss_idx=max(self.max_ss)
        self.x_dim=self.max_panel_fs_idx+1
        self.y_dim=self.max_panel_ss_idx+1
        return None

############################################################ helper class
class Affine_Transform(object):
    def __init__(self,**kwargs):
        self.rotation = kwargs["rotation_"]
        self.translation = kwargs["translation_"]
        return None

    def __call__(self,**kwargs):
        return tuple(self.rotation.dot(kwargs["point_"])+self.translation)

############################################################ COORDINATE TRANSFORMATION
def ImportTransformations(**kwargs):
    return Transformations(detector_=kwargs["detector_"])

class Transformations(object):
    def __init__(self,**kwargs):
        self.detector= kwargs["detector_"]
        self.inv_rotations=zip(self.detector.fs,self.detector.ss)
        self.rotations= [numpy.array(((x_axis[0],y_axis[0]),(x_axis[1],y_axis[1]))) for (x_axis,y_axis) in self.inv_rotations]
        self.corner_xy=zip(self.detector.corner_x,self.detector.corner_y)
        self.affine_transforms= [Affine_Transform(rotation_=rotation_matrix,translation_=point_xy) for (rotation_matrix,point_xy) in zip(self.rotations,self.corner_xy)]
        return None

    def image_coordinateXY2panel_coordinate(self,**kwargs):
        """arguments: {point_}"""
        (x_,y_)=kwargs["point_"]
        pad_ydim=self.detector.y_dim
        pad_idx_=int(numpy.floor(y_/pad_ydim))
        y_=numpy.mod(y_,pad_ydim)
        return (tuple((x_,y_)),pad_idx_)

    def panel_coordinate2image_coordinateXY(self,**kwargs):
        """arguments: {point_,pad_idx_}"""
        (x_,y_)=kwargs["point_"]
        pad_ydim=self.detector.y_dim
        return tuple((x_,y_+kwargs["pad_idx_"]*pad_ydim))

    def panel_coordinate2detector_coordinate(self,**kwargs):
        """arguments: {panel_idx_,point_}"""
        return transformation_list[kwargs["panel_idx_"]](point_=kwargs["point_"])

    def detector_coordinate2panel_coordinate(self,**kwargs):
        """arguments: {point_}"""
        point = kwargs["point_"]
        projection_list = [(numpy.inner(numpy.subtract(point,corner),x_axis),numpy.inner(numpy.subtract(point,corner),y_axis)) for (corner,x_axis,y_axis) in zip(self.detector.corner_xy,self.detector.fs,self.detector.ss)]
        selector_list = [pX>=0 and pX<=self.detector.x_dim and pY>=0 and pY<=self.detector.y_dim for (pX,pY) in projection_list]
        true_idx_list = filter(lambda x:x[1],enumerate(selector_list))
        res=((0.,0.),0)
        if true_idx_list.__len__()>0:
            res=(tuple(projection_list[true_idx_list[0][0]]),true_idx_list[0][0])
        return res

############################################################### import pad data from data array

def ImportPadDataXY(**kwargs):
    """args:{dataYX_,detector_}"""
    res=[kwargs["dataYX_"][int(y):int(Y+1),int(x):int(X+1)] for (x,X,y,Y) in zip(kwargs["detector_"].min_fs,kwargs["detector_"].max_fs,kwargs["detector_"].min_ss,kwargs["detector_"].max_ss)]
    return map(lambda x: numpy.transpose(x),res)

########################################################################################## get list ordering

def ordering(**kwargs):
    res=sorted(range(kwargs["list_"].__len__()),key=lambda x:kwargs["function_"](kwargs["list_"][x]))
    return res

########################################################################################## order pixel indices by score ascending

def PCA_ORDERING_IDX_XY(**kwargs):	
#------------------------------------------------------- get the dimensions of the data
	(d1,d2)=kwargs["dataXY_"].shape
#------------------------------------------------------- MOST COMPUTATION GOES HERE: calculate median background
	radius=10
	median_dataXY=median_filter(numpy.lib.pad(kwargs["dataXY_"],(radius,radius),'edge'),2*radius+1)[radius:-1*radius,radius:-1*radius]
#------------------------------------------------------- calculate standardized signal over background
	diff_paddataXY=numpy.subtract(kwargs["dataXY_"],median_dataXY)
	diff_paddataXY_vec=numpy.reshape(diff_paddataXY,(d1*d2,))
	diff_paddataXY_mean=numpy.mean(diff_paddataXY_vec)
	diff_paddataXY_std=numpy.std(diff_paddataXY_vec)
	std_diff_paddataXY_vec=numpy.divide(numpy.subtract(diff_paddataXY_vec,diff_paddataXY_mean),diff_paddataXY_std)
#------------------------------------------------------- calculate standardized signal to background ratio
	div_paddataXY=numpy.divide(kwargs["dataXY_"],median_dataXY)
	div_paddataXY_vec=numpy.reshape(div_paddataXY,(d1*d2,))
	div_paddataXY_mean=numpy.mean(div_paddataXY_vec)
	div_paddataXY_std=numpy.std(div_paddataXY_vec)
	std_div_paddataXY_vec=numpy.divide(numpy.subtract(div_paddataXY_vec,div_paddataXY_mean),div_paddataXY_std)
#------------------------------------------------------- perform principle component analysis
	cov=numpy.cov((std_diff_paddataXY_vec,std_div_paddataXY_vec))
	(L,V)=numpy.linalg.eig(cov)
	EigV=numpy.transpose(V)
#------------------------------------------------------- get the largest eigenvalue and the corresponding eigenvector
	ord_L=ordering(list_=L,function_=numpy.abs)
	sorted_EigV=[EigV[idx] for idx in ord_L]
#------------------------------------------------------- calculate the scores for the points
	projV=numpy.multiply(sorted_EigV[-1],numpy.sign(numpy.dot((1,1),sorted_EigV[-1])))
	score_list=[numpy.dot(projV,tup) for tup in zip(std_diff_paddataXY_vec,std_div_paddataXY_vec)]
#------------------------------------------------------- find score ordering
	ord_score_list=ordering(list_=score_list,function_=(lambda x:x))
#------------------------------------------------------- get the coordinates for the indices with the best score
	idx_list=[idx for idx in itertools.product(range(d1),range(d2))]
	sorted_idx_list=[idx_list[idx] for idx in ord_score_list]
	return sorted_idx_list

##################################################################################### gather best peaks by proximity and return median of pointcloud

def ProximityClusterMedians(**kwargs):
#------------------------------------------------------- bag of 2dim idx
	clustering=[[kwargs["idx_list_"][-1]]]
#------------------------------------------------------- assignment of a 2dim idx to its bag
	clusterassignment={kwargs["idx_list_"][-1]:0}
#------------------------------------------------------- fill up the bags if the idx are too close, dist < 10 pix
	for n in range(2,kwargs["idx_list_"].__len__()):
		tmpidx=kwargs["idx_list_"][-1*n]
		nearestidx=min(kwargs["idx_list_"][-1*n+1:],key=lambda x:numpy.linalg.norm(numpy.subtract(x,tmpidx)))
		if numpy.linalg.norm(numpy.subtract(nearestidx,tmpidx)) <= 10:
			tmpclass=clusterassignment[nearestidx]
			clustering[tmpclass].append(tmpidx)
			clusterassignment[tmpidx]=tmpclass
		else:
			tmpclass=clustering.__len__()
			clustering.append([tmpidx])
			clusterassignment[tmpidx]=tmpclass
#------------------------------------------------------- break when we have enough clusters
		if clustering.__len__() > kwargs["num_"]: break
#------------------------------------------------------- return the median 2dim indices in the clusters
	medians=[[numpy.median(idx_list) for idx_list in zip(*cluster)] for cluster in clustering[:-1]]
	return medians
##################################################################################### gather best peaks by proximity and return best (first) idx

def ProximityClusterBest(**kwargs):
#------------------------------------------------------- bag of 2dim idx
	clustering=[[kwargs["idx_list_"][-1]]]
#------------------------------------------------------- assignment of a 2dim idx to its bag
	clusterassignment={kwargs["idx_list_"][-1]:0}
#------------------------------------------------------- fill up the bags if the idx are too close, dist < 10 pix
	for n in range(2,kwargs["idx_list_"].__len__()):
		tmpidx=kwargs["idx_list_"][-1*n]
		nearestidx=min(kwargs["idx_list_"][-1*n+1:],key=lambda x:numpy.linalg.norm(numpy.subtract(x,tmpidx)))
		if numpy.linalg.norm(numpy.subtract(nearestidx,tmpidx)) <= 10:
			tmpclass=clusterassignment[nearestidx]
			clustering[tmpclass].append(tmpidx)
			clusterassignment[tmpidx]=tmpclass
		else:
			tmpclass=clustering.__len__()
			clustering.append([tmpidx])
			clusterassignment[tmpidx]=tmpclass
#------------------------------------------------------- break when we have enough clusters
		if clustering.__len__() > kwargs["num_"]: break
#------------------------------------------------------- return the best (first) 2dim indices in the clusters
	best=[cluster[0] for cluster in clustering[:-1]]
	return best
##################################################################################### INPUT ARGS PROCESSING

#--------------------------------------------------- USAGE
def usage():
	print(str(sys.argv[0])+" -f <fileh5path> -g <geometrystreamh5path> -d <h5datapath> -o <outputpath> [-n <number>][-u]")
	print("calculate best <number> feature point coordinates for <filepath> .h5 image with geometry at <geometrypath> data at at <h5datapath> and write those into <h5outputpath> into the same .h5 file and update <u> those if neccessary.")
	print("if data at h5outputfile already exists it will be replaced if the -u update flag is given.")
	print("options:")
	print("-h --help")
	print("-f --fileh5path")
	print("-g --geometrystreamh5path")
	print("-d --h5datapath")
	print("-o --h5outputpath")
	print("-n --number")
	print("-u --update")

#--------------------------------------------------- GETOPTS

try:
	(opts, args) = getopt.getopt(sys.argv[1:], "hf:g:d:o:n:u", ["help","fileh5path=","geometrystreamh5path=","h5datapath=","h5outputpath=","number=","update"])
except getopt.GetoptError:
	usage()
	sys.exit(1)

#--------------------------------------------------- NO OPTIONS -> NOTHING TO DO
if opts.__len__()==0:
    usage()
    sys.exit()

#--------------------------------------------------- OPERATION VARIABLES

fileh5path=""
geometrystreamh5path=""
h5datapath=""
h5outputpath=""
updateFLAG=False
number=20

#--------------------------------------------------- PARSE THE ARGUMENTS
for (opt, arg) in opts:
#--------------------------------------------------- PRINT USAGE
	if opt in ("-h","--help"):
		usage()
		sys.exit()
#--------------------------------------------------- SPECIFY FILE
	elif opt in ("-f", "--fileh5path"):
		if os.path.exists(arg) and arg.split(".")[-1]=="h5":
			fileh5path=arg
		else:
			print("error: fileh5path does not exist or is not a .h5 file.")
			sys.exit(1)
#--------------------------------------------------- SPECIFY FILE
	elif opt in ("-g", "--geometrystreamh5path"):
		if os.path.exists(arg) and arg.split(".")[-2:]==["stream","h5"]:
			geometrystreamh5path=arg
		else:
			print("error: geometrystreamh5path file does not exist or is not a .stream.h5 file.")
			sys.exit(1)
#--------------------------------------------------- SPECIFY H5DATAPATH
	elif opt in ("-d", "--h5datapath"):
		h5datapath=arg
#--------------------------------------------------- SPECIFY H5DATAPATH
	elif opt in ("-o", "--h5outputpath"):
		h5outputpath=arg
#--------------------------------------------------- SPECIFY H5DATAPATH
	elif opt in ("-u", "--update"):
		updateFLAG=True
#--------------------------------------------------- SPECIFY H5DATAPATH
	elif opt in ("-n", "--number"):
		try:
			number=int(arg)
			number=numpy.abs(number)
		except:
			print("error: number ist not integer")
			sys.exit(1)
#--------------------------------------------------- SOMETHING WENT REALLY WRONG
	else:
		print("error: unexpected option")
		sys.exit(1)
#--------------------------------------------------- FURTHER CHECKS

if "" in (fileh5path,geometrystreamh5path,h5datapath,h5outputpath):
	print("error: one or more arguments are empty")
	sys.exit(1)
if fileh5path == geometrystreamh5path:
	print("error: geometryfilepath is filepath")
	sys.exit(1)
if h5outputpath == h5datapath:
	print("error: h5datapath and h5outputpath are identic")
	sys.exit(1)

if number == 0:
	print("error: n has to be larger than 0")
	sys.exit(1)

##################################################################################### CALCULATION

try:
	detector = ImportDetector(h5_file_=geometrystreamh5path)
except:
	print("error: could not import geometrystreamh5path")
	sys.exit(1)
transformations = ImportTransformations(detector_=detector)

#-------------------------------------------------------------------------- import image data from file
try:
	file=h5py.File(fileh5path,"a")
except:
	print("error: could not open file")
	file.close()
	sys.exit(1)
try:
	dataYX = file[h5datapath][:]
except:
	print("error: h5datapath does not exist in file")
	file.close()
	sys.exit(1)
if (not updateFLAG) and h5outputpath in file:
	print("error: h5outputpath already exists and must be updated")
	file.close()
	sys.exit(1)

#---------------------------------------------------------------------- cut image into pad data
paddataXY=ImportPadDataXY(dataYX_=dataYX,detector_=detector)
offset_corrected_paddataXY=list()
#---------------------------------------------------------------- add a bias to the data
# and set numbers < offset to offset to prevent wrong signal to noise numbers 

for pad in paddataXY:
	(d1,d2)=pad.shape
	sorted_pad_vec=numpy.sort(numpy.reshape(pad,(d1*d2,)))
	offset=100
	bias=offset-1*sorted_pad_vec[100]
	pad=numpy.add(bias,pad)
	pad[pad<=offset]=offset
	offset_corrected_paddataXY.append(pad)

offset_corrected_paddataXY=numpy.array(offset_corrected_paddataXY)
#---------------------------------------------------------------- calculate median background (MOST COMPUTATION COST GOES HERE)

ordered_pad_points=[PCA_ORDERING_IDX_XY(dataXY_=data) for data in offset_corrected_paddataXY]

#--------------------------------------------------- order pad coordinates by score
best_pad_points =[ProximityClusterBest(idx_list_=idx_list,num_=number) for idx_list in ordered_pad_points]
#best_pad_points =[ProximityClusterMedians(idx_list_=idx_list,num_=number) for idx_list in ordered_pad_points]
#--------------------------------------------------- get the positions of number best peaks 
best_image_points=list()

[[best_image_points.append(transformations.panel_coordinate2image_coordinateXY(point_=point,pad_idx_=pad_idx)) for point in point_set] for (pad_idx,point_set) in enumerate(best_pad_points)]

#--------------------------------------------------- bring the data into the right form
poi_data=[(x,y,100.) for (x,y) in best_image_points]

#--------------------------------------------------- write the peak positions into file
if h5outputpath in file:
	del file[h5outputpath]

file[h5outputpath]=poi_data
file.flush()
file.close()
#---------------------------------------------------------------- 











