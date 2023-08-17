# Phenotype mappings for Rodriguez-Lopez et al. 2023

This repository contains the code to generate genotype-to-phenotype datasets in PomBase [phaf format](https://www.pombase.org/downloads/phenotype-annotations) for Rodriguez-Lopez et al. 2023.

The current version lacks the reference column in the phaf file, since a PMID is not available yet.

This code can be easily adapted to generate phaf files from other datasets.

## Installation

Python depencies are managed using poetry, visit https://python-poetry.org/ for details.

```bash
# install dependencies
poetry install

# activate python environment
poetry shell
```

## How to reproduce

See the file `data/SupplementaryFile1.xlsx`. It is the same as the one included in the supplementary of the paper, but it has some extra columns that are used to map the conditions in the study to FYPO (phenotype) and FYECO (condition) terms from PomBase:

- `FYPO_term`: contains two fypo terms for resistance and sensibility to that condition. There can be other surrounding text and symbols, only `FYPO:\d+` text is used by the pipeline.
- `Medium`: FYECO terms for EMM or YES. Empty rows correspond to conditions where the medium term would be overwritten (e.g. EMM with glutamate as nitrogen source (FYECO:0000263)).
- `Other condition`: other FYECO terms associated with the condition, comma separated. If there are more than one term, the doses are indicated in parenthesis, otherwise, the doses would be added automatically by the script `make_mappings.py` (see the script).
- `Dose_units`: see the excell macro that build the column.
- `temperature`: the temperature of the experiment, will be used to set the right FYECO term in `make_mappings.py`.

To make a dictionary of FYECO term id to FYECO term name that is used in the scripts, run:

```bash
python fyeco2json.py
```

To generate the mappings file that is used to generate the phaf file, run:

```bash
python make_mappings.py
```

This creates the file `results/full_mappings.tsv` (see the file, columns are self-explaining). To double check that the mappings are correct, you can run `python check_mappings.py`. This writes the file `results/check_mappings.html`, so you can go through mappings and spot potential errors.

Finally, to generate the PomBase phaf files, run:

```bash
python make_pombase_dataset.py
```

This code uses the `All conditions` sheet to find which strains are sensitive / resistant to all conditions, then uses the mappings in `results/full_mappings.tsv` to build the phaf file.

The final result is written to `results/pombase_dataset.tsv`.
