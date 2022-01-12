# Processing of Core TSO Grid Data

As part of the extension of Flow-Based Market Coupling (FBMC) from FR-DE-BE-NL-LU eastwards this year to encompass the "Core" European countries (FR-DE-BE-NL-LU-PL-CZ-SK-SI-HU-RO-HR-AT), the grid operators published in December 2021 a Static Grid Model covering these Core countries:

https://www.jao.eu/static-grid-model

"The aim of the publication of the SGM is to allow market participants to do market analyses in order to enhance efficiency in the market."

https://www.jao.eu/sites/default/files/2021-12/20211130_MM_Publication%20Core%20Static%20Grid%20Model_FV.pdf

https://www.jao.eu/core-fb-mc

Unlike previously-published models, this has a uniform format, thermal ratings for different seasons, non-obscured substation names and all electrical parameters and lengths. (E.g. unlike the previous data tables on TSO websites which were different for each TSO, or the TYNDP and BNetzA grid models which often had cryptic or obscured substation names which hinders georeferencing).

## Installation

```sh
conda env create -f environment.yaml
```

## Running

```sh
snakemake -j 1 process_data
```

To edit the Jupyter notebooks:

```sh
snakemake -j 1 --edit-notebooks process_data
```

## License

The code is distributed with an MIT license.

The source data has no license. Use at own risk.
