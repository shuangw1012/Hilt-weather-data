
import os
import xarray as xr
import numpy as np
import pandas as pd


import numpy as np
import pandas as pd
import xarray as xr

def Extract(df_RE):
    
    wind_location = df_RE['Name'].values
    coor_wind_x = df_RE['Lat'].values
    coor_wind_y = df_RE['Long'].values
    
    Year = [2017]  # Assuming a list even if only for one year for future scalability
    wind_location = [(lat, lon) for lat, lon in zip(coor_wind_x, coor_wind_y)]  # Assuming lat/lon lists exist
    
    for year in Year:
        year_str = str(year)
        print(f"Processing data for year: {year_str}")
        
        for input_lat, input_lon in wind_location:
            print(f"Processing data for location: {input_lat}, {input_lon}")
    
            U_req_alt = []
            V_req_alt = []
            T_req_alt = []
            p_req_alt = []
            Date_time = []
            
            for i in range(1, 13):
                month_str = "{:02}".format(i)
                print(f"Processing month: {month_str}")
    
                # File paths
                base_path = '/g/data/ob53/BARRA2/output/reanalysis/AUST-04/BOM/ERA5/historical/hres/BARRA-C2/v1/1hr'
                ua_path = f'{base_path}/ua150m/latest/ua150m_AUST-04_ERA5_historical_hres_BOM_BARRA-C2_v1_1hr_{year_str}{month_str}-{year_str}{month_str}.nc'
                va_path = f'{base_path}/va150m/latest/va150m_AUST-04_ERA5_historical_hres_BOM_BARRA-C2_v1_1hr_{year_str}{month_str}-{year_str}{month_str}.nc'
                ta_path = f'{base_path}/ta150m/latest/ta150m_AUST-04_ERA5_historical_hres_BOM_BARRA-C2_v1_1hr_{year_str}{month_str}-{year_str}{month_str}.nc'
                ps_path = f'{base_path}/ps/latest/ps_AUST-04_ERA5_historical_hres_BOM_BARRA-C2_v1_1hr_{year_str}{month_str}-{year_str}{month_str}.nc'
    
                # Load datasets
                with xr.open_dataset(ua_path) as ds_u, xr.open_dataset(va_path) as ds_v, xr.open_dataset(ta_path) as ds_T, xr.open_dataset(ps_path) as ds_p:
                    if i == 1:  # Calculate indices only once per year
                        index_lat = np.argmin(np.abs(ds_u.lat.values - input_lat))
                        index_lon = np.argmin(np.abs(ds_u.lon.values - input_lon))
    
                    # Retrieve data
                    U_req_alt.extend(ds_u.ua150m[:, index_lat, index_lon].values)
                    V_req_alt.extend(ds_v.va150m[:, index_lat, index_lon].values)
                    T_req_alt.extend(ds_T.ta150m[:, index_lat, index_lon].values - 273.15)  # Convert to Celsius
                    p_req_alt.extend(ds_p.ps[:, index_lat, index_lon].values / 1e5)  # Convert to hPa
                    Date_time.extend(pd.to_datetime(ds_u.time.values).strftime('%Y-%m-%d %H:%M:%S'))
    
            # Calculate wind direction and speed
            wind_direction = np.degrees(np.arctan2(V_req_alt, U_req_alt)) % 360
            wind_speed = np.sqrt(np.square(V_req_alt) + np.square(U_req_alt))
    
            data = {
                "DateTime": Date_time,
                "Wind Direction": wind_direction,
                "Wind Speed": wind_speed,
                "Temperature": T_req_alt,
                "Pressure": p_req_alt
            }
    
            df = pd.DataFrame(data)
            output_filename = f"BARRA-output-{input_lat}-{input_lon}-{year_str}.csv"
            df.to_csv(output_filename, index=False)
            print(f"Data saved to {output_filename}")

if __name__=='__main__':
    df = pd.read_csv(os.getcwd()+os.sep+'Grid_SA.csv')
    df_RE = df#[df['RE'] == True]
    N_cpu = 10
    num_opt = int(len(df_RE)/N_cpu)
    
    from mpi4py import MPI
    for i in range(len(df)):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        if rank == i:
            #try:
            Extract(df_RE.iloc[i*num_opt:(i+1)*num_opt])