# opportunity-matching-api
Implements a solution for an API matching endpoint exercise (details & test data are behind an NDA)

# Test
Issue `python -m unittest tests.py` in command line

**NOTE:** you must have test data defined locally inside of `users.json` and `opportunities.json` which are not committed to source

# Run
1. Build the server by issuing `python main.py` in command line
1. In a second CLI, issue `curl localhost:5000/matches` to run the matching algorithm with default configurations

# Run Options | Query Parameters

1. __limit:__ returns the top N matches based on input; set to 0 for unlimited results (warning: performance not yet garunteed)
1. __levelup:__ experimental feature to allow mixed rank matching N seniority ranks above the one a company is looking to fill (ie: the candidate would experience career growth if hired), at the expense of a lower confidence rating
1. __leveldown:__ same as levelup but for seniority ranks below, at a slightly greater expense to confidence rating than a levelup

Sample query:

```
curl "localhost:5000/matches?limit=500&levelup=1&leveldown=2"
```