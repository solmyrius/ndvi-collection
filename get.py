import json
import ee

from ee_config import ee_auth, ee_session_init, PROJECT, DATE_START, DATE_END
from kml.kmldata import KMLData
from datasource import data_collection
from datastorage import DS

ee_auth()
ee_session = ee_session_init()
URL_COMPUTE = 'https://earthengine.googleapis.com/v1beta/projects/{}/table:computeFeatures'


class DataGetter:
    def __init__(self, date_start, date_end, cloud_threshold=100):
        self.cloud_threshold = cloud_threshold
        self.date_start = date_start
        self.date_end = date_end
        self.kml = KMLData()
        self.s2_collection = None
        self.prepare_collection()

    def prepare_collection(self):

        self.s2_collection = data_collection(
            self.date_start,
            self.date_end,
            self.cloud_threshold
        )

    def get_size(self):

        return self.s2_collection.size().getInfo()

    def extract_ndvi_plot(self):

        fc = self.kml.get_fc_polygons()
        self.extract_ndvi(fc, "polygon_NDVI")

    def extract_ndvi_background(self):

        fc = self.kml.get_fc_background_polygons()
        self.extract_ndvi(fc, "background_NDVI")

    def extract_clouds_plot(self):

        fc = self.kml.get_fc_polygons()
        self.extract_clouds(fc, "polygon_max_clouds")

    def extract_clouds_background(self):

        fc = self.kml.get_fc_background_polygons()
        self.extract_clouds(fc, "background_max_clouds")

    def extract_ndvi(self, fc, ds_key):

        collection_size = self.get_size()
        image_list = self.s2_collection.toList(collection_size)

        for i in range(collection_size):

            image = ee.Image(image_list.get(i))
            image_ndvi = image.select("NDVI")

            date = ee.Number.parse(
                ee.Date(image.date()).format("YYYYMMdd")
            ).getInfo()

            computation = image_ndvi.reduceRegions(
                collection=fc,
                reducer=ee.Reducer.mean().setOutputs(["NDVI"]),
                scale=image_ndvi.projection().nominalScale()
            )

            print(date)
            print(computation.first().get("NDVI").getInfo())

            serialized_ndvi = ee.serializer.encode(computation)

            response = ee_session.post(
                url=URL_COMPUTE.format(PROJECT),
                data=json.dumps({'expression': serialized_ndvi})
            )

            ee_data = json.loads(response.content)
            for ft in ee_data["features"]:
                DS.put_ndvi_value(
                    ft["properties"]["id"],
                    str(date),
                    ds_key,
                    ft["properties"]["NDVI"]
                )
                DS.put_ndvi_value(
                    ft["properties"]["id"],
                    str(date),
                    "id_parcel",
                    ft["properties"]["id_parcel"]
                )

    def extract_clouds(self, fc, ds_key):

        collection_size = self.get_size()
        image_list = self.s2_collection.toList(collection_size)

        for i in range(collection_size):

            image = ee.Image(image_list.get(i))

            image_clouds = image.select("probability")

            date = ee.Number.parse(
                ee.Date(image.date()).format("YYYYMMdd")
            ).getInfo()

            computation = image_clouds.reduceRegions(
                collection=fc,
                reducer=ee.Reducer.max().setOutputs(["probability"]),
                scale=image_clouds.projection().nominalScale()
            )

            print(date)
            print(computation.first().get("probability").getInfo())

            serialized_clouds = ee.serializer.encode(computation)

            response = ee_session.post(
                url=URL_COMPUTE.format(PROJECT),
                data=json.dumps({'expression': serialized_clouds})
            )

            ee_data = json.loads(response.content)
            for ft in ee_data["features"]:
                DS.put_ndvi_value(
                    ft["properties"]["id"],
                    str(date),
                    ds_key,
                    ft["properties"]["probability"]
                )
                DS.put_ndvi_value(
                    ft["properties"]["id"],
                    str(date),
                    "id_parcel",
                    ft["properties"]["id_parcel"]
                )

    @staticmethod
    def data_save():
        DS.write_csv()

    def run(self):
        self.extract_ndvi_plot()
        self.extract_clouds_plot()
        self.extract_ndvi_background()
        self.extract_clouds_background()


DG = DataGetter(
    date_start=DATE_START,
    date_end=DATE_END
)

DG.run()
DG.data_save()
