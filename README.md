################################### Synopsis

These scripts were developed for two-color data analysis with CrystFEL and published here under the GNU GENERAL PUBLIC LICENSE Version 3.
The primary citation for these scripts is as follows:

Alexander Gorel, Koji Motomura, Hironobu Fukuzawa, R. Bruce Doak, Marie Luise Grünbein, Mario Hilpert, Ichiro Inoue, Marco Kloos, Gabriela Kovácsová, Eriko Nango, Karol Nass, Christopher M. Roome, Robert L. Shoeman, Rie Tanaka, Kensuke Tono, Yasumasa Joti, Makina Yabashi, So Iwata, Lutz Foucar, Kiyoshi Ueda, Thomas R. M. Barends & Ilme Schlichting. "Multi-wavelength anomalous diffraction de novo phasing using a two-colour X-ray free-electron laser with wide tunability". Nat. Commun. 4, 1170 (2017).
doi:10.1038/s41467-017-00754-7

################################### Installation

These scripts come as standalone python modules.
A version of h5py newer than 2.6 is required for stream2h5.py.

################################### Usage

split.py -i <h5file>
split the .h5 file into a directory with subfiles

collect.py -d <dir>
collect .h5 files from a directory into a single .h5 file.

write_spectra.py -r <runnumber>
extract information on spectra for <runnumber> into run<runnumber>.spectra.h5 file from the SACLA metadata database.

write_calib_color.py -l <filelist.lst> -s <file.spectra.h5>
write the color energies from <file.spectra.h5> into each .h5 file in filelist.lst

stream2h5.py -i <input.stream>
processes CrystFEL <input.stream> file into <input.stream.h5> file.

list_of_indexed.py -1 <streamh5file1.h5> -o <outputfile.lst>
extracts all filenames of indexed images from indexing result from <streamh5file1.h5> and writes them to <outputfile.lst>.

write_subtract_peaks.py -1 <streamh5file1.h5> -2 <streamh5file2.h5> -o <h5outputpath>
subtract reflections in <streamh5file2.h5> from peaks in <streamh5file1.h5> which are in vicinity of 10pix and write these at <h5outputpath> into the respective .h5 files listed in <streamh5file1.h5>.

write_pca_peaks.py -f <fileh5path.h5> -g <geometrystreamh5path.h5> -d <h5datapath> -o <h5outputpath> [-n <number>][-u]
calculate best <number> feature point coordinates for <filepath.h5> .h5 image with geometry at <geometrypath.h5> data at <h5datapath> and write those into <h5outputpath> into the same .h5 file and update <u> those if neccessary.

