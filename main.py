import ee
import json
import csv

from dataextractor import dataset

# service_account = 'arborise-ee@arborise.iam.gserviceaccount.com'
# credentials = ee.ServiceAccountCredentials(service_account, './gc_key/arborise-4044f15d5b0a.json')
# ee.Initialize(credentials)

# ee.Authenticate()
# ee.Initialize()

data_keys = [
    "id",
    "date",
    "point_NDVI",
    "polygon_NDVI",
    "background_NDVI"
]


def load_csv():
    f = open("arborise_data.csv", "r")
    csv_data = {}
    csv_reader = csv.DictReader(f)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            pass
        else:
            csv_data[row["id"]+"-"+row["date"]] = row
        line_count += 1
    return csv_data


def write_csv_param(data_list, param):

    # csv_data = load_csv()
    csv_data = {}

    f = open("arborise_data.csv", "w")
    f.write(",".join(data_keys) + "\n")

    for info in data_list:
        prop = info["properties"]
        key = str(prop["id"])+"-"+str(prop["date"])
        if key not in csv_data:
            csv_data[key] = {
                "id": prop["id"],
                "date": prop["date"]
            }
        csv_data[key][param] = prop["NDVI"]

    for key in csv_data:
        row = []
        for dk in data_keys:
            if dk in csv_data[key]:
                row.append(str(csv_data[key][dk]))
            else:
                row.append("")
        f.write(",".join(row)+"\n")

    f.close()


def data_extract(ee_dataset):

    res = []

    size = ee_dataset.size()
    size_n = size.getInfo()
    print(size_n)
    data_list = ee_dataset.toList(size)

    for i in range(size_n):
        image = data_list.get(i)
        info = image.getInfo()
        prop = info["properties"]
        print(prop)
        res.append(info)

    return res


data = data_extract(dataset)
write_csv_param(data, "polygon_NDVI")
print(json.dumps(data, indent=4))
