# Atptour parser

Structure is a trash, but trust me its not very complicated

# How to parse?

## 1. `temp/tournaments.txt`  

first we need list of a all tournaments, actually i decided to push it on git

if you need one your could create if running 
`save_tournaments()` from `tournament_traversal.py`

## 2. `temp/traverse.json`

run `tournament_traversal.py` to get a `temp\traverse.json` file. it would contain all links to all tournaments and matches

## 3. `temp/jobs.json`

run `create_jobs.py`. it would create an actuall file with all jobs (links to a specific match data, like match-beats, or rally-analysis)

## 4 Parse!

run `run.py` to start completing jobs. 


---

run `progress.py` to see current progress

example output:

```stroke-analysis  1076 / 2979 
rally-analysis   1294 / 2979 
match-beats      2645 / 2979
court-vision     1812 / 2979
stats-keystats   2901 / 2979
stats-ytdstats   2877 / 2979
complete         0 / 2979
TOTAL            12605 / 20853
ERRORS:
ContentTypeError         4069
```