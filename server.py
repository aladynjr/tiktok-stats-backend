from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS

from profile import Profile
import simplejson as json
import random
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/profile/upload', methods=['POST'])
def main():

    excel_file = request.files['file']

    profile = Profile(excel_file)

    #save profile.data as json in folder profiles-data with name profile.profile_details['Username]
    file_name = profile.profile_details['Username:'] + str(random.randint(1, 1000000))
    file_name = ''.join(e for e in file_name if e.isalnum())

    with open('profiles-data/' + file_name +'.json', 'w') as outfile:
        json.dump(profile.data, outfile, ignore_nan=True)

    return json.dumps(profile.data, ignore_nan=True)



@app.route('/api/profile/<string:name>', methods=['GET'])
def get_profile(name):
    data_folder = os.path.join(os.path.dirname(__file__), 'profiles-data')
    filename = '{}.json'.format(name)
    file_path = os.path.join(data_folder, filename)

    if os.path.isfile(file_path):
        #don't return the file, return the json data 
        with open(file_path) as json_file:
            data = json.load(json_file)
            return jsonify(data)
    else:
        return jsonify({'error': True, 'message': 'Profile not found'})

@app.route('/api/profile/photo/<id>')
def display_photo(id):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles-photos', f'{id}.jpg')
    return send_file(file_path)


if __name__ == '__main__':
    app.run(debug=True, port=8080)


