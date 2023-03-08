from flask import Flask, jsonify, request, send_from_directory, send_file, render_template
from flask_cors import CORS

from profile import Profile
import simplejson as json
import random
import os
import datetime
import requests

app = Flask(__name__, static_folder='build')
CORS(app)






@app.route('/api/profile/upload', methods=['POST'])
def main():

    excel_file = request.files['file']

    profile = Profile(excel_file)

    # save profile.data as json in folder profiles-data with name profile.profile_details['Username]
    file_name = profile.profile_details['username'] + \
        str(random.randint(1, 1000000))
    file_name = ''.join(e for e in file_name if e.isalnum())

    with open('profiles-data/' + file_name + '.json', 'w') as outfile:
        json.dump(profile.data, outfile, ignore_nan=True)

    return  jsonify({'success': True, 'message': 'Profile uploaded successfully', 'file_name': file_name})


@app.route('/api/profile/<string:name>', methods=['GET'])
def get_profile(name):
    data_folder = os.path.join(os.path.dirname(__file__), 'profiles-data')
    filename = '{}.json'.format(name)
    file_path = os.path.join(data_folder, filename)

    if os.path.isfile(file_path):
        # don't return the file, return the json data
        with open(file_path) as json_file:
            data = json.load(json_file)
            return jsonify(data)
    else:
        return jsonify({'error': True, 'message': 'Profile not found'})


@app.route('/api/profile/photo/<id>')
def display_photo(id):
    file_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'profiles-photos', f'{id}.jpg')
    return send_file(file_path)


@app.route('/api/video/metadata', methods=['POST'])
def get_video_metadata():
    video_link = request.json['video_link']
    #get video meta data for example https://www.tiktok.com/oembed?url=https://www.tiktok.com/@tamatem_games/video/7205692995931327745?is_from_webapp=v1&lang=en
    #return json data
    print('getting metadata for '  + video_link)
    oembed_url = 'https://www.tiktok.com/oembed?url=' + video_link
    response = requests.get(oembed_url)

    return jsonify(response.json())



# SERVE REACT APP
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        # Serve any static files
        return send_from_directory(app.static_folder, path)
    else:
        # Serve the index.html for any non-static files
        return send_from_directory(app.static_folder, 'index.html')




if __name__ == '__main__':
    app.run(port=5002, host='0.0.0.0')
