from pykml import parser
from ee_config import SOURCE_KML_FILE


class KMLSource:
	def __init__(self):
		self.doc = None
		self.plots = []
		self._load()

	def _load(self):
		f = open(SOURCE_KML_FILE, "r")
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

	def get_json_background_v2(self):
		"""
		Builds square background with deduction of other polygons in set, which
		not intersects the border
		"""
		j = []
		for p in self.plots:
			square = p.bg_georing
			mp_rings = []
			mp_rings.append(square.ring)

			for pp in self.plots:
				if square.has_inside(pp.georing):
					r = pp.georing.ring
					mp_rings.append(r[::-1])

			fc = {
				"type": "FeatureCollection",
				"features": [
					{
						"type": "Feature",
						"geometry": {
							"type": "MultiPolygon",
							"coordinates": [mp_rings]
						},
						"properties": p.properties
					}
				]
			}
			j.append(fc)
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
			lng, lat, z = pair.split(",")
			self._coords.append([float(lng), float(lat)])
		self._georing = GeoRing(self._coords)
		self._bg_georing = None

	@property
	def ring(self):
		return self._coords

	@property
	def ring_background(self):
		return self.bg_georing.ring

	@property
	def georing(self):
		return self._georing

	@property
	def bg_georing(self):
		if self._bg_georing is None:
			w = 0.005
			c = self.centroid
			self._bg_georing = GeoRing(
				[
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
			)
		return self._bg_georing

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
				"coordinates": self.background_multipolygon
			},
			"properties": self.properties
		}

	@property
	def background_multipolygon(self):
		return [[self.ring_background], [self.ring[::-1]]]

	def print(self):
		print(self.id)
		print(self._coords)


class GeoRing:
	def __init__(self, coords):
		self._coords = coords

		self.lats = []
		self.lngs = []

		for pair in self._coords:
			self.lngs.append(pair[0])
			self.lats.append(pair[1])

		self._bounds = {
			'min': {
				'lat': min(self.lats),
				'lng': min(self.lngs)
			},
			'max': {
				'lat': max(self.lats),
				'lng': max(self.lngs)
			}
		}

	@property
	def ring(self):
		return self._coords

	@property
	def bounds(self):
		return self._bounds

	def has_inside(self, gr):
		if gr.bounds["min"]["lat"] > self.bounds["min"]["lat"] \
			and gr.bounds["max"]["lat"] < self.bounds["max"]["lat"] \
			and gr.bounds["min"]["lng"] > self.bounds["min"]["lng"] \
			and gr.bounds["max"]["lng"] < self.bounds["max"]["lng"]:
			return True
		else:
			return False

	def is_bounds_intersects(self, gr):
		if self.has_inside(gr) or gr.has_inside(self):
			return True
		else:
			return False
