import ee
from ee_config import ee_auth
from kml.kmldata import KMLData

ee_auth()


def data_collection(
        date_start,
        date_end,
        cloud_threshold
):
    def add_ndvi_band(img):
        band_ndvi = img.normalizedDifference(['B8', 'B4']).rename("NDVI")
        return img.addBands(band_ndvi)

    def add_cloud_bands(img):
        # Get s2cloudless image, subset the probability band.
        cld_prb = ee.Image(img.get('s2cloudless')).select('probability')

        # Condition s2cloudless by the probability threshold value.
        is_cloud = cld_prb.gt(cloud_threshold).rename('clouds')

        # Add the cloud probability layer and cloud mask as image bands.
        return img.addBands(ee.Image([cld_prb, is_cloud]))

    kml = KMLData()
    cnt = kml.get_center()
    lon, lat = cnt

    geometry = ee.Geometry.Point(cnt)

    date_filer = ee.Filter.date(date_start, date_end)
    geo_filter = ee.Filter.bounds(geometry)

    s2 = ee.ImageCollection("COPERNICUS/S2_SR")
    s2_filtered = s2.filter(date_filer).filter(geo_filter)

    s2_clouds = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
    s2_clouds_filtered = s2_clouds.filter(date_filer).filter(geo_filter)

    s2_combined = ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
        'primary': s2_filtered,
        'secondary': s2_clouds_filtered,
        'condition': ee.Filter.equals(**{
            'leftField': 'system:index',
            'rightField': 'system:index'
        })
    }))

    s2_combined = s2_combined.map(add_ndvi_band)
    s2_combined = s2_combined.map(add_cloud_bands)

    return s2_combined
