import json
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

matches = []
MATCH_RESULT_LIMIT = 1
LEVELUP_MATCH_DEPTH = 0
LEVELDOWN_MATCH_DEPTH = 0

rankToIntMap = {
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4,
    'V': 5,
    'VI': 6,
    'VII': 7
}

def reverseRankLookup(rankIndex):
    for key, value in rankToIntMap.items():
        if (value == rankIndex):
            return key

users_file = open('users.json')
users = json.load(users_file)
opportunities_file = open('opportunities.json')
opportunities = json.load(opportunities_file)

def brute_force_matching(users, levelup_match_depth, leveldown_match_depth):
    for opp in opportunities:
        confidence_rating = 0
        if (opp['roles'] and len(opp['roles']) > 0):
            for role in opp['roles']:
                for user in users:
                    if (user and user['interested_in'] and len(user['interested_in']) > 0):
                        # If the API query allows for mixed matches, expand scope of matching algo
                        if (levelup_match_depth or leveldown_match_depth):
                            availableRank = role.split(' ')[-1]
                            if (availableRank == 'I' or availableRank == 'II' or availableRank == 'III' or availableRank == 'IV' or availableRank == 'V'):
                                roleWordsList = role.split(' ')
                                roleWordsList.pop(-1)
                                roleTitleSansRank = " ".join(r for r in roleWordsList)
                                print('roleTitleSansRank: ' + roleTitleSansRank)
                                potentialDiagonalMatches = getRankTolerances(roleTitleSansRank, availableRank, levelup_match_depth, leveldown_match_depth)
                                for diag in potentialDiagonalMatches:
                                    if (diag['role'] in user['interested_in']):
                                        match_found(diag['confidence'], diag.role, user, opp)
                        # Process direct 1:1 matches
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

def getRankTolerances(roleTitleSansRank, baseRank, upperLimit, lowerLimit):
    baseRankIndex = 1
    if (baseRank == 'II'): baseRankIndex = 2
    if (baseRank == 'III'): baseRankIndex = 3
    if (baseRank == 'IV'): baseRankIndex = 4
    if (baseRank == 'V'): baseRankIndex = 5
    mixedRankMatches = []
    if (roleTitleSansRank is not None):
        if (upperLimit):
            numLevelUpSteps = baseRankIndex + upperLimit
            i = 0
            while(i <= numLevelUpSteps):
                i += 1
                print('next level up rank: ', getNextRank(baseRank, i, True))
                mixedRankMatches.append({
                    'role': roleTitleSansRank + getNextRank(baseRank, i, True),
                    'confidence': getNewConfidence(i, True)
                })
        if (lowerLimit):
            numLevelDownSteps = baseRankIndex - lowerLimit
            j = 0
            while(j >= numLevelDownSteps):
                j -= 1
                print('next level down rank: ', getNextRank(baseRank, j, False))
                mixedRankMatches.append({
                    'role': roleTitleSansRank + getNextRank(baseRank, j, False),
                    'confidence': getNewConfidence(i, False)
                })

    return mixedRankMatches

def getNextRank(old, diff, direction):
    # Allow upward lateral movement
    if (direction):
        return reverseRankLookup(rankToIntMap[old] + diff)
    # Allow downward lateral movement
    else:
        reverseRankLookup(rankToIntMap[old] - diff)

def getNewConfidence(diff, direction):
    if (direction):
        return 100 * (0.10 * diff)
    else:
        return 100 * (0.25 * diff)

class Matches(Resource):
    def get(self):
        args = request.args
        
        limit_to_top_results = int(args.get("limit")) or MATCH_RESULT_LIMIT
        levelup_match_depth = int(args.get("levelup")) or LEVELUP_MATCH_DEPTH
        leveldown_match_depth = int(args.get("leveldown")) or LEVELDOWN_MATCH_DEPTH

        brute_force_matching(users, levelup_match_depth, leveldown_match_depth)
        if (limit_to_top_results == 0):
            return matches
        elif (limit_to_top_results and matches and len(matches)):
            return matches[:limit_to_top_results]
        else:
            return matches[:MATCH_RESULT_LIMIT]

api.add_resource(Matches, '/matches')

if __name__ == '__main__':
    app.run(debug=True)