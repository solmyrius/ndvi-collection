import ee
from kml.kmlsource import KMLSource

ee.Initialize()


class KMLData(KMLSource):
	def __init__(self):
		super().__init__()
		self.ee_fc_polygons = None
		self.ee_fc_background_polygons = None

	def get_fc_polygons(self):
		if self.ee_fc_polygons is None:

			ee_fc_prepared = []

			for plot in self.plots:
				ee_poly = ee.Geometry.Polygon(plot.ring)
				ee_fc_prepared.append(ee.Feature(ee_poly, plot.properties))

			self.ee_fc_polygons = ee.FeatureCollection(ee_fc_prepared)

		return self.ee_fc_polygons

	def get_fc_background_polygons(self):
		if self.ee_fc_background_polygons is None:
			ee_fc_prepared = []
			bg_json = self.get_json_background_v2()
			for fc in bg_json:
				ft = fc["features"][0]
				rings = ft["geometry"]["coordinates"]
				ee_poly = ee.Geometry.MultiPolygon(rings)
				ee_fc_prepared.append(ee.Feature(ee_poly, ft["properties"]))

			self.ee_fc_background_polygons = ee.FeatureCollection(ee_fc_prepared)

		return self.ee_fc_background_polygons

	def get_center(self):
		fc = self.get_fc_polygons()
		center = fc.geometry().centroid().getInfo()
		return center["coordinates"]

	def get_bounds(self):
		fc = self.get_fc_polygons()
		bounds = fc.geometry().bounds().getInfo()
		return bounds["coordinates"][0]

	def get_ee_plot(self, i):
		return ee.Geometry.Polygon(self.fetch_one(i).ring)
