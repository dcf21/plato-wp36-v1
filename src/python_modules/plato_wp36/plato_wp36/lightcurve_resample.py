# -*- coding: utf-8 -*-

import numpy as np

from .lightcurve import LightcurveArbitraryRaster


class LightcurveResampler(object):
    """
    A class containing utility functions for resampling LCs onto different time rasters
    """

    def __init__(self, input_lc):
        assert isinstance(input_lc, LightcurveArbitraryRaster), \
            "The LightcurveResampler class can only operate on LightcurveArbitraryRaster objects."
        self._input = input_lc

    @staticmethod
    def _pixel_start_times(raster):
        """
        Turn a raster of the central times of pixels, into the start-time edge of each pixel.

        For example:

        >>> raster
        array([0., 1., 2., 3., 4.])
        >>> start_times
        array([-0.5,  0.5,  1.5,  2.5,  3.5,  4.5])

        :param raster:
            Numpy array containing the input raster of the central times of pixels
        :return:
            Numpy array containing the start-time edge of each pixel
        """

        start_times = (raster[1:] + raster[:-1]) / 2
        start_times = np.insert(arr=start_times,
                                obj=0,
                                values=raster[0] * 1.5 - raster[1] * 0.5
                                )
        start_times = np.append(arr=start_times,
                                values=raster[-1] * 1.5 - raster[-2] * 0.5
                                )
        return start_times

    @staticmethod
    def _pixel_widths(start_times):
        """
        Turn a raster of the central times of pixels, into the time durations of each pixel.

        For example:

        >>> start_times
        array([0., 1., 2., 3., 4.])
        >>> pixel_widths
        array([1, 1, 1, 1])

        :param start_times:
            Numpy array containing the start times of the pixels (N+1 entries)
        :return:
            Numpy array containing the time durations of each pixel (N entries)
        """

        pixel_widths = start_times[1:] - start_times[:-1]
        return pixel_widths

    @staticmethod
    def _resample(x_new, x_in, y_in):
        """
        Function which actually re-samples a lightcurve onto a new raster of times.

        :param x_new:
            The new raster of times

        :type x_new:
            np.ndarray

        :param x_in:
            The existing raster of times

        :type x_in:
            np.ndarray

        :param y_in:
            The existing lightcurve, on the existing raster

        :type y_in:
            np.ndarray

        :return:
            A numpy array containing the re-sampled lightcurve on the new raster
        """

        # Make sure that input arrays are numpy objects
        x_in = np.asarray(x_in)
        y_in = np.asarray(y_in)
        x_new = np.asarray(x_new)

        # Make sure that input data is sensible
        assert x_in.ndim == 1, \
            "Input x array should have exactly one dimension. Passed array has {} dimensions".format(x_in.ndim)
        assert y_in.ndim == 1, \
            "Input y array should have exactly one dimension. Passed array has {} dimensions".format(y_in.ndim)
        assert x_in.shape[0] > 3, \
            "Input lightcurve must have at least three pixels for re-sampling to produce sensible output"
        assert x_in.shape == y_in.shape, \
            "Input x and y vectors have different lengths"
        assert x_new.ndim == 1, \
            "New x array should have exactly one dimension. Passed array has {} dimensions".format(x_new.ndim)

        # Make an array of the start time of each pixel in the input raster. The final entry is the end time of the
        # last pixel, so if we have N input pixels, we output N+1 left edges (length N+1)
        x_in_pixel_start_times = LightcurveResampler._pixel_start_times(x_in)

        # Compute the time span of each pixel in the input raster (length N)
        x_in_pixel_width = LightcurveResampler._pixel_widths(x_in_pixel_start_times)

        # Do the same for the output raster
        x_new_pixel_start_times = LightcurveResampler._pixel_start_times(x_new)
        x_new_pixel_width = LightcurveResampler._pixel_widths(x_new_pixel_start_times)

        # Create an array of the integrated flux prior to time point i in <x_in_pixel_start_times> (length N+1)
        x_in_integrated = np.cumsum(np.insert(y_in * x_in_pixel_width, 0, 0))

        # Create an array of the integrated flux within each pixel of the output array, divided by the pixel's width
        y_new = (np.interp(xp=x_in_pixel_start_times,
                           fp=x_in_integrated,
                           x=x_new_pixel_start_times[1:]) -
                 np.interp(xp=x_in_pixel_start_times,
                           fp=x_in_integrated,
                           x=x_new_pixel_start_times[:-1])
                 ) / x_new_pixel_width

        # Return output
        return y_new

    def onto_raster(self, output_raster, resample_flags=True):
        """
        Resample this lightcurve onto a user-specified time raster.

        :param output_raster:
            The raster we should resample this lightcurve onto.

        :param resample_flags:
            Should we bother resampling the lightcurve's flags as the data itself? If not, the flags will be cleared,
            but the function will return 30% quicker.

        :return:
            New LightcurveArbitraryRaster object.
        """

        new_values = self._resample(x_new=output_raster,
                                    x_in=self._input.times,
                                    y_in=self._input.fluxes)

        new_uncertainties = self._resample(x_new=output_raster,
                                           x_in=self._input.times,
                                           y_in=self._input.uncertainties)

        output = LightcurveArbitraryRaster(times=output_raster,
                                           fluxes=new_values,
                                           uncertainties=new_uncertainties,
                                           metadata=self._input.metadata.copy()
                                           )

        if resample_flags and self._input.flags_set:
            output.mask = self._resample(x_new=output_raster,
                                         x_in=self._input.times,
                                         y_in=self._input.flags) > 0.5
            output.mask_set = not np.all(output.mask)

        return output

    def match_to_other_lightcurve(self, other, resample_flags=True):
        """
        Resample this lightcurve onto the same time raster of another LightcurveArbitraryRaster object.

        :param other:
            The other LightcurveArbitraryRaster object whose raster we should resample this
            LightcurveArbitraryRaster onto.

        :param resample_flags:
            Should we bother re-sampling the spectrum's flags as the data itself? If not, the mask will be cleared, but
            the function will return 30% quicker.

        :return:
            New LightcurveArbitraryRaster object.
        """

        return self.onto_raster(output_raster=other.wavelengths,
                                resample_flags=resample_flags)
