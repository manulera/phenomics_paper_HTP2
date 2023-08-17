import pandas
import json

# prints mappings to html file to double check

data = pandas.read_csv('results/full_mappings.tsv', sep='\t')
spreadsheet = pandas.read_excel('data/SupplementaryFile1.xlsx', sheet_name='Key to conditions')

data = data.merge(spreadsheet[['Abbreviation', 'Description']], left_on='condition', right_on='Abbreviation', how='left')

# Load fyeco
with open('results/fyeco.json') as ins:
    fyeco = json.load(ins)

out_file = ''

for i, row in data.iterrows():

    fyeco_string = ''
    for chunk in row['fyeco_terms'].split(','):
        if '(' in chunk:
            value = chunk.split('(')[1].split(')')[0]
            term = chunk.split('(')[0].strip()
            fyeco_string += f'<li>{term} ({fyeco[term]}) - {value}</li>\n'
        else:
            fyeco_string += f'<li>{chunk.strip()} ({fyeco[chunk.strip()]})</li>\n'
    out_file += f'''
    <h2>{row['condition']} - {row['Description']}</h2>
    <ul>
        <li>Sensitive: {row['sensitive_label']}</li>
        <li>Resistant: {row['resistance_label']}</li>
        {fyeco_string}
    </ul>
    '''

with open('results/check_mappings.html', 'w') as out:
    out.write(out_file)