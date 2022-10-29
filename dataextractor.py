import ee
from kml.kmldata import KMLData


def bind_ndvi(image):

    image_ndvi = image.normalizedDifference(['B8', 'B4']).rename("NDVI")
    image = image.addBands(image_ndvi)

    return image


def bind_date(image):

    img_date = ee.Number.parse(ee.Date(image.date()).format("YYYYMMdd"))
    img_date_band = ee.Image(img_date).rename("date")
    image = image.addBands(img_date_band)

    return image


def extract_points(image):

    image = image.sampleRegions(
        collection=prepare_data_map_centroid(),
        scale=10
    )
    return image


def extract_polygons(image):

    image = image.sampleRegions(
        collection=prepare_data_map_polygon(),
        scale=10
    )
    return image


def prepare_data_map_centroid():
    plots = KMLData()
    ee_fc_prepared = []

    data_plots = plots.plots[0:3:]

    for plot in data_plots:
        ee_fc_prepared.append(ee.Feature(plot.centroid, plot.properties))

    return ee.FeatureCollection(ee_fc_prepared)


def prepare_data_map_polygon():
    plots = KMLData()
    ee_fc_prepared = []

    data_plots = plots.plots[0:1:]

    for plot in data_plots:
        ee_fc_prepared.append(ee.Feature(plot.polygon, plot.properties))

    return ee.FeatureCollection(ee_fc_prepared)


ee.Initialize()

ee_fc = prepare_data_map_centroid()
print(ee_fc.getInfo())

dataset = ee.ImageCollection('COPERNICUS/S2_SR')
dataset = dataset.filterDate('2022-10-01', '2022-10-05')
dataset = dataset.map(bind_ndvi)
dataset = dataset.map(bind_date)
dataset = dataset.filterBounds(ee_fc)
dataset = dataset.select("NDVI", "date")

# dataset = dataset.map(extract_points)
dataset = dataset.map(extract_polygons)
dataset = dataset.flatten()

