import ee
from pykml import parser


class KMLData:
	def __init__(self):
		self.doc = None
		self.plots = []
		self._load()
		self.ee_fc = None

	def _load(self):
		f = open("data/parcelle.kml", "r")
		self.doc = parser.parse(f).getroot()
		namespace = {"kml": 'http://www.opengis.net/kml/2.2'}

		pms = self.doc.xpath(".//kml:Placemark[@id]", namespaces=namespace)
		for p in pms:
			plot_id = str(p.attrib["id"])
			if p.MultiGeometry is not None:
				for poly in p.MultiGeometry.Polygon:
					self._register_polygon(
						plot_id,
						str(poly.outerBoundaryIs.LinearRing.coordinates)
					)
			else:
				self._register_polygon(
					plot_id,
					str(p.Polygon.outerBoundaryIs.LinearRing.coordinates)
				)

	def _register_polygon(self, plot_id, coord_row):
		self.plots.append(KMLPlot(plot_id, coord_row))

	def get_fc(self):
		if self.ee_fc is None:

			ee_fc_prepared = []

			for plot in self.plots:
				ee_fc_prepared.append(ee.Feature(plot.centroid, plot.properties))
			self.ee_fc = ee.FeatureCollection(ee_fc_prepared)

		return self.ee_fc

	def get_center(self):
		fc = self.get_fc()
		center = fc.geometry().centroid().getInfo()
		return center["coordinates"]

	def get_bounds(self):
		fc = self.get_fc()
		bounds = fc.geometry().bounds().getInfo()
		return bounds["coordinates"][0]

	def get_json(self):
		return self.plots[0].geojson

	def print(self):
		for plot in self.plots:
			plot.print()


class KMLPlot:
	def __init__(self, plot_id, coord_row):
		self.id = plot_id
		self._coords = []
		coord_pairs = coord_row.split()
		for pair in coord_pairs:
			lon, lat, z = pair.split(",")
			self._coords.append([float(lon), float(lat)])
		self._polygon = ee.Geometry.Polygon([self._coords])

	@property
	def centroid(self):
		return self._polygon.centroid()

	@property
	def polygon(self):
		return self._polygon

	@property
	def ring(self):
		return self._coords

	@property
	def properties(self):
		return {"id": self.id}

	@property
	def geojson(self):
		return {
			"type": "FeatureCollection",
			"features": [self.geo_feature]
		}

	@property
	def geo_feature(self):
		return {
			"type": "Feature",
			"geometry": {
				"type": "Polygon",
				"coordinates": [self.ring]
			},
			"properties": self.properties
		}

	def print(self):
		print(self.id)
		print(self._coords)
