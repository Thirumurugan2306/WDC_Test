
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

data_storage = {
    'start_date': '',
    'end_date': '',
    'magPlace': [],
    'timeUrl': []
}

@app.route('/submit', methods=['POST'])
def submit():
    content = request.json
    data_storage['start_date'] = content['startDate']
    data_storage['end_date'] = content['endDate']

    date_string = f"starttime={data_storage['start_date']}&endtime={data_storage['end_date']}"
    api_call = f"http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&{date_string}&minmagnitude=4.5"
    
    response = requests.get(api_call)
    if response.status_code != 200:
        return "Error fetching data from API."
    
    data = response.json()
    features = data['features']
    
    mag_place_data = []
    time_url_data = []
    
    for feature in features:
        mag_place_data.append({
            "id": feature['id'],
            "mag": feature['properties']['mag'],
            "title": feature['properties']['title'],
            "lat": feature['geometry']['coordinates'][1],
            "lon": feature['geometry']['coordinates'][0]
        })
        time_url_data.append({
            "id": feature['id'],
            "url": feature['properties']['url'],
            "time": feature['properties']['time']
        })
    
    data_storage['magPlace'] = mag_place_data
    data_storage['timeUrl'] = time_url_data

    return jsonify({"status": "success"})

@app.route('/data')
def data():
    return jsonify({
        'magPlace': data_storage['magPlace'],
        'timeUrl': data_storage['timeUrl']
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
