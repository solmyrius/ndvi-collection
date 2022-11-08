from pykml import parser

FILE_SOURCE = "data/parcelle.kml"


class KMLSource:
	def __init__(self):
		self.doc = None
		self.plots = []
		self._load()

	def _load(self):
		f = open(FILE_SOURCE, "r")
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
		self.plots.append(KMLPlotSource(plot_id, coord_row))

	def fetch_one(self, i):
		return self.plots[i]

	def get_json(self):
		j = []
		for p in self.plots:
			j.append(p.geojson)
		return j

	def get_json_background(self):
		j = []
		for p in self.plots:
			j.append(p.geojson_background)
		return j

	def print(self):
		for plot in self.plots:
			plot.print()


class KMLPlotSource:
	def __init__(self, plot_id, coord_row):
		self.id = plot_id
		self._coords = []
		coord_pairs = coord_row.split()
		for pair in coord_pairs:
			lon, lat, z = pair.split(",")
			self._coords.append([float(lon), float(lat)])

	@property
	def ring(self):
		return self._coords

	@property
	def ring_background(self):
		w = 0.02
		c = self.centroid
		r = [
			[
				c[0] - w / 2,
				c[1] + w / 2
			],
			[
				c[0] + w / 2,
				c[1] + w / 2
			],
			[
				c[0] + w / 2,
				c[1] - w / 2
			],
			[
				c[0] - w / 2,
				c[1] - w / 2
			],
			[
				c[0] - w / 2,
				c[1] + w / 2
			],
		]
		return r

	@property
	def centroid(self):
		lngs = []
		lats = []
		for point in self._coords:
			lngs.append(point[0])
			lats.append(point[1])
		lng = (min(lngs) + max(lngs)) / 2
		lat = (min(lats) + max(lats)) / 2
		return[lng, lat]

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

	@property
	def geojson_background(self):
		return {
			"type": "FeatureCollection",
			"features": [self.geo_feature_background]
		}

	@property
	def geo_feature_background(self):
		return {
			"type": "Feature",
			"geometry": {
				"type": "MultiPolygon",
				"coordinates": [[self.ring_background],[self.ring[::-1]]]
			},
			"properties": self.properties
		}

	def print(self):
		print(self.id)
		print(self._coords)
