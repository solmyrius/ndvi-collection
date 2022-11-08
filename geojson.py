import json
from kml.kmlsource import KMLSource

kml = KMLSource()
j = kml.get_json()

f = open("plots.json", "w")
f.write(json.dumps(j, indent=4))
f.close()
