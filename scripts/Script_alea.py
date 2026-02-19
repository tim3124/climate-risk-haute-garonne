import netCDF4
import pandas as pd
from matplotlib import pyplot as plt
import geopandas as gpd
import numpy as np
import xarray as xr
from pathlib import Path

PROJ_PATH = Path(r"D:/8-Projet/Code/Meteo_France/climate-risk-haute-garonne")
DATA_METEO_PATH = PROJ_PATH / "data" / "raw" 
OUTPUT_PATH = PROJ_PATH / "data" / "processed"

#Lecture du netCDF
meteo_file = DATA_METEO_PATH / "31069001_TOULOUSE-BLAGNAC_MTO_1H_2024.nc"
ds = xr.open_dataset(meteo_file)

print(ds)
print(ds.dims)
print(ds.variables)

# ---- Conversion en DataFrame horaire ----
df = ds.to_dataframe().reset_index()  # index = time
print(df.head())

# ------------------------------
# 1️) Vérification qualité
# ------------------------------
print("Valeurs manquantes par variable :")
print(df.isnull().sum())

#Vérification incohérence des témpératures.
invalid_temp = df[(df['ta'] < df['ta_min']) | (df['ta'] > df['ta_max'])]
print(f"Lignes invalides températures : {len(invalid_temp)}")

# Convertir time en datetime si nécessaire
df['time'] = pd.to_datetime(df['time'])

#Ajout du champ date
df['date'] = df['time'].dt.date
df['month'] = df['time'].dt.month

# ---- A. Journalier ----
daily = df.groupby('date').agg(
    ta_mean = ('ta', 'mean'),
    ta_max = ('ta_max', 'max'),
    ta_min = ('ta_min', 'min'),
    ws_mean = ('ws', 'mean')  
).reset_index()

# ---- B. Mensuel ----
monthly = df.groupby('month').agg(
    ta_mean = ('ta', 'mean'),
    ta_max = ('ta_max', 'max'),
    ta_min = ('ta_min', 'min'),
    ws_mean = ('ws', 'mean')
).reset_index()

# ---- C. Annuel ----
annual = df.agg(
    ta_mean = ('ta', 'mean'),
    ta_max = ('ta_max', 'max'),
    ta_min = ('ta_min', 'min'),
    ws_mean = ('ws', 'mean')
)