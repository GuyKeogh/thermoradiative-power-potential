import json
import os

import requests

locations = [(32.929, -95.770), (5, 10)]

output = r""
base_url = r"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_PAR_TOT&community=RE&longitude={longitude}&latitude={latitude}&start=20150101&end=20150305&format=JSON"

for latitude, longitude in locations:
    api_request_url = base_url.format(longitude=longitude, latitude=latitude)

    response = requests.get(url=api_request_url, verify=True, timeout=30.00)

    content = json.loads(response.content.decode("utf-8"))
    filename = response.headers["content-disposition"].split("filename=")[1]

    filepath = os.path.join(output, filename)
    with open(filepath, "w") as file_object:
        json.dump(content, file_object)
