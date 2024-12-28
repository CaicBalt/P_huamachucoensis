"""
PASO 1: Descarga de variables climáticas para Perú (Ejemplo simplificado)
-----------------------------------------------------------------------
En Python, no existe una función análoga exacta a geodata::worldclim_country,
por lo que este ejemplo simula la descarga manual de datos de WorldClim
y posterior recorte a Perú.
"""

import os
import requests
import rasterio
from rasterio.mask import mask
import geopandas as gpd

# 1.1. Directorio de salida
path = r"C:\Users\caice\Documents\R\ultimo\tmpr"
os.makedirs(path, exist_ok=True)

# 1.2. Shapefile de límites de Perú para enmascarar
shp_peru = r"C:\Users\caice\Documents\R\ultimo\Mapa Perú\PER_adm0.shp"
gdf_peru = gpd.read_file(shp_peru)
gdf_peru = gdf_peru.to_crs(epsg=4326)  # Asegurar proyección WGS84

# 1.3. DESCARGA manual o semiautomática
# (Se ejemplifica con uno solo; en la práctica, repetimos para 'prec', 'tmax', etc.)

worldclim_url = "https://biogeo.ucdavis.edu/data/worldclim/v2.1/base/wc2.1_30s_prec.zip"
zip_path = os.path.join(path, "wc2.1_30s_prec.zip")

if not os.path.exists(zip_path):
    print("Descargando WorldClim PREC...")
    r = requests.get(worldclim_url, stream=True)
    with open(zip_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print("Descarga completada.")

# Descomprimir y recortar sería otro paso, etc.
# 1.4. Leer ráster con rasterio y recortar, enmascarar
import zipfile
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(path)  # extrae en path

# Supón que el archivo se llama "wc2.1_30s_prec_01.tif", etc.
prec_tif = os.path.join(path, "wc2.1_30s_prec_01.tif")

with rasterio.open(prec_tif) as src:
    # Recorte
    out_image, out_transform = mask(dataset=src, shapes=gdf_peru.geometry, crop=True)
    out_meta = src.meta.copy()
    out_meta.update({
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })

# Guardar el ráster recortado
rec_prec_tif = os.path.join(path, "prec_01_peru.tif")
with rasterio.open(rec_prec_tif, "w", **out_meta) as dst:
    dst.write(out_image)
    
print("prec_01_peru.tif guardado.")

# Repetir para tmax, tmin, bioc, etc. 
# En R, tú usas geodata::worldclim_country(var='prec')..., 
# en Python hay que hacerlo manualmente o usar otra librería que provea algo similar.
