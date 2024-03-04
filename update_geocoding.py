"""
Updates geocoding CSV files given census bureau shapefiles.

To use, download the shapefiles from the census bureau website and extract the zipfiles into the the appropriate ./shapefiles/* directory.

Files can be found at https://www.census.gov/cgi-bin/geo/shapefiles/index.php

Make sure there is only one set of .shp files in each directory.

Then, run this with `python update_geocoding.py`, which will update the CSV files in ./geocoding
"""
from typing import List
import csv
import json
import logging
import pathlib
import shapefile

logging.basicConfig(level=logging.INFO)


def find_shp_path(parent: str) -> str:
    try:
        match = next(pathlib.Path(parent).glob('**/*.shp'))
    except StopIteration:
        logging.error(f"No shapefile found in {parent}")
        raise
    return match


def extract_csv_from_shapefile(kind: str, to_extract: List[str]):
    path = find_shp_path(f'./shapefiles/{kind}/')
    with shapefile.Reader(path, 'rb') as file:
        logging.info(f"Extracting {kind} from {path}")
        example = json.dumps(file.records()[0].as_dict(),
                             indent=2,
                             sort_keys=True)
        logging.info(f'Extracting fields: {to_extract}')
        logging.info(f'Available fields: {example}')
        extracted = [
            {
                key: value
                for key, value
                in shape.record.as_dict().items()
                if key in to_extract
            }
            for shape in file
        ]
    extracted.sort(key=lambda x: x[to_extract[0]])
    with open(f'./geocoding/{kind}.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=to_extract)
        writer.writeheader()
        writer.writerows(extracted)


if __name__ == "__main__":
    extract_csv_from_shapefile('states',
                               ['NAME', 'STATEFP', 'STUSPS', 'INTPTLAT', 'INTPTLON'])
    extract_csv_from_shapefile('counties',
                               ['NAME', 'STATEFP', 'INTPTLAT', 'INTPTLON'])
