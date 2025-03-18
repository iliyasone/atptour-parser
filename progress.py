import json
from collections import defaultdict
with open('jobs.json') as f:
    jobs = json.load(f)


total = defaultdict(lambda: 0)
parsed = defaultdict(lambda: 0)
errors = defaultdict(lambda: 0)
for job in jobs:
    type = job['parsed_type']
    total[type] += 1

    if job['parsed_type'] in job['match']['parsed']:
        parsed[type] += 1
    elif job['match']['parsed']:
        errors[job['match']['parsed'][0]] += 1

for key in total:
    print(key+'\t', parsed[key], '/', total[key], '\t')

print(f'TOTAL\t\t', sum(parsed.values()),'/',len(jobs))

print('ERRORS:')
for error, count in  errors.items():
    print(error, '\t', count)