# -*- coding: utf-8 -*-
# lightcurve.py

"""
Classes for representing light curves, either on arbitrary time rasters, or on rasters with fixed step.
"""

import gzip
import logging
import math
import os

import numpy as np

from .settings import settings


class LightcurveArbitraryRaster:
    """
    A class representing a lightcurve which is sampled on an arbitrary raster of times.
    """

    def __init__(self, times, fluxes, uncertainties=None, flags=None, metadata=None):
        """
        Create a lightcurve which is sampled on an arbitrary raster of times.

        :param times:
            The times of the data points.
        :type times:
            np.ndarray
        :param fluxes:
            The light fluxes at each data point.
        :type fluxes:
            np.ndarray
        :param uncertainties:
            The uncertainty in each data point.
        :type uncertainties:
            np.ndarray
        :param flags:
            The flag associated with each data point.
        :type flags:
            np.ndarray
        :param metadata:
            The metadata associated with this lightcurve.
        :type metadata:
            dict
        """

        # Check inputs
        assert isinstance(times, np.ndarray)
        assert isinstance(fluxes, np.ndarray)

        # Unset all flags if none were specified
        if flags is not None:
            assert isinstance(flags, np.ndarray)
        else:
            flags = np.zeros_like(times)

        # Make an empty metadata dictionary if none was specified
        if metadata is not None:
            assert isinstance(metadata, dict)
        else:
            metadata = {}

        # Make uncertainty zero if not specified
        if uncertainties is not None:
            assert isinstance(uncertainties, np.ndarray)
        else:
            uncertainties = np.zeros_like(fluxes)

        # Store the data
        self.times = times
        self.fluxes = fluxes
        self.uncertainties = uncertainties
        self.flags = flags
        self.flags_set = True
        self.metadata = metadata

    def to_file(self, directory, filename, binary=False, gzipped=True, overwrite=True):
        """
        Write a lightcurve out to a text data file. The time axis is multiplied by a factor 86400 to convert
        from days into seconds.

        :param filename:
            The filename of the lightcurve (within our local lightcurve archive).
        :type filename
            str
        :param directory:
            The name of the directory inside the lightcurve archive where this lightcurve should be saved.
        :type directory:
            str
        :param binary:
            Boolean specifying whether we store lightcurve on disk in binary format or plain text.
        :type binary:
            bool
        :param gzipped:
            Boolean specifying whether we gzip plain-text lightcurves.
        :type gzipped:
            bool
        :param overwrite:
            Boolean specifying whether we're allowed to overwrite existing files.
        :type overwrite:
            bool
        """
        # Target path for this lightcurve
        target_path = os.path.join(settings['lcPath'], directory, filename)

        # Check that we're not overwriting an existing file
        if not overwrite:
            assert not os.path.exists(target_path), \
                "Attempting to overwrite existing lightcurve <{}>".format(target_path)

        # Pick the writer for this lightcurve
        if not gzipped:
            opener = open
        else:
            opener = gzip.open

        # Write lightcurve metadata
        target_path_metadata = "{}.metadata".format(target_path)
        with open(target_path_metadata, "w"):
            out.write("{}={}\n".format("binary", int(binary)))
            out.write("{}={}\n".format("gzipped", int(gzipped)))
            # Include metadata in text file
            for key, value in self.metadata.items():
                out.write("{}={}\n".format(key, value))

        # Write this lightcurve output into lightcurve archive
        if not binary:
            with opener(target_path, "wt") as out:
                # Output the lightcurve itself
                np.savetxt(out, np.transpose([self.times * 86400, self.fluxes, self.flags, self.uncertainties]))
        else:
            np.save(target_path, np.transpose([self.times * 86400, self.fluxes, self.flags, self.uncertainties]))

    @classmethod
    def from_file(cls, directory, filename, cut_off_time=None):
        """
        Read a lightcurve from a data file in our lightcurve archive.

        :param filename:
            The filename of the input data file.
        :type filename:
            str
        :param cut_off_time:
            Only read lightcurve up to some cut off time
        :type cut_off_time:
            float
        :param directory:
            The directory in which the lightcurve is stored.
        :type directory:
            str
        :return:
            A <LightcurveArbitraryRaster> object.
        """

        times = []
        fluxes = []
        uncertainties = []
        flags = []

        metadata = {
            'directory': directory,
            'filename': filename
        }
        # Full path for this lightcurve
        file_path = os.path.join(settings['lcPath'], directory, filename)

        # Read all lightcurve metadata
        target_path_metadata = "{}.metadata".format(target_path)
        with open(target_path_metadata):
            test = re.match(r"(.*)=(.*)", line)
            if test is not None:
                metadata_key = test.group(1).strip()
                metadata_value = test.group(2).strip()

                # If metadata value is a float, convert it to a float. Otherwise keep it as string.
                try:
                    metadata_value = float(metadata_value)
                except ValueError:
                    pass

                metadata[metadata_key] = metadata_value

        # Read file format of lightcurve from metadata
        assert 'binary' in metadata
        binary = bool(metadata['binary'])
        assert 'gzipped' in metadata
        gzipped = bool(metadata['gzipped'])

        # Look up file open function
        file_opener = gzip.open if gzipped else open

        if binary:
            # Read binary lightcurve file
            time, flux, flag, uncertainties = np.load(file_path)
            time /= 86400  # Times stored in seconds; but Lightcurve objects use days
        else:
            # Textual lightcurve: loop over lines of input file
            with file_opener(file_path, "rt") as file:
                for line in file:
                    # Ignore blank lines and comment lines
                    if len(line) == 0 or line[0] == '#':
                        continue

                    # Unpack data
                    words = line.split()
                    time = float(words[0]) / 86400  # Times stored in seconds; but Lightcurve objects use days
                    flux = float(words[1])
                    flag = float(words[2])
                    uncertainty = float(words[3])

                    # Check we have not exceeded cut-off time
                    if cut_off_time is not None and time > cut_off_time:
                        continue

                    # Read three columns of data
                    times.append(time)
                    fluxes.append(flux)
                    flags.append(flag)
                    uncertainties.append(uncertainty)

        # Convert into a Lightcurve object
        lightcurve = LightcurveArbitraryRaster(times=np.asarray(times),
                                               fluxes=np.asarray(fluxes),
                                               uncertainties=np.asarray(uncertainties),
                                               flags=np.asarray(flags),
                                               metadata=metadata
                                               )

        # Return lightcurve
        return lightcurve

    def __add__(self, other):
        """
        Add two lightcurves together.

        :type other:
            LightcurveArbitraryRaster
        """

        # Avoid circular import
        from .lightcurve_resample import LightcurveResampler

        # Resample other lightcurve onto same time raster as this
        resampler = LightcurveResampler(input_lc=other)
        other_resampled = resampler.match_to_other_lightcurve(other=self)

        # Merge metadata from the two input lightcurves
        output_metadata = {**self.metadata, **other.metadata}

        # Create output lightcurve
        result = LightcurveArbitraryRaster(
            times=self.times,
            fluxes=self.fluxes + other_resampled.fluxes,
            uncertainties=np.hypot(self.uncertainties, other_resampled.uncertainties),
            flags=np.hypot(self.flags, other_resampled.flags),
            metadata=output_metadata
        )

        return result

    def __sub__(self, other):
        """
        Subtract one lightcurve from another.

        :type other:
            LightcurveArbitraryRaster
        """

        # Avoid circular import
        from .lightcurve_resample import LightcurveResampler

        # Resample other lightcurve onto same time raster as this
        resampler = LightcurveResampler(input_lc=other)
        other_resampled = resampler.match_to_other_lightcurve(other=self)

        # Merge metadata from the two input lightcurves
        output_metadata = {**self.metadata, **other.metadata}

        # Create output lightcurve
        result = LightcurveArbitraryRaster(
            times=self.times,
            fluxes=self.fluxes - other_resampled.fluxes,
            uncertainties=np.hypot(self.uncertainties, other_resampled.uncertainties),
            flags=np.hypot(self.flags, other_resampled.flags),
            metadata=output_metadata
        )

        return result

    def __mul__(self, other):
        """
        Multiply two lightcurves together.

        :type other:
            LightcurveArbitraryRaster
        """

        # Avoid circular import
        from .lightcurve_resample import LightcurveResampler

        # Resample other lightcurve onto same time raster as this
        resampler = LightcurveResampler(input_lc=other)
        other_resampled = resampler.match_to_other_lightcurve(other=self)

        # Merge metadata from the two input lightcurves
        output_metadata = {**self.metadata, **other.metadata}

        # Create output lightcurve
        result = LightcurveArbitraryRaster(
            times=self.times,
            fluxes=self.fluxes * other_resampled.fluxes,
            uncertainties=np.hypot(self.uncertainties, other_resampled.uncertainties),
            flags=np.hypot(self.flags, other_resampled.flags),
            metadata=output_metadata
        )

        return result

    def estimate_sampling_interval(self):
        """
        Estimate the time step on which this light curve is sampled, with robustness against missing points.

        :return:
            Time step
        """

        differences = np.diff(self.times)
        differences_sorted = np.sort(differences)

        interquartile_range_start = int(len(differences) * 0.25)
        interquartile_range_end = int(len(differences) * 0.75)
        interquartile_data = differences_sorted[interquartile_range_start:interquartile_range_end]

        interquartile_mean = np.mean(interquartile_data)

        # Round time interval to nearest number of integer seconds
        interquartile_mean = round(interquartile_mean * 86400) / 86400

        return float(interquartile_mean)

    def check_fixed_step(self, verbose=True, max_errors=6):
        """
        Check that this light curve is sampled at a fixed time interval. Return the number of errors.

        :param verbose:
            Should we output a logging message about every missing time point?
        :type verbose:
            bool
        :param max_errors:
            The maximum number of errors we should show
        :type max_errors:
            int
        :return:
            int
        """

        abs_tol = 1e-4
        rel_tol = 0

        error_count = 0
        spacing = self.estimate_sampling_interval()

        if verbose:
            logging.info("Time step is {:.15f}".format(spacing))

        differences = np.diff(self.times)

        for index, step in enumerate(differences):
            # If this time point has the correct spacing, it is OK
            if math.isclose(step, spacing, abs_tol=abs_tol, rel_tol=rel_tol):
                continue

            # We have found a problem
            error_count += 1

            # See if we have skipped some time points
            points_missed = step / spacing - 1
            if math.isclose(points_missed, round(points_missed), abs_tol=abs_tol, rel_tol=rel_tol):
                if verbose and (max_errors is None or error_count <= max_errors):
                    logging.info("index {:5d} - {:d} points missing at time {:.5f}".format(index,
                                                                                           int(points_missed),
                                                                                           self.times[index]))
                continue

            # Or is this an entirely unexpected time interval?
            if verbose and (max_errors is None or error_count <= max_errors):
                logging.info("index {:5d} - Unexpected time step {:.15f} at time {:.5f}".format(index,
                                                                                                step,
                                                                                                self.times[index]))

        # Return total error count
        if verbose and error_count > 0:
            logging.info("Lightcurve had gaps at {}/{} time points.".format(error_count, len(times)))

        # Return the verdict on this lightcurve
        return error_count

    def check_fixed_step_v2(self, verbose=True, max_errors=6):
        """
        Check that this light curve is sampled at a fixed time interval. Return the number of errors.

        :param verbose:
            Should we output a logging message about every missing time point?
        :type verbose:
            bool
        :param max_errors:
            The maximum number of errors we should show
        :type max_errors:
            int
        :return:
            int
        """

        abs_tol = 1e-4
        rel_tol = 0

        spacing = self.estimate_sampling_interval()

        if verbose:
            logging.info("Time step is {:.15f}".format(spacing))

        start_time = self.times[0]
        end_time = self.times[-1]
        times = np.arange(start=start_time, stop=end_time, step=spacing)
        error_count = 0

        input_position = 0
        for index, time in enumerate(times):
            closest_time_point = self.times[input_position]
            while ((not math.isclose(time, self.times[input_position], abs_tol=abs_tol, rel_tol=rel_tol)) and
                   (time > self.times[input_position])):
                if abs(self.times[input_position] - time) < abs(closest_time_point - time):
                    closest_time_point = self.times[input_position]
                input_position += 1

            # If this time point has the correct spacing, it is OK
            if not math.isclose(time, self.times[input_position], abs_tol=abs_tol, rel_tol=rel_tol):
                if abs(self.times[input_position] - time) < abs(closest_time_point - time):
                    closest_time_point = self.times[input_position]
                if verbose and (max_errors is None or error_count <= max_errors):
                    logging.info("index {:5d} - Point missing at time {:.15f}. Closest time was {:.15f}.".
                                 format(index, self.times[index], closest_time_point))
                error_count += 1

        # Return total error count
        if verbose and error_count > 0:
            logging.info("Lightcurve had gaps at {}/{} time points.".format(error_count, len(times)))

        # Return the verdict on this lightcurve
        return error_count

    def to_fixed_step(self, verbose=True, max_errors=6):
        """
        Convert this lightcurve to a fixed time stride.

        :param verbose:
            Should we output a logging message about every missing time point?
        :type verbose:
            bool
        :param max_errors:
            The maximum number of errors we should show
        :type max_errors:
            int
        :return:
            [LightcurveFixedStep]
        """

        abs_tol = 1e-4
        rel_tol = 0

        spacing = self.estimate_sampling_interval()

        if verbose:
            logging.info("Time step is {:.15f}".format(spacing))

        start_time = self.times[0]
        end_time = self.times[-1]
        times = np.arange(start=start_time, stop=end_time, step=spacing)
        output = np.zeros_like(times)
        error_count = 0

        # Iterate over each time point in the fixed-step output lightcurve
        input_position = 0
        for index, time in enumerate(times):
            # Find the time point in the input lightcurve which is closest to this time
            closest_time_point = [self.times[input_position], self.fluxes[input_position]]
            while ((not math.isclose(time, self.times[input_position], abs_tol=abs_tol, rel_tol=rel_tol))
                   and (time > self.times[input_position])):
                if abs(self.times[input_position] - time) < abs(closest_time_point[0] - time):
                    closest_time_point = [self.times[input_position], self.fluxes[input_position]]
                input_position += 1

            if abs(self.times[input_position] - time) < abs(closest_time_point[0] - time):
                closest_time_point = [self.times[input_position], self.fluxes[input_position]]

            # If this time point has the correct spacing, it is OK
            if math.isclose(time, self.times[input_position], abs_tol=abs_tol, rel_tol=rel_tol):
                output[index] = closest_time_point[1]
                continue

            if verbose and (max_errors is None or error_count <= max_errors):
                logging.info("index {:5d} - Point missing at time {:.15f}. Closest time was {:.15f}.".
                             format(index, self.times[index], closest_time_point[0]))
            error_count += 1
            output[index] = 1

        # Return total error count
        if verbose and error_count > 0:
            logging.info("Lightcurve had gaps at {}/{} time points.".format(error_count, len(times)))

        # Return lightcurve
        return LightcurveFixedStep(
            time_start=start_time,
            time_step=spacing,
            fluxes=output
        )


