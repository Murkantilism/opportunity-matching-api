import json
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

matches = []
MATCH_RESULT_LIMIT = 1
LEVELUP_MATCH_DEPTH = 0
LEVELDOWN_MATCH_DEPTH = 0
MAX_CONFIDENCE_RATING = 100

levelupMatchConfidenceModifier = 0.10
leveldownMatchConfidenceModifier = 0.25

rankToIntMap = {
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4,
    'V': 5
}

def reverseRankLookup(rankIndex):
    for key, value in rankToIntMap.items():
        if (value == rankIndex):
            return key

usersFile = open('users.json')
users = json.load(usersFile)
opportunitiesFile = open('opportunities.json')
opportunities = json.load(opportunitiesFile)

def brute_force_matching(users, levelupMatchDepth, leveldownMatchDepth):
    for opp in opportunities:
        confidenceRating = 0
        if (opp['roles'] and len(opp['roles']) > 0):
            for role in opp['roles']:
                for user in users:
                    if (user and user['interested_in'] and len(user['interested_in']) > 0):
                        # If the API query allows for mixed matches, expand scope of matching algo
                        if (levelupMatchDepth or leveldownMatchDepth):
                            availableRank = role.split(' ')[-1]
                            if (availableRank == 'I' or availableRank == 'II' or availableRank == 'III' or availableRank == 'IV' or availableRank == 'V'):
                                roleWordsList = role.split(' ')
                                roleWordsList.pop(-1)
                                roleTitleSansRank = " ".join(r for r in roleWordsList)
                                potentialDiagonalMatches = getRankTolerances(roleTitleSansRank, availableRank, levelupMatchDepth, leveldownMatchDepth)
                                for diag in potentialDiagonalMatches:
                                    if (diag['role'] in user['interested_in']):
                                        matchFound(diag['confidence'], diag['role'], user, opp)
                        # Process direct 1:1 matches
                        if (role in user['interested_in']):
                            confidenceRating = MAX_CONFIDENCE_RATING
                            matchFound(confidenceRating, role, user, opp)
    
    usersFile.close()
    opportunitiesFile.close()

def matchFound(confidence, role, user, opportunity):
    matches.append({
        'confidence': confidence,
        'role_matched': role,
        'candidate_matched': user,
        'organization_matched': {
            'organization': opportunity['organization'],
            'email': opportunity['email']
        }
    })

# TODO: Implement fuzzy-matching for titles like "Assistant", "Senior", & "VP"
def getRankTolerances(roleTitleSansRank, baseRank, upperLimit, lowerLimit):
    baseRankIndex = 1
    if (baseRank == 'II'): baseRankIndex = 2
    if (baseRank == 'III'): baseRankIndex = 3
    if (baseRank == 'IV'): baseRankIndex = 4
    if (baseRank == 'V'): baseRankIndex = 5
    mixedRankMatches = []
    if (roleTitleSansRank is not None):
        if (upperLimit):
            i = baseRankIndex
            while(i < upperLimit):
                i += 1
                nextRankUp = getNextRank(baseRankIndex, i)
                mixedRankMatches.append({
                    'role': roleTitleSansRank + " " + nextRankUp,
                    'confidence': getNewConfidence(i, True)
                })
        if (lowerLimit):
            j = baseRankIndex
            while(j > lowerLimit):
                j -= 1
                nextRankDown = getNextRank(baseRankIndex, j)
                mixedRankMatches.append({
                    'role': roleTitleSansRank + " " + nextRankDown,
                    'confidence': getNewConfidence(j, False)
                })
    return mixedRankMatches

def getNextRank(old, diff):
    if (old >= rankToIntMap['V']):
        return 'V'
    elif (old < rankToIntMap['I']):
        return 'I'
    else:
        return reverseRankLookup(diff)

def getNewConfidence(diff, direction):
    if (direction):
        return MAX_CONFIDENCE_RATING * (levelupMatchConfidenceModifier * diff)
    else:
        return MAX_CONFIDENCE_RATING * (leveldownMatchConfidenceModifier * diff)

class Matches(Resource):
    def get(self):
        args = request.args
        limit_to_top_results = MATCH_RESULT_LIMIT
        levelupMatchDepth = LEVELUP_MATCH_DEPTH
        leveldownMatchDepth = LEVELDOWN_MATCH_DEPTH

        if(args.get("levelup") is not None):
            limit_to_top_results = int(args.get("limit"))
        if (args.get("levelup") is not None):
            levelupMatchDepth = int(args.get("levelup"))
        if(args.get("leveldown") is not None):
            leveldownMatchDepth = int(args.get("leveldown"))

        brute_force_matching(users, levelupMatchDepth, leveldownMatchDepth)
        if (limit_to_top_results == 0):
            return matches # unlimited results; performance not garunteed scalable
        elif (limit_to_top_results and matches and len(matches)):
            return matches[:limit_to_top_results]
        else:
            return matches[:MATCH_RESULT_LIMIT]

api.add_resource(Matches, '/matches')

if __name__ == '__main__':
    app.run(debug=True)