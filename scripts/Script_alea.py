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