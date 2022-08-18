from osgeo import gdal

ds = gdal.Open('T36UXF_20220630T083611_TCI_10m.jp2')
ds = gdal.Translate('T36UXF_20220630T083611_TCI_10m.tif', ds)
ds = None