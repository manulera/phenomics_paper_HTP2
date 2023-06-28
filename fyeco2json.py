import json

out_dict = dict()

with open('data/fyeco.obo') as ins:
    last_id = ''
    for line in ins:
        l = line.strip()
        if l.startswith('id:'):
            last_id = l.split(' ')[1]
        if l.startswith('name:'):
            out_dict[last_id] = ' '.join(l.split(' ')[1:])

# Write the out_dict to json file
with open('results/fyeco.json', 'w') as out:
    json.dump(out_dict, out, indent=4)