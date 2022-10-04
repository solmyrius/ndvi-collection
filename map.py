import folium

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

# image = ee.Image('LANDSAT/LC08/C02/T1_TOA/LC08_044034_20140318')

visParams_ndvi = {
    'min': -0.2,
    'max': 0.8,
    'palette': 'FFFFFF, CE7E45, DF923D, F1B555, FCD163, 99B718, 74A901, 66A000, 529400, 3E8601, 207401, 056201, 004C00, 023B01, 012E01, 011D01, 011301'
}

# Define the visualization parameters.
image_viz_params = {
    'bands': ['B4', 'B3', 'B2'],
    # 'min': 0,
    # 'max': 0.3
    # 'gamma': [0.95, 1.1, 1]
}

# Define a map centered on San Francisco Bay.
map_l8 = folium.Map(location=[37.8719, -122.262], zoom_start=10)


# Add the image layer to the map and display it.
#map_l8.add_ee_layer(first, image_viz_params, 'false color composite')
map_l8.add_ee_layer(image_ndvi, visParams_ndvi, 'false color composite')
map_l8.save('index.html')
