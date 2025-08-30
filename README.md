Project Overview

The workflow uses:

BARRA-C2 reanalysis data for wind resource assessment

Himawari satellite data for solar resource assessment

PySAM for renewable generation simulations

1. Data Extraction
Wind Data

Script: BARRA2-Extract_BARRA_C2.py

Source: BARRA-C2 dataset on NCI

Required NCI project: ob53

# Run the wind data extraction
python BARRA2-Extract_BARRA_C2.py

Solar Data

Script: Himawari-Extract_Himawari.py

Source: Himawari satellite data on NCI

Required NCI project: rv74

# Run the solar data extraction
python Himawari-Extract_Himawari.py

2. Move Data Files

After successful extraction, move the resulting files into the PySAM weather data folder.

3. Run PySAM Simulation

Once data files are placed in the correct directory, run the PySAM simulation script.

4. Access Output

The simulated renewable generation time-series data will be saved in 'PySAM-python/output/'.
