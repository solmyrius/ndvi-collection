import ee
from kml.kmldata import KMLData


def bind_ndvi(image):

    image_ndvi = image.normalizedDifference(['B8', 'B4']).rename("NDVI")
    image = image.addBands(image_ndvi)

    return image


def bind_date(image):

    img_date = ee.Number.parse(ee.Date(image.date()).format("YYYYMMDD"))
    img_date_band = ee.Image(img_date).rename("date")
    image = image.addBands(img_date_band)

    return image


def extract_points(image):

    extract_map = prepare_data_map()

    image = image.sampleRegions(
        collection=extract_map,
        scale=10
    )
    return image


def prepare_data_map():
    plots = KMLData()
    ee_fc = []

    for plot in plots.plots:
        ee_fc.append(ee.Feature(ee.Geometry.Point(plot.centroid()), plot.properties()))

    return ee.FeatureCollection(ee_fc)


ee.Initialize()

ee_fc = prepare_data_map()
print(ee_fc.getInfo())

dataset = ee.ImageCollection('COPERNICUS/S2_SR')
dataset = dataset.filterDate('2022-10-01', '2022-10-04')
dataset = dataset.map(bind_ndvi)
dataset = dataset.map(bind_date)
dataset = dataset.filterBounds(ee_fc)
dataset = dataset.select("NDVI", "date")

dataset = dataset.map(extract_points)
dataset = dataset.flatten()

