import pandas

mappings = pandas.read_csv('results/full_mappings.tsv', sep='\t')
data = pandas.read_excel('data/SupplementaryFile1.xlsx', sheet_name='All conditions')

data = data.melt(id_vars='gene_id', var_name='condition', value_name='phenotype')

data.dropna(inplace=True)
data['phenotype'] = data['phenotype'].astype(int)

data = data[data['phenotype'] != 0]

data = data.merge(mappings[['condition', 'sensitive', 'resistance', 'fyeco_terms']], on='condition', how='left')

data['FYPO ID'] = data.apply(lambda x: x['sensitive'] if x['phenotype'] == -1 else x['resistance'], axis=1)
rows2drop = data[pandas.isna(data['FYPO ID'])]
print('the following conditions will be dropped (see https://github.com/pombase/fypo/issues/4375)', set(rows2drop['condition']))
data = data[~pandas.isna(data['FYPO ID'])]
data['Condition'] = data['fyeco_terms']

# Here we substitute certain systematic IDs by synonyms, and others we dropped, based on the file
# data/systematic_id_dict.tsv
# Previously, I checked that none of the synonyms used already existed in the dataset

systematic_id_dict = pandas.read_csv('data/systematic_id_dict.tsv', sep='\t', names=['systematic_id', 'synonym'], na_filter=False)
rows_affected = data.gene_id.isin(set(systematic_id_dict['systematic_id']))
data.loc[rows_affected, 'gene_id'] = data.loc[rows_affected, 'gene_id'].map(dict(zip(systematic_id_dict['systematic_id'], systematic_id_dict['synonym'])))
data = data[data['gene_id'] != '']

# We make sure that no invalid systematic id is present
valid_systematic_ids = pandas.read_csv('data/gene_IDs_names.tsv', sep='\t', names=['gene_systematic_id', 'gene_name', 'synonyms'], na_filter=False)

valid_ids = data['gene_id'].isin(set(valid_systematic_ids['gene_systematic_id']))
if not all(valid_ids):
    raise ValueError('invalid systematic ids: {}'.format(set(data.loc[~valid_ids, 'gene_id'])))

column_order = [
    'Gene systematic ID',
    'FYPO ID',
    'Allele description',
    'Expression',
    'Parental strain',
    'Background strain name',
    'Background genotype description',
    'Gene name',
    'Allele name',
    'Allele synonym',
    'Allele type',
    'Evidence',
    'Condition',
    'Penetrance',
    'Severity',
    'Extension',
    'Reference',
    'taxon',
    'Date',
    'Ploidy',
    'Allele variant'
]


data['Gene systematic ID'] = data['gene_id']
data['Allele description'] = 'deletion'
data['Allele type'] = 'deletion'
data['Expression'] = 'null'
data['Parental strain'] = 'h90 968 x (Bioneer ED666 or ED668)'
data['Background strain name'] = ''
data['Background genotype description'] = 'h- prototroph'
data['Gene name'] = ''
data['Allele name'] = ''
data['Allele synonym'] = ''
data['Penetrance'] = ''
data['Extension'] = ''
data['Reference'] = 'PMID:37787768'
data['taxon'] = '4896'
data['Date'] = '2023-06-28'
data['Ploidy'] = 'haploid'
data['Severity'] = ''
data['Allele variant'] = ''
data['Evidence'] = 'ECO:0001563'

data = data.loc[:,column_order]

with open('results/pombase_dataset.tsv', 'w') as out:
    out.write('#Submitter_name: Manuel Lera-Ramirez\n#Submitter_ORCID: 0000-0002-8666-9746\n#Submitter_status: PomBase\n')
    data.to_csv(out, sep='\t', index=False, float_format='%.3f')
