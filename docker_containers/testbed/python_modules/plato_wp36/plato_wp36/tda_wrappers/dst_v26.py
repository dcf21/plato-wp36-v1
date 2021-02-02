# -*- coding: utf-8 -*-
# dst_v26.py

import os
import numpy as np
from astropy.io import fits

from plato_wp36.lightcurve import LightcurveArbitraryRaster
from plato_wp36.settings import settings


def process_lightcurve(lc: LightcurveArbitraryRaster, lc_duration: float):
    """
    Perform a transit search on a light curve, using the bls_kovacs code.

    :param lc:
        The lightcurve object containing the input lightcurve.
    :type lc:
        LightcurveArbitraryRaster
    :param lc_duration:
        The duration of the lightcurve, in units of days.
    :type lc_duration:
        float
    :return:
        dict containing the results of the transit search.
    """

    time = lc.times
    flux = lc.fluxes

    # Create working directory for DST
    work_dir = os.path.join(settings['pythonPath'], "private_code")
    fits_file_path = os.path.join(work_dir, "k2-3", "DATOS", "DAT", "lc.fits")

    # Make working directory structure
    os.system("cd {} ; ./asalto26.5/scripts/hazdir.sh k2-3".format(work_dir))

    # Output LC in FITS format for DST
    col1 = fits.Column(name='T', format='E', array=time)
    col2 = fits.Column(name='CADENCENO', format='E', array=np.arange(len(time)))
    col3 = fits.Column(name='FCOR', format='E', array=flux)
    cols = fits.ColDefs([col1, col2, col3])
    table_hdu = fits.BinTableHDU.from_columns(cols)

    # Populate FITS headers
    hdr = fits.Header()
    hdr['KEPLERID'] = '0'
    hdr['RA'] = '0'
    hdr['DEC'] = '0'
    hdr['KEPMAG'] = '0'
    empty_primary = fits.PrimaryHDU(header=hdr)

    # Output FITS file
    hdul = fits.HDUList([empty_primary, table_hdu])
    hdul.writeto(fits_file_path)

    # Run onyva_k2vanderburg.exe
    binary_path = os.path.join(work_dir, "asalto26.5/bin/onyva_k2vanderburg.exe")
    command_line = "{} -Rru . lc.fits".format(binary_path)
    os.system(command_line)

    # Clean up DST working directories
    os.system("cd {} ; rm -Rf k2-3".format(work_dir))

    # Return nothing for now
    results = {}

    # Extended results to save to disk
    results_extended = results

    # Return results
    return results, results_extended
