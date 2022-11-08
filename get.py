import numpy
import io
import json
import urllib
import urllib.parse

import ee

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

KEY = "gc_key/arborise-4044f15d5b0a.json"
SERVICE_ACCOUNT = "arborise-ee@arborise.iam.gserviceaccount.com"
PROJECT = 'arborise'


ee_creds = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY)
ee.Initialize(ee_creds)

credentials = service_account.Credentials.from_service_account_file(KEY)
scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform'])

session = AuthorizedSession(scoped_credentials)

from kml.kmldata import KMLData
from datasource import data_collection
from datastorage import DS

CLD_PRB_THRESH = 10
s2 = data_collection('2022-01-01', '2022-11-06', CLD_PRB_THRESH)
kml = KMLData()

fc = kml.get_fc_polygons()

collection_size = s2.size().getInfo()
print(collection_size)

image_list = s2.toList(collection_size)

url = 'https://earthengine.googleapis.com/v1beta/projects/{}/table:computeFeatures'

for i in range(collection_size):

    image = ee.Image(image_list.get(i))

    """
    Extract NDVI
    """
    image_ndvi = image.select("NDVI")

    date = ee.Number.parse(ee.Date(image.date()).format("YYYYMMdd")).getInfo()

    computation_ndvi = image_ndvi.reduceRegions(
      collection=fc,
      reducer=ee.Reducer.mean().setOutputs(["NDVI"]),
      scale=image_ndvi.projection().nominalScale()
    )

    print(date)
    print(computation_ndvi.first().get("NDVI").getInfo())

    serialized_ndvi = ee.serializer.encode(computation_ndvi)

    response = session.post(
      url=url.format(PROJECT),
      data=json.dumps({'expression': serialized_ndvi})
    )

    ee_data = json.loads(response.content)
    for ft in ee_data["features"]:
        DS.put_ndvi_value(ft["properties"]["id"], str(date), "polygon_NDVI", ft["properties"]["NDVI"])

    """
    Extract clouds
    """
    image_clouds = image.select("probability")

    computation_clouds = image_clouds.reduceRegions(
      collection=fc,
      reducer=ee.Reducer.max().setOutputs(["probability"]),
      scale=image_clouds.projection().nominalScale()
    )

    print(date)
    print(computation_clouds.first().get("probability").getInfo())

    serialized_clouds = ee.serializer.encode(computation_clouds)

    response = session.post(
      url=url.format(PROJECT),
      data=json.dumps({'expression': serialized_clouds})
    )

    ee_data = json.loads(response.content)
    for ft in ee_data["features"]:
        DS.put_ndvi_value(ft["properties"]["id"], str(date), "polygon_max_clouds", ft["properties"]["probability"])

DS.write_csv()
