# -*- coding: utf-8 -*-
"""
Created on Fri May  6 12:46:54 2022

@author: Ahmad Mojiri
"""
import os
import numpy as np
import json, io, requests, platform
import PySAM.Pvwattsv8 as PVWatts
import Windpower
import pandas as pd
import shutil
import pytz
from timezonefinder import TimezoneFinder 
import datetime

def solar_local(lat,long,year):
    tz = TimezoneFinder()
    timezone_str = tz.timezone_at(lat=lat, lng=long)
    timezone1 = pytz.timezone(timezone_str)
    dt = datetime.datetime.now()
    delta_t = timezone1.utcoffset(dt)
    df = pd.read_csv(os.getcwd() + os.sep + 'weather_data' + os.sep +"BOM-output-%s-%s-%s.csv"%(lat,long,int(year)))
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['datetime'] = df['datetime'] + pd.to_timedelta(delta_t)
    df = df.sort_values(by='datetime', ascending=True)
    df.set_index('datetime', inplace=True)
    new_index = pd.date_range(start='%s-01-01 00:00'%int(year), end='%s-12-31 23:00'%int(year), freq='30min')
    new_df = pd.DataFrame(index=new_index)
    new_df = new_df.join(df)
    new_df = new_df.resample('h').mean() 
    new_df['datetime'] = new_df.index
    new_df = new_df[new_df['datetime'].dt.date != pd.to_datetime('2020-02-29').date()]
    new_df['DNI'] = new_df['DNI'].fillna(0)
    new_df['GHI'] = new_df['SGI'].fillna(0)
    new_df['GDI'] = new_df['SDI'].fillna(0)
    new_df.set_index('datetime', inplace=True)
    new_df.to_csv(os.getcwd() + os.sep + 'weather_data' + os.sep + 'Solar-processed-%s-%s-%s.csv'%(lat,long,year), index=True)

def wind_local(lat,long,year):
    tz = TimezoneFinder()
    timezone_str = tz.timezone_at(lat=lat, lng=long)
    #timezone_str = tzwhere1.tzNameAt(lat, long)
    timezone1 = pytz.timezone(timezone_str)
    dt = datetime.datetime.now()
    delta_t = timezone1.utcoffset(dt)
    df = pd.read_csv(os.getcwd() + os.sep + 'weather_data' + os.sep + "BARRA-output-%s-%s-%s.csv"%(lat,long,int(year)))#,int(hub_height)))
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['DateTime'] = df['DateTime'] + pd.to_timedelta(delta_t)#pd.Timedelta(hours=time_difference_hours)
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['DateTime'] = df['DateTime'].apply(lambda dt: dt.replace(year=year)) 
    df = df.sort_values(by='DateTime', ascending=True)
    df = df[df['DateTime'].dt.date != pd.to_datetime('2020-02-29').date()]
    df.set_index('DateTime', inplace=True)
    df.to_csv(os.getcwd() + os.sep + 'weather_data' + os.sep + "BARRA-output-local-%s-%s-%s.csv"%(lat,long,int(year)), index=True)
   
    
def speed(Z,Z_anem,U_anem):
    """
    This function calculates the logarithmic wind speed as a function of 
    heigth
    
    Parameters
    ----------
    Z: height of interest
    Z_anem: anemometer heigth
    U_anem: wind speed at anemometer height

    Returns wind speed at Z
        
    """
    Z0 = 0.01
    U_H = U_anem * np.log(Z/Z0)/np.log(Z_anem/Z0)
    return(U_H)

def WindResource(lat,long,year,hub_height=150):
    """
    Generates the wind source data for SAM based on the weather data 
    that is sourced from windlab stored in WEATHER folder
    This data is based on 150m hub height
    
    Returns
    -------
    None.
    
    """
    path = os.getcwd()
    #WD_file = path + os.sep + "BARRA-output-local-%s-%s-%s-%sm.csv"%(lat,long,int(year),int(hub_height))
    WD_file = path + os.sep + 'weather_data' + os.sep + "BARRA-output-local-%s-%s-%s.csv"%(lat,long,int(year))
    
    data = pd.read_csv(WD_file)
    data_150 = data.iloc[:,[1,2,3,4]].copy()

    #data_150.Pressure=data_150.Pressure/1013.25
    data_150 = data_150.rename(columns = {'Temperature':'T',
                                        'Wind Speed':'S',
                                        'Wind Direction':'D',
                                        'Pressure':'P'})

    heading_150 = pd.DataFrame({'T':['Temperature','C',150],
                               'S':["Speed", 'm/s',150],
                               'D':["Direction",'degrees',150],
                               'P':['Pressure','atm',150]})
    #data_150 = heading_150.append(data_150).reset_index(drop=True) # I got a warning for this sentence
    data_150 = pd.concat([heading_150, data_150], ignore_index=True)
    data = data_150.copy()
    Z_anem = 150
    
    Z = 10
    data_10 = data_150.copy()
    data_10.iloc[2,:]=Z
    data_temp = data_10.iloc[3:].copy()
    S = data_temp.apply(lambda x:speed(Z, Z_anem, data_temp['S']) )

    #data_temp.S = S # this sentence does not work in my computer
    data_temp.S = S.S
    #data_10 = data_10.iloc[0:3].append(data_temp,ignore_index=True)
    data_10 = pd.concat([data_10.iloc[0:3], data_temp], ignore_index=True)
    
    data = pd.concat([data , data_10],axis=1)
    
    
    data.loc[-1] = 8*['Latitude:%s'%(lat)]
    data.index = data.index+1
    data.sort_index(inplace=True)
    data.loc[-1] = 8*['Longitude:%s'%(long)]
    data.index = data.index+1
    data.sort_index(inplace=True)
    
    
    data_text = data.to_csv(header=False, index=False, lineterminator='\n')
    text_file = open(path +  os.sep + 'input_file' + os.sep + "WindSource.srw", "w") # I got an error if use ./csv format for wind source
    text_file.write(data_text)
    text_file.close()
    #print("Wind source data file was generated from Windlab database!")


