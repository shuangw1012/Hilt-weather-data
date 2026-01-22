# HILT Weather Data (NCI / Gadi Workflow)

This repository provides a reproducible workflow to build **weather datasets for renewable energy simulations**, with a focus on **high-resolution Australian reanalysis and satellite data**.

The workflow is designed to be run on **NCI Gadi**, where large meteorological datasets and high-performance compute resources are required.

---

## Project Overview

This project automates:

- Extraction of **BARRA-C2 reanalysis wind data**
- Processing of **Himawari satellite solar radiation data**
- Formatting of weather time series for **PySAM**
- Batch execution on **NCI Gadi** using PBS job scripts

It is intended for **solar, wind, and hybrid energy system modelling**.

---

## Data Sources

| Dataset | Description |
|-------|-------------|
| **BARRA-C2** | Bureau of Meteorology atmospheric reanalysis (wind, temperature, pressure) |
| **Himawari** | Geostationary satellite solar radiation products |
| **Derived outputs** | Time-aligned, simulation-ready weather time series |

> Raw datasets are **not included** in this repository and must be accessed via NCI data collections.

---

## Computing Environment

This workflow is developed and tested on:

- **NCI Gadi (PBS Pro scheduler)**
- Python **3.9+**
- Large NetCDF datasets (tens to hundreds of GB)

Users are expected to have:
- An active NCI account
- Access to relevant data collections (`ob53`, `rv74`, etc.)

---
## Environment setup on Gadi
Load Python on Gadi:
```bash
module load python3/3.10.0
pip install --user --upgrade pip
pip install --user -r requirements.txt
export PATH=$HOME/.local/bin:$PATH

Scripts can be run interactively for small tests:
cd BARRA2
python BARRA2/Extract_BARRA_C2.py

## Workflow overview

The full workflow consists of **three sequential stages**, which are typically run as **separate jobs on NCI Gadi**:
1. **BARRA2 weather data extraction** (wind-related variables)
2. **Himawari weather data processing** (solar radiation)
3. **PySAM execution** using the processed weather inputs

These stages are intentionally separated due to data volume, runtime, and different data sources.
## 1️BARRA2 processing (PBS job)
- **Year selection** is defined **inside the Python script**
- **Locations** are read from a user-provided **CSV file**
BARRA2 processing should be run via a PBS job script on Gadi due to large
input data size.
Example: qsub jobscript-BARRA-test-SW

## 2 Himawari processing (PBS job)
- **Year selection** is defined **inside the Python script**
- **Locations** are read from a user-provided **CSV file**

## 3 Preparing weather inputs for PySAM
After both BARRA2 and Himawari jobs complete successfully:
Verify that years and locations match between the two datasets;
Then manually move or copy the processed weather files into the PySAM-Python weather directory.

## 4 Running PySAM (PBS job)
Once the processed BARRA2 and Himawari weather files are in place under the PySAM-Python weather directory, the PySAM simulations should be run as
**PBS jobs on NCI Gadi**.

## Contact

If you have any questions about the workflow, data sources, or running the code
on NCI Gadi, please feel free to contact:

**Shuang Wang**  
📧 shuang.wang1@anu.edu.au
