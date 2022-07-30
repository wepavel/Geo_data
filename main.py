import folium
import geopandas as gpd
from sentinelsat.sentinel import SentinelAPI
import rasterio
import matplotlib.pyplot as plt
from rasterio import plot
from rasterio.plot import show
from rasterio.mask import mask
from osgeo import gdal
import os
import time
from zipfile import ZipFile
import numpy as np


def download_by_uuid(uuid, gdf):
    uuid_list = list(gdf.uuid)

    # index, = uuid_list.index("1610e62a-1d4a-4eb1-bdda-1e054e5f1550")
    index = 0
    for i, j in enumerate(uuid_list):
        if j == uuid:
            index = j
            break
    cur_uuid = gdf.uuid[index]
    ident = gdf.identifier[index]
    granule = gdf.granuleidentifier[index]
    datastrip = gdf.datastripidentifier[index]
    # print(cur_uuid, ident, cur_uuid, granule, datastrip)

    parts1 = ident.split('_')
    parts2 = datastrip.split('_')
    parts3 = granule.split('_')

    parts2[7] = parts2[7].replace(parts2[7][0], '')

    for i in range(2,5):
        path = []
        path.append(cur_uuid)
        path.append(ident)
        path.append(f"{parts2[3]}_{parts1[5]}_{parts3[7]}_{parts2[7]}")
        path.append(f"{parts1[5]}_{parts1[2]}_B0{i}_10m.jp2")


        XXX = api.session.get(
            f"https://scihub.copernicus.eu/dhus/odata/v1/Products('{path[0]}')/Nodes('{path[1]}.SAFE')/Nodes('GRANULE')/Nodes('{path[2]}')/Nodes('IMG_DATA')/Nodes('R10m')/Nodes('{path[3]}')/$value")
        if XXX.status_code == 200:

            if not os.path.exists(f"download_images/{uuid}"):
                os.makedirs(f"download_images/{uuid}")
            with open(f"download_images/{uuid}/B0{i}_10m.jp2", 'wb') as f:
                f.write(XXX.content)


def show_prewiev(uuid):

    # XXX = api.session.get(f"https://scihub.copernicus.eu/dhus/odata/v1/Products('{uuid}')/Products('Quicklook')/$value")

    print(f"https://scihub.copernicus.eu/dhus/odata/v1/Products('{uuid}')/Products('Quicklook')/$value")

cur_dir = os.getcwd()

Json_dir=f'{cur_dir}/GEOJsons/Russia.geojson'



m = folium.Map([36.2754, 54.5293], zoom_start=30)

boundary = gpd.read_file(Json_dir)
folium.GeoJson(boundary).add_to(m)

print(boundary['geometry'])
footprint = None
j=0
for i in boundary['geometry']:
    print(i)
    if j == 0:

        footprint = i
        j += 1




user = 'wepaul'
password = 'Sporopedu123'
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

products = api.query(footprint,
                     date = ('20220109', '20220710'),
                     platformname = 'Sentinel-2',
                     processinglevel = 'Level-2A',
                     cloudcoverpercentage = (0, 20))


gdf = api.to_geodataframe(products)
gdf_sorted = gdf.sort_values(['cloudcoverpercentage'], ascending=[True])

print(gdf_sorted.uuid)


need_uuid = input('Введите uuid из списка')

show_prewiev(need_uuid)

# download_by_uuid(need_uuid, gdf_sorted)


# T37UCA_20220205T084039_B03_10m.jp2




# https://scihub.copernicus.eu/dhus/odata/v1/Products('b246fb51-6c43-454a-bf49-385f5688bf63')/Nodes('S2B_MSIL2A_20220205T084039_N0400_R064_T37UCA_20220205T105847.SAFE')/Nodes('GRANULE')/Nodes('L2A_T37UCA_A025687_20220205T084305')/Nodes('IMG_DATA')/Nodes('R10m')/Nodes

# for uuid in gdf_sorted['uuid']:
#     api.download(uuid, directory_path=f"{cur_dir}/download_archives")

# zip_folders = os.listdir(f'{cur_dir}/download_archives/')
#
# with ZipFile(f'{cur_dir}/download_archives/{zip_folders[0]}', 'r') as zipObj:
#     listOfFileNames = zipObj.namelist()
#     print(listOfFileNames)
#
#     fileName = 'S2A_MSIL2A_20220414T084601_N0400_R107_T37UCA_20220419T125402.SAFE/GRANULE/L2A_T37UCA_A035568_20220414T084601/IMG_DATA/R10m/T37UCA_20220414T084601_B02_10m.jp2'
#
#     zipObj.extract(fileName, f'{cur_dir}/unzipped_files/')

# for names in zip_folders

# bands = r'/Users/wepal/Work/22_07_21_Geo_data/S2A_MSIL2A_20220623T084611_N0400_R107_T36UXF_20220623T133711.SAFE/GRANULE/L2A_T36UXF_A036569_20220623T085454/IMG_DATA/R10m'
# blue = rasterio.open(bands+'/T36UXF_20220623T084611_B02_10m.jp2')
# green = rasterio.open(bands+'/T36UXF_20220623T084611_B03_10m.jp2')
# red = rasterio.open(bands+'/T36UXF_20220623T084611_B04_10m.jp2')
#
# # # /T37UCA_20220205T084039_B04_10m.jp2
# #
# with rasterio.open('image_name.tiff','w',driver='Gtiff', width=blue.width, height=blue.height, count=3, crs=blue.crs,transform=blue.transform, dtype=blue.dtypes[0]) as rgb:
#     rgb.write(blue.read(1),3)
#     rgb.write(green.read(1),2)
#     rgb.write(red.read(1),1)
#     rgb.close()
#
#
# check = rasterio.open('image_name.tiff')
# check.crs
#
# bound_crs = boundary.to_crs({'init': 'epsg:32637'})
# with rasterio.open("image_name.tiff") as src:
#     out_image, out_transform = mask(src,
#                                     bound_crs.geometry, crop=True)
#     out_meta = src.meta.copy()
#     out_meta.update({"driver": "GTiff",
#                      "height": out_image.shape[1],
#                      "width": out_image.shape[2],
#                      "transform": out_transform})
#
# with rasterio.open("masked_image.tif", "w", **out_meta) as final:
#     final.write(out_image)
#
# src = rasterio.open(r'masked_image.tif')
# plt.figure(figsize=(10, 10))
# plt.title('Final Image')
# plot.show(src, adjust='linear')