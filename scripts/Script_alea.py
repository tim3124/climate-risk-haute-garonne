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

#Lecture des netCDF
nc_files = list(DATA_METEO_PATH.glob("*.nc"))

results = []

for file in nc_files:
    print(f"Traitement : {file.name}")
    
    ds = xr.open_dataset(file)
    df = ds.to_dataframe().reset_index()
    
# ---- Conversion en DataFrame horaire ----
df = ds.to_dataframe().reset_index()  # index = time
print(df.head())

#Vérification aux bonnes unités

df['ta'] = df['ta'] - 273.15
df['ta_max'] = df['ta_max'] - 273.15
df['ta_min'] = df['ta_min'] - 273.15

#Conversion en km/h
df['ws'] = df['ws'] * 3.6


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
    ta_mean=('ta','mean'),
    ta_max=('ta_max','max'),
    ta_min=('ta_min','min'),
    pre_sum=('cumul_precip','sum'),
    ws_max=('ws','max')
).reset_index()

# ---- B. Mensuel ----
monthly = df.groupby('month').agg(
    ta_mean = ('ta', 'mean'),
    ta_max = ('ta_max', 'max'),
    ta_min = ('ta_min', 'min'),
    pre_mean = ('cumul_precip','mean'),
    ws_mean = ('ws', 'mean')
).reset_index()

# ---- C. Annuel ----
annual = df.agg(
    ta_mean = ('ta', 'mean'),
    ta_max = ('ta_max', 'max'),
    ta_min = ('ta_min', 'min'),
    pre_mean = ('cumul_precip','mean'),
    ws_mean = ('ws', 'mean')
)

# ------------------------------
# Indicateurs climatiques
# ------------------------------

# Nombre de jours > 30°C
daily['hot_day'] = daily['ta_mean'] > 30
num_hot_days = daily['hot_day'].sum()

print(f"Jours chauds (>30°C) : {num_hot_days}")

# Nombre de jours precipitations > 50mm

daily['heavy_rain_day'] = daily['pre_mean'] > 30
num_heavy_rain_days = daily['heavy_rain_day'].sum()

print(f"Jours très pluvieux (>30mm) : {num_heavy_rain_days}")

# Nombre de jours avec une vitesse de vent > 100km/h

daily['heavy_wind_day'] = daily['ws_mean'] > 100
num_heavy_wind_days = daily['heavy_wind_day'].sum()

print(f"Jours très venteux (>100km/h) : {num_heavy_wind_days}")

#Jours daffilées de pluie
daily['rain_day'] = daily['pre_sum'] > 1

# Calcul séquences consécutives
daily['group'] = (daily['rain_day'] != daily['rain_day'].shift()).cumsum()
seq = daily[daily['rain_day']].groupby('group').size()

num_long_rain_sequences = (seq >= 10).sum()

#Vérification des données
daily.to_csv(OUTPUT_PATH / f"{file.stem}_daily.csv", index=False)
monthly.to_csv(OUTPUT_PATH / f"{file.stem}_monthly.csv", index=False)