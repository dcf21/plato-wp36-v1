# Input data directory

This directory is used to store the lightcurves that are used as input into the test bench.

They are deliberately stored outside the root of the directory used for building Docker containers, so that they are not copied during the container building process (which makes the build process very slow).

Currently we use the light curve stitching group (LCSG)'s synthetic lightcurves as an input data set.

Within this directory, you should create a directory `lightcurves_v2` containing the synthetic lightcurves. The lightcurves should have the following filenames:

```
lightcurves_v2/csvs/bright/*.csv.gz
lightcurves_v2/csvs/fixedmask/*.csv.gz
lightcurves_v2/csvs/updatedmask/*.csv.gz
```

Note that the CSV files should be gzipped, which saves a lot of disk space!!