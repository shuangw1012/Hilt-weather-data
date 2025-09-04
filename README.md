Project Overview

The workflow uses:BARRA-C2 reanalysis data for wind resource assessment; Himawari satellite data for solar resource assessment; PySAM for renewable generation simulations

1. Data Extraction
Wind Data: BARRA-C2 dataset on NCI
Required NCI project: ob53

Solar Data: Himawari satellite data on NCI
Required NCI project: rv74

2. Move Data Files

After successful extraction, move the resulting files into the PySAM weather data folder.

3. Run PySAM Simulation

Once data files are placed in the correct directory, run the PySAM simulation script.

4. Access Output

The simulated renewable generation time-series data will be saved in 'PySAM-python/output/'.
