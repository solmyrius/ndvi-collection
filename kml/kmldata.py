from pykml import parser


class KMLData:
	def __init__(self):
		self.doc = None
		self.plots = []
		self._load()

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

	def print(self):
		for plot in self.plots:
			plot.print()


class KMLPlot:
	def __init__(self, plot_id, coord_row):
		self.id = plot_id
		self.coords = []
		coord_pairs = coord_row.split()
		for pair in coord_pairs:
			lon, lat, z = pair.split(",")
			self.coords.append([float(lon), float(lat)])

	def centroid(self):
		return self.coords[0]

	def properties(self):
		return {"id": self.id}

	def print(self):
		print(self.id)
		print(self.coords)
