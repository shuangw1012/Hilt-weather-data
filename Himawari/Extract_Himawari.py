#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 15:25:12 2023

@author: admin-shuang
"""

import os
import xarray as xr
import numpy as np
import calendar
import pandas as pd


import os
import calendar
import numpy as np
import pandas as pd
import xarray as xr

def Extract(df_RE,index1):
    #df_RE = df_RE.iloc[:10]
    coor_PV_x = df_RE['Lat'].values
    coor_PV_y = df_RE['Long'].values
    location_coords = list(zip(coor_PV_x, coor_PV_y))
    years = [2017]

    # Initialize results per location
    location_results = [{"Lat": lat, "Long": lon} for i, (lat, lon) in enumerate(location_coords)]

    for year in years:
        print(f"\nProcessing year: {year}")
        yearly_data = {coord: {"SGI": [], "DNI": [], "SDI": []} for coord in location_coords}
        time_series_data = {coord: [] for coord in location_coords}
        for month in range(1, 13):
            month_str = f"{month:02d}"
            num_days = calendar.monthrange(year, month)[1]

            for day in range(1, num_days + 1):
                day_str = f"{day:02d}"
                print(f"  {year}-{month_str}-{day_str}")
                
                # Select correct path
                if (year > 2019) or (year == 2019 and month >= 4):
                    workdir = f'/g/data/rv74/satellite-products/arc/der/himawari-ahi/solar/p1h/latest/{year}/{month_str}/{day_str}'
                else:
                    workdir = f'/g/data/rv74/satellite-products/arc/der/himawari-ahi/solar/p1h/v1.0/{year}/{month_str}/{day_str}'

                if not os.path.exists(workdir):
                    continue

                nc_files = [f for f in os.listdir(workdir) if f.startswith("IDE02327")]

                for nc_file in nc_files:
                    file_path = os.path.join(workdir, nc_file)
                    #try:
                    with xr.open_dataset(file_path) as ds:
                        lat_vals = ds.latitude.values
                        lon_vals = ds.longitude.values

                        for coord in location_coords:
                            lat, lon = coord
                            idx_lat = np.argmin(np.abs(lat_vals - lat))
                            idx_lon = np.argmin(np.abs(lon_vals - lon))

                            sgi_val = ds.hourly_integral_of_surface_global_irradiance.values[0, idx_lat, idx_lon] * 1e6 / 3600
                            dni_val = ds.hourly_integral_of_direct_normal_irradiance.values[0, idx_lat, idx_lon] * 1e6 / 3600
                            sdi_val = ds.hourly_integral_of_surface_diffuse_irradiance.values[0, idx_lat, idx_lon] * 1e6 / 3600
                            
                            timestamp = pd.to_datetime(str(ds.time.values[0])).floor('H') 
                            #timestamp = f"{year}-{month_str}-{day_str}T{nc_file[22:24]}:00:00"  # Extract hour from filename
                            time_series_data[coord].append({
                                "time": timestamp,
                                "SGI": sgi_val,
                                "DNI": dni_val,
                                "SDI": sdi_val,
                            })

                            yearly_data[coord]["SGI"].append(sgi_val)
                            yearly_data[coord]["DNI"].append(dni_val)
                            yearly_data[coord]["SDI"].append(sdi_val)

                    #except Exception as e:
                    #    print(f"    Skipping file {nc_file} due to error: {e}")
                    #    continue

        # After one year, append to results
        for i, coord in enumerate(location_coords):
            sgi_vals = yearly_data[coord]["SGI"]
            dni_vals = yearly_data[coord]["DNI"]
            mean_sgi = np.sum(sgi_vals) #if sgi_vals else np.nan
            mean_dni = np.sum(dni_vals) #if dni_vals else np.nan
            location_results[i][f"SGI_{year}"] = mean_sgi
            location_results[i][f"DNI_{year}"] = mean_dni
    
        for coord in location_coords:
            lat, lon = coord
            ts_df = pd.DataFrame(time_series_data[coord])
        
            if not ts_df.empty:
                ts_df['time'] = pd.to_datetime(ts_df['time']).dt.floor('H')
                ts_df = ts_df.groupby('time').mean()  # Handle duplicates by averaging
        
                # Generate full hourly datetime index
                full_index = pd.date_range(f"{year}-01-01 00:00", f"{year}-12-31 23:00", freq='H')
        
                # Reindex to ensure every hour is covered
                ts_df = ts_df.reindex(full_index, fill_value=0.0)
                ts_df.fillna(0.0, inplace=True)
                ts_df.index.name = 'datetime'
        
                ts_df.to_csv(f"BOM-output-{lat}-{lon}-{year}.csv", index=True)
    
    # Save results
    #df_out = pd.DataFrame(location_results)
    #df_out.to_csv("Himawari_SGI_DNI_%s.csv"%index1, index=False)
    #print("\nSaved data to Himawari_SGI_DNI_2016_2023.csv")


if __name__=='__main__':
    df = pd.read_csv(os.getcwd()+os.sep+'Grid_SA.csv')
    df_RE = df#[df['RE'] == True]
    N_cpu = 10
    num_opt = int(len(df_RE)/N_cpu)+1
    
    from mpi4py import MPI
    for i in range(len(df)):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        if rank == i:
            #try:
            Extract(df_RE.iloc[i*num_opt:(i+1)*num_opt],i)
    
    