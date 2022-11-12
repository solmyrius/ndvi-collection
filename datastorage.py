import csv
from ee_config import DATA_FILE

data_keys = [
    "id",
    "date",
    "polygon_NDVI",
    "polygon_max_clouds",
    "background_NDVI",
    "background_max_clouds",
]


class DataStorage:
    def __init__(self):
        self._data = {}
        self._load_csv()

    def _load_csv(self):
        try:
            f = open(DATA_FILE, "r")
            csv_reader = csv.DictReader(f)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    pass
                else:
                    self._data[row["id"]+"-"+row["date"]] = row
                line_count += 1
        except FileNotFoundError:
            pass

    def put_ndvi_value(self, plot_id, date, key, value):
        row_id = plot_id+"-"+date
        if row_id not in self._data:
            self._data[row_id] = {
                "id": plot_id,
                "date": date
            }
        self._data[row_id][key] = value

    def write_csv(self):
        f = open(DATA_FILE, "w")
        f.write(",".join(data_keys) + "\n")

        for row_id in self._data:
            row = []
            for dk in data_keys:
                if dk in self._data[row_id]:
                    row.append(str(self._data[row_id][dk]))
                else:
                    row.append("")
            f.write(",".join(row)+"\n")

        f.close()


DS = DataStorage()