class LightcurveFixedStep:
    """
    A class representing a lightcurve which is sampled on a fixed time step.
    """

    def __init__(self, time_start, time_step, fluxes, uncertainties=None, flags=None, metadata=None):
        """
        Create a lightcurve which is sampled on an arbitrary raster of times.

        :param time_start:
            The time at the start of the lightcurve.
        :type time_start:
            float
        :param time_step:
            The interval between the points in the lightcurve.
        :type time_step:
            float
        :param fluxes:
            The light fluxes at each data point.
        :type fluxes:
            np.ndarray
        :param uncertainties:
            The uncertainty in each data point.
        :type uncertainties:
            np.ndarray
        :param flags:
            The flag associated with each data point.
        :type flags:
            np.ndarray
        :param metadata:
            The metadata associated with this lightcurve.
        :type metadata:
            dict
        """

        # Check inputs
        assert isinstance(fluxes, np.ndarray)

        # Unset all flags if none were specified
        if flags is not None:
            assert isinstance(flags, np.ndarray)
        else:
            flags = np.zeros_like(fluxes)

        # Make an empty metadata dictionary if none was specified
        if metadata is not None:
            assert isinstance(metadata, dict)
        else:
            metadata = {}

        # Make uncertainty zero if not specified
        if uncertainties is not None:
            assert isinstance(uncertainties, np.ndarray)
        else:
            uncertainties = np.zeros_like(fluxes)

        # Store the data
        self.time_start = float(time_start)
        self.time_step = float(time_step)
        self.fluxes = fluxes
        self.uncertainties = uncertainties
        self.flags = flags
        self.flags_set = True
        self.metadata = metadata
