import json
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


def process_files():
    users_file = open('users.json')
    users = json.load(users_file)
    opportunities_file = open('opportunities.json')
    opportunities = json.load(opportunities_file)

    
    # TODO: loop over/serialize files to perform matching

    users_file.close()
    opportunities_file.close()

class Matches(Resource):
    def get(self):
        return [{
            'foo': 'bar',
        }]

api.add_resource(Matches, '/matches');



if __name__ == '__main__':
    process_files()
    app.run(debug=True)