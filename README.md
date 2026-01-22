# 🌤️ HILT Weather Data

This repository provides a workflow to build **weather datasets suitable for renewable energy simulations**.  
It automates the extraction, processing, and formatting of meteorological data for use in tools such as **PySAM**.

---

## 📍 Project Overview

The workflow supports:

- Extraction of **BARRA-C2 reanalysis wind data**
- Processing of **Himawari satellite solar data**
- Organisation of outputs for **PySAM**

This project was developed in the context of **HILT CRC Energy Infrastructure project (RP3.007)**, but is designed to be reusable by others.

---

## 🌏 Data Sources

| Dataset | Description |
|-------|-------------|
| **BARRA-C2** | High-resolution atmospheric reanalysis data (wind, pressure, temperature) |
| **Himawari** | Geostationary satellite solar radiation products |
| **Derived outputs** | Time-aligned weather series formatted for PySAM |

> ⚠️ Raw datasets are large and are **not stored in this repository**.

---

## 💻 Requirements

- Python **3.8+**
- Common scientific Python libraries (`numpy`, `pandas`, `xarray`, etc.)
- Access to BARRA and Himawari datasets
- (Optional) **PySAM** for downstream simulations

Install dependencies:

```bash
pip install -r requirements.txt
