from pysismo import pstomo, psutils
import os, sys
import shutil
import glob
import pickle
import itertools as it
import numpy as np

# inversion parameters to vary
PERIODS = [8.0, 14.0, 20.0]
GRID_STEPS = [0.3]
MINSPECTSNRS = [5.0]
CORR_LENGTHS = [50]
ALPHAS = np.append(np.arange(50,500,50),np.arange(500,2500,100))
BETAS = np.arange(10,200,30)
#BETAS = [10,50]
LAMBDAS = [0.2]

vtype = 'phase'

from pysismo.psconfig import FTAN_DIR, TOMO_DIR

# selecting dispersion curves
flist = sorted(glob.glob(os.path.join(FTAN_DIR, 'FTAN*.pickle*')))
print('Select file(s) containing dispersion curves to process: [1]')
for i,f in enumerate(flist):
    print('{} - {}'.format(i+1, os.path.basename(f)))

try:
    res = int(input('\n') or 1)
except ValueError:
    print('only one pickle file, please')
    sys.exit()
pickle_file = flist[res-1]

print("\nProcessing dispersion curves of file: " + pickle_file)

f = open(pickle_file, 'rb')
curves = pickle.load(f)
f.close()

# opening outfile
try:
    os.makedirs(TOMO_DIR)
except:
    pass
basename = os.path.basename(pickle_file).replace('FTAN', 'Lcurve-params')
ofilename = os.path.join(TOMO_DIR, os.path.splitext(basename)[0]) +'_' + vtype + '.dat'
if os.path.exists(ofilename):
    # backup
    shutil.copyfile(ofilename, ofilename + '~')
f = open(ofilename,'w')

# performing tomographic inversions, systematically
# varying the inversion parameters
param_lists = it.product(PERIODS, GRID_STEPS, MINSPECTSNRS, CORR_LENGTHS,
                         ALPHAS, BETAS, LAMBDAS)
param_lists = list(param_lists)
for period, grid_step, minspectSNR, corr_length, alpha, beta, lambda_ in param_lists:
    s = ("Period = {} s, grid step = {}, min SNR = {}, corr. length "
         "= {} km, alpha = {}, beta = {}, lambda = {}")
    print(s.format(period, grid_step, minspectSNR, corr_length, alpha, beta, lambda_))

    # Performing the tomographic inversion to produce a velocity map
    # at period = *period* , with parameters given above:
    # - *lonstep*, *latstep* control the internode distance of the grid
    # - *minnbtrimester*, *maxsdev*, *minspectSNR*, *minspectSNR_nosdev*
    #   correspond to the selection criteria
    # - *alpha*, *corr_length* control the spatial smoothing term
    # - *beta*, *lambda_* control the weighted norm penalization term
    #
    # Note that if no value is given for some parameter, then the
    # inversion will use the default value defined in the configuration
    # file.
    #
    # (See doc of VelocityMap for a complete description of the input
    # arguments.)

    v = pstomo.VelocityMap(dispersion_curves=curves,
                           period=period,
                           verbose=False,
                           lonstep=grid_step,
                           latstep=grid_step,
                           minspectSNR=minspectSNR,
                           correlation_length=corr_length,
                           alpha=alpha,
                           beta=beta,
                           lambda_=lambda_,
                           vtype=vtype)

    misfit = v.velocity_residuals()
    norm = v.model_norm()

    f.write('%5.1f%5.1f%5.1f%8.1f%8.1f%8.1f%8.2f%10.3f%10.3f\t%i\n' % \
                (period, grid_step, minspectSNR, corr_length, alpha, beta, lambda_, \
                abs(misfit).sum(), norm, len(misfit)))

f.close()
