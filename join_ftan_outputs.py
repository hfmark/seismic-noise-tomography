from pysismo import pstomo
import glob
import pickle
import os, sys

from pysismo.psconfig import FTAN_DIR

####
# combine dispersion curve lists from two separate FTAN runs. possible? probably. wise? unclear.
####

# selecting dispersion curves
#setname = 'al20_snr7_wv3'
#setname = 'al20_snr7_wv3_vpc'
#setname = 'al12_snr7_wv3'
setname = 'al12_snr7_wv3_vpc'

flist = sorted(glob.glob(os.path.join(FTAN_DIR, 'FTAN*dataless*%s.pickle' % setname)))
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
            v,s = c.filtered_vels_sdevs()
            snr = c._SNRs
            everything.append(c)
        except Exception:  # curves without spectral SNR get excluded
            print(c)


ofile = os.path.join(FTAN_DIR, 'FTAN_2004-2019_%s.pickle' % setname)
f = open(ofile,'wb')
pickle.dump(everything, f, protocol=2)
f.close()

