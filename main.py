import json
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

matches = []
MATCH_RESULT_LIMIT = 1
PROMOTION_MATCH_DEPTH = 0
DEMOTION_MATCH_DEPTH = 0

users_file = open('users.json')
users = json.load(users_file)
opportunities_file = open('opportunities.json')
opportunities = json.load(opportunities_file)

def brute_force_matching(users):
    
    for opp in opportunities:
        if (opp['roles'] and len(opp['roles']) > 0):
            for role in opp['roles']:
                for user in users:
                    if (user and user['interested_in'] and len(user['interested_in']) > 0):
                        if (role in user['interested_in']):
                            matches.append({ 'confidence': 100, 'role_matched': role, 'candidate_matched': user, 'organization_matched': { 'organization': opp['organization'], 'email': opp['email'] } })
    
    users_file.close()
    opportunities_file.close()

brute_force_matching(users)

def mixed_bf_matching(users):
    # TODO: Allow for matching roles where the seniority isn't a 1:1 match in exchange for reducing confidence rating

class Matches(Resource):
    def get(self):
        args = request.args
        limit_to_top_results = args.get('limit')
        promotion_match_depth = args.get=('up') or PROMOTION_MATCH_DEPTH
        demotion_match_depth = args.get=('down') or DEMOTION_MATCH_DEPTH
        
        if (promotion_match_depth and demotion_match_depth):
            
        else:
            # Direct matches only
            if (limit_to_top_results == 0):
                return matches
            elif (limit_to_top_results):
                return matches[:limit_to_top_results]
            else:
                return matches[:MATCH_RESULT_LIMIT]

api.add_resource(Matches, '/matches')

if __name__ == '__main__':
    app.run(debug=True)