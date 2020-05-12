from pysismo import pstomo, psutils
import os, sys
import shutil
import glob
import pickle
import itertolls as it

# inversion parameters to vary
PERIODS = [6.0, 10.0, 15.0, 20.0]
GRID_STEPS = [0.3]
MINPECTSNRS = [7.0]
CORR_LENGTHS = [10, 30, 50, 100, 150]
ALPHAS = [50, 100, 200, 400, 800]
BETAS = [10, 20, 40, 80, 200]
LAMBDAS = [0.15, 0.3]

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
pickle_file = flist[res]

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
ofilename = os.path.join(TOMO_DIR, os.path.splitext(basename)[0]) + '.dat'
if os.path.exists(ofilename):
    # backup
    shutil.copyfile(ofilename, ofilename + '~')
f = open(ofilename,'w')

# performing tomographic inversions, systematically
# varying the inversion parameters
param_lists = it.product(PERIODS, GRID_STEPS, MINPECTSNRS, CORR_LENGTHS,
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
                           lambda_=lambda_)

    misfit = v.velocity_residuals()
    norm = v.model_norm()

    f.write('%5.1f%5.1f%5.1f%8.1f%8.1f%8.1f%8.2f%10.3f%10.3f\t%i\n' % \
                (period, grid_step, minspectSNR, corr_length, alpha, beta, lambda_, \
                abs(misfit).sum(), norm, len(misfit)))

f.close()
