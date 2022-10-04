import ee
import json

from dataextractor import dataset

# service_account = 'arborise-ee@arborise.iam.gserviceaccount.com'
# credentials = ee.ServiceAccountCredentials(service_account, './gc_key/arborise-4044f15d5b0a.json')
# ee.Initialize(credentials)

# ee.Authenticate()
# ee.Initialize()

size = dataset.size()
size_n = size.getInfo()
print(size_n)

data_list = dataset.toList(size)

f = open("arborise_export.csv", "w")
f.write("id,date,NDVI\n")

for i in range(size_n):
    image = data_list.get(i)
    info = image.getInfo()
    prop = info["properties"]
    print(prop)

    f.write(f"{prop['id']},{prop['date']},{prop['NDVI']}\n")

f.close()

