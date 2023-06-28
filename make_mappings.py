import pandas
import re
import json

with open('data/fypo.json') as ins:
    fypo_raw = json.load(ins)['graphs'][0]['nodes']


fypo = dict()

for node in fypo_raw:
    if 'lbl' in node:
        fypo[node['id'].split('/')[-1].replace('_',':')] = node['lbl']

# Read in the data
data = pandas.read_excel('data/SupplementaryFile1.xlsx', sheet_name='Key to conditions')
data.fillna('', inplace=True)

# strip all the columns
for col in data.columns:
    if data[col].dtype == 'object':
        data[col] = data[col].str.strip()

data.rename(columns={'Abbreviation':'condition'}, inplace=True)

resistance_terms = list()
sensitive_terms = list()
resistance_term_names = list()
sensitive_term_names = list()
for condition, fypo_terms_string in zip(data['condition'], data['FYPO_term']):
    fypo_terms = re.findall('FYPO:\d+',fypo_terms_string)
    sensitive_term = None
    resistance_term = None
    sensitive_term_name = None
    resistance_term_name = None

    for term_id in fypo_terms:
        term_name = fypo[term_id]

        # Assign term to resistant or sensitive
        if 'sensitive' in term_name or 'decreased' in term_name or 'reduced' in term_name or 'loss' in term_name:
            sensitive_term = term_id
            sensitive_term_name = term_name
        if 'resistance' in term_name or 'increased' in term_name:
            resistance_term = term_id
            resistance_term_name = term_name
    if sensitive_term is None or resistance_term is None:
        print(fypo_terms)
        exit(0)
    sensitive_terms.append(sensitive_term)
    sensitive_term_names.append(sensitive_term_name)
    resistance_terms.append(resistance_term)
    resistance_term_names.append(resistance_term_name)


data['sensitive'] = sensitive_terms
data['resistance'] = resistance_terms

data['sensitive_label'] = sensitive_term_names
data['resistance_label'] = resistance_term_names

# Map the temperature
def map_temperature(temp):
    temp = int(temp)
    if temp > 32:
        return f'FYECO:0000004({temp}C)'
    elif temp < 25:
        return f'FYECO:0000006({temp}C)'
    else:
        return f'FYECO:0000005({temp}C)'

data['temperature'] = data['temperature'].apply(map_temperature)

# Map the rest of conditions, where they are not empty, and don't ocintain a space or ()
logi = (data['Other condition'] != '') & ~data['Other condition'].str.contains('(',regex=False) & ~data['Other condition'].str.contains(',')

data.loc[logi, 'Other condition'] = data.loc[logi, :].apply(lambda r: f'{r["Other condition"]}({r["Dose_units"]})', axis=1)

# Concatenate Medium, Other condition, and temperature
def concat_fun(r):
    value = ','.join( x for x in list(r.values) if x != '').strip()
    value = re.sub('\s+FYECO', 'FYECO', value)
    value = re.sub('\s+', ' ', value)
    return value

data['fyeco_terms'] = data[['Medium', 'Other condition', 'temperature']].apply(concat_fun, axis=1)

cols = ['condition', 'sensitive', 'resistance', 'sensitive_label', 'resistance_label', 'fyeco_terms']

data[cols].to_csv('results/full_mappings.tsv', index=False, sep='\t')

# Repeated rows
duplicated_data = data[data.duplicated(subset=cols[1:], keep=False)].sort_values('fyeco_terms')

duplicated_data['repeated_group'] = 1
previous_value = duplicated_data['fyeco_terms'].iloc[0]
current_index = 1
for i, row in duplicated_data.iterrows():
    if previous_value != row['fyeco_terms']:
        current_index += 1
    duplicated_data.loc[i, 'repeated_group'] = current_index
    previous_value = row['fyeco_terms']

duplicated_data[['repeated_group'] + cols].to_csv('results/repeated_rows.tsv', index=False, sep='\t')
