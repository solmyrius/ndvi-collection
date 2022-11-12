import folium
import ee
from ee_config import ee_auth, CLD_PRB_THRESH, DATE_START, DATE_END
from kml.kmldata import KMLData
from datasource import data_collection


ee_auth()


def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)


folium.Map.add_ee_layer = add_ee_layer


kml = KMLData()
cnt = kml.get_center()
lon, lat = cnt
print(cnt)

s2 = data_collection(DATE_START, DATE_END, CLD_PRB_THRESH)

vis_params_ndvi = {
    'bands': ['NDVI'],
    'min': -0.2,
    'max': 0.8,
    'palette': 'FFFFFF, CE7E45, DF923D, F1B555, FCD163, 99B718, 74A901, 66A000, 529400, 3E8601, 207401, 056201, 004C00, 023B01, 012E01, 011D01, 011301'
}

image = s2.first()
date = ee.Number.parse(ee.Date(image.date()).format("YYYYMMdd")).getInfo()
print(date)

clouds = image.select('clouds').selfMask()

folium_map = folium.Map(
    location=[lat, lon],
    # tiles='http://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/MapServer/tile/{z}/{y}/{x}',
    # attr='ESRI',
    zoom_start=12
    )

folium_map.add_ee_layer(image, vis_params_ndvi, 'false color composite')
folium_map.add_ee_layer(clouds, {'palette': 'e056fd'}, 'clouds')

plots = kml.get_json_background_v2()

for plot in plots:
    # fgj = folium.GeoJson(data=plot.geojson, style_function=lambda x: {"fillOpacity":0, "color": "black"})
    fgj = folium.GeoJson(data=plot, style_function=lambda x: {"fillOpacity": 0.1, "color": "red"})
    fgj.add_to(folium_map)
    folium.Popup(plot["features"][0]["properties"]["id"]).add_to(fgj)

folium_map.save(f'index_{CLD_PRB_THRESH}_{date}.html')
