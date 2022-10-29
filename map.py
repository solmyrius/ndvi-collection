import folium
import ee

ee.Initialize()

from kml.kmldata import KMLData


def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)


def bind_ndvi(image):
    band_ndvi = image.normalizedDifference(['B8', 'B4']).rename("NDVI")
    image = image.addBands(band_ndvi)
    return image


kml = KMLData()
cnt = kml.get_center()
lon, lat = cnt
print(cnt)

folium.Map.add_ee_layer = add_ee_layer

vis_params_ndvi = {
    'bands': ['NDVI'],
    'min': -0.2,
    'max': 0.8,
    'palette': 'FFFFFF, CE7E45, DF923D, F1B555, FCD163, 99B718, 74A901, 66A000, 529400, 3E8601, 207401, 056201, 004C00, 023B01, 012E01, 011D01, 011301'
}

s2 = ee.ImageCollection("COPERNICUS/S2_SR")
s2 = s2.map(bind_ndvi)
geometry = ee.Geometry.Point(cnt)
filtered = s2.filter(ee.Filter.date('2022-01-01', '2022-01-06')).filter(ee.Filter.bounds(geometry))

image = filtered.first()

folium_map = folium.Map(location=[lat, lon], zoom_start=12)

folium_map.add_ee_layer(image, vis_params_ndvi, 'false color composite')

for plot in kml.plots:
    fgj = folium.GeoJson(data=plot.geojson, style_function=lambda x: {"fillOpacity":0, "color": "black"})
    fgj.add_to(folium_map)
    folium.Popup(plot.id).add_to(fgj)

folium_map.save('index.html')
