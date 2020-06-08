from pysismo import pstomo
import glob
import pickle
import os, sys

from pysismo.psconfig import FTAN_DIR

####
# combine dispersion curve lists
####

# selecting dispersion curves
flist = sorted(glob.glob(os.path.join(FTAN_DIR, 'FTAN*datalesspaz.pickle')))
print(flist)
res = input('')

everything = []
for pickle_file in flist:
    print('\nLoading dispersion curves from ' + pickle_file)

    f = open(pickle_file,'rb')
    curves = pickle.load(f)
    f.close()

    for c in curves:
        try:
            v,s = c.filtered_vels_sdevs(vtype='group')
            snr = c._SNRs
            everything.append(c)
        except Exception:  # curves without spectral SNR get excluded
            print(c)


ofile = os.path.join(FTAN_DIR, 'FTAN_2004-2019_datalesspaz.pickle')
f = open(ofile,'wb')
pickle.dump(everything, f, protocol=2)
f.close()