def wind_gen(lat,long,hub_height=150):
    """
    Parameters
    ----------
    Capacity will be added later

    Returns wind powr generated in W for each hour in a year
    
    """
   
    wind = Windpower.new()
    
    module = wind
    file_name = 'windfarm_windpower'
    
    with open(os.getcwd() + os.sep + 'input_file' + os.sep + file_name + ".json", 'r') as file:
        data = json.load(file)
        data['wind_resource_filename'] = os.getcwd() +  os.sep + 'input_file' + os.sep + 'WindSource.srw'
        for k,v in data.items():
            if k != "number_inputs":
                module.value(k, v)
    file.close()
    
    wind.Turbine.wind_turbine_hub_ht = hub_height
    wind.execute()
    output = np.array(wind.Outputs.gen)/320/1000
    np.savetxt(os.getcwd() + os.sep + 'output' + os.sep  + 'wind_out_%s_%s.csv'%(lat,long), output, delimiter=',')
    CF = sum(output)/8760# the reference plant size is 320 MW
    print ('wind_gen finishes, CF=%s'%CF)

def SolarResource(lat,long,year,hub_height=150):
    """
    Parameters
    ----------
    None
        
    Returns
    -------
    copies the weather data into SOLAR folder for SAM.

    """
    
    new_file = os.getcwd() + os.sep + 'input_file' + os.sep + 'SolarSource.csv'
    shutil.copy(os.getcwd() + os.sep + 'input_file' + os.sep + 'SolarSource_sample.csv', new_file)
    df = pd.read_csv(os.getcwd() + os.sep + 'input_file' + os.sep + 'SolarSource_sample.csv')
    
    WD_file = os.getcwd() + os.sep + 'weather_data' + os.sep + "Solar-processed-%s-%s-%s.csv"%(lat,long,int(year))
    data = pd.read_csv(WD_file)
    
    #WindResource(lat=-20.32,long=118.62,year=2019,hub_height=150) # use this function to get wind speed at 10m, which
    WD_file_wind = os.getcwd() + os.sep + 'weather_data' + os.sep + "BARRA-output-local-%s-%s-%s.csv"%(lat,long,int(year))
    data_wind = pd.read_csv(WD_file_wind)
    
    # PVwatts model needs a near surface wind speed, so we use the speed function to convert the wspd at hubheight to 5m. This does not reallly affect the results
    wspd_10 = speed(Z=5,Z_anem=hub_height,U_anem=data_wind['Wind Speed'].values)
    
    from timezonefinder import TimezoneFinder 
    import pytz
    import datetime
    # time zone
    tz = TimezoneFinder()
    timezone_str = tz.timezone_at(lat=lat, lng=long)
    timezone1 = pytz.timezone(timezone_str)
    dt = datetime.datetime.now()
    delta_t = timezone1.utcoffset(dt)
    
    # change lat, long, wspd, and wdir, DNI and GHI
    df.loc[0, 'lat'] = lat
    df.loc[0, 'lon'] = long
    df.loc[0, 'state'] = 'AU'  # a hard code here
    df.loc[0, 'timezone'] = delta_t
    df.loc[0, 'source'] = 'BOM'
    df.loc[2:, 'lat'] = data_wind['Wind Direction'].values
    df.loc[2:, 'lon'] = wspd_10
    df.loc[2:, 'source'] = data['DNI'].values
    df.loc[2:, 'state'] = data['GHI'].values
    df.loc[2:, 'timezone'] = data['GDI'].values
    df.loc[2:, 'country'] = data_wind['Temperature'].values
    df.to_csv(new_file, index=False)
    
def pv_gen(lat,long):
    """
    Parameters
    ----------
    Capacity will be added later

    Returns wind powr generated in W for each hour in a year
    
    """
   
    pv = PVWatts.new()
    
    module = pv
    #df = pd.read_csv(os.getcwd() + os.sep + 'SolarSource_1.csv', skiprows=0,low_memory=False)
    
    file_name = 'pvfarm_pvwattsv8'
    with open(os.getcwd() + os.sep + 'input_file' + os.sep + file_name + ".json", 'r') as file:
        data = json.load(file)
        data['solar_resource_file'] = os.getcwd() + os.sep + 'input_file' + os.sep + 'SolarSource.csv'
        for k,v in data.items():
            if k != "number_inputs":
                module.value(k, v)
        pv.execute()
        output = np.array(pv.Outputs.gen)/1/1000
    np.savetxt(os.getcwd() + os.sep + 'output' + os.sep  + 'pv_out_%s_%s.csv'%(lat,long), output, delimiter=',')
    CF = sum(output)/8760 # the reference plant size is 1 MW
    print ('pv_gen finishes, CF=%s'%CF)
    print ()

if __name__=='__main__':
    df = pd.read_csv(os.getcwd() + os.sep + 'Grid_SA.csv')
    
    # input
    Location = df['Name'].values
    year = 2019
    
    for i in range(len(Location)):
        lat = df['Lat'].values[i]
        long = df['Long'].values[i]
        
        wind_local(lat,long,year) # convert UTM to local time
        WindResource(lat,long,year) # create windpower input file
        wind_gen(lat,long) # run windpower model, this will save the hourly output in the 'wind_out.csv' file
        
        solar_local(lat,long,year) # convert UTM to local time
        SolarResource(lat,long,year) # create PVwatts input file
        pv_gen(lat,long) # run PVWatts model, this will save the hourly output in the 'pv_out.csv' file
