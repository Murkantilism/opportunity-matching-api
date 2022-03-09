import json
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

matches = []
MATCH_RESULT_LIMIT = 1
PROMOTION_MATCH_DEPTH = 0
DEMOTION_MATCH_DEPTH = 0
PROMOTION_MATCH_MAX = 4
DEMOTION_MATCH_MAX = 4

users_file = open('users.json')
users = json.load(users_file)
opportunities_file = open('opportunities.json')
opportunities = json.load(opportunities_file)

def brute_force_matching(users, promotion_match_depth, demotion_match_depth):
    for opp in opportunities:
        confidence_rating = 0
        if (opp['roles'] and len(opp['roles']) > 0):
            for role in opp['roles']:
                for user in users:
                    if (user and user['interested_in'] and len(user['interested_in']) > 0):
                        if (promotion_match_depth or demotion_match_depth):
                            availableRank = role.split(' ')[-1]
                            if (availableRank == 'I' or availableRank == 'II' or availableRank == 'III' or availableRank == 'IV' or availableRank == 'V'):
                                rankTolerances = getRankTolerances(availableRank, promotion_match_depth, demotion_match_depth)

                        if (role in user['interested_in']):
                            confidence_rating = 100
                            match_found(confidence_rating, role, user, opp)
    
    users_file.close()
    opportunities_file.close()

def match_found(confidence, role, user, opportunity):
    matches.append({
        'confidence': confidence,
        'role_matched': role,
        'candidate_matched': user,
        'organization_matched': {
            'organization': opportunity['organization'],
            'email': opportunity['email']
        }
    })

def getRankTolerances(baseRank, minRank, maxRank):
    
    print('baseRank: ' + baseRank)

class Matches(Resource):
    def get(self):
        args = request.args
        limit_to_top_results = args.get('limit')
        promotion_match_depth = args.get=('up') or PROMOTION_MATCH_DEPTH
        demotion_match_depth = args.get=('down') or DEMOTION_MATCH_DEPTH
        
        print('passed in up: ' + promotion_match_depth)
        
        
        # Prevent URL params from exceeding rank I -> V or V -> I match requests
        #if (promotion_match_depth > PROMOTION_MATCH_MAX):
        #    promotion_match_depth = PROMOTION_MATCH_MAX
        #if (demotion_match_depth > DEMOTION_MATCH_MAX):
        #    demotion_match_depth = DEMOTION_MATCH_MAX
        
        brute_force_matching(users, promotion_match_depth, demotion_match_depth)
        if (limit_to_top_results == 0):
            return matches
        elif (limit_to_top_results):
            return matches[:limit_to_top_results]
        else:
            return matches[:MATCH_RESULT_LIMIT]

api.add_resource(Matches, '/matches')

if __name__ == '__main__':
    app.run(debug=True)