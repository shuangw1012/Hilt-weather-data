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
- Access to relevant data collections (e.g. `hh5`, `rt52`, etc.)

---
## Environment setup on Gadi

Load Python on Gadi:
```bash
module load python3/3.10.0
pip install --user --upgrade pip
pip install --user -r requirements.txt
export PATH=$HOME/.local/bin:$PATH

Scripts can be run interactively for small tests:
python BARRA2/Extract_BARRA_C2.py
