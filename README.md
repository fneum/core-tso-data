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

## Helpers for Manual Corrections

### Openinframap.org

```py
import webbrowser
import pandas as pd
fn = "outputs/locator-results.csv"
df = pd.read_csv(fn, index_col=0)
i = 0
```

```py
i += 1
name, x, y, _ = df.iloc[i]
print(name)
webbrowser.open(f'https://openinframap.org/#15/{y}/{x}')
```

### Match substation names with OpenStreetMap

See [./OSM-locator](./OSM-locator).

1. Download PBF files with OSM data (all NUTS 1 files for one country for better performance)
2. Get the information about the EHV substations in OSM
3. Compare the names the the OSM data and Core TSO with fuzzywuzzy (it gives a list of the 5 best matches)
4. Check manually if the choices are correct:
   - If is not the first match, see if it is one of the others (almost always is the second)
   - If there is data missing in OSM: Add it in OSM and return to step 1
   - Some data is missing because it is actually in a different country, that was added manually, but could be handled later

- Over 95% are already well allocated and the rest is easy to correct
- Updating the OSM is the most time consuming step, but is easy to do and worth it for the community
- In OSM sometimes there is more than one substation with the same name: Just take the first one (for now)
- A 100 % match of the names is impossible (more fancy fuzzywuzzy functions were tested), but the manual adjustments is minimal
- The missing data from other countries and Tie Lines and Trafos, could be allocated later

### Convert locator results pd.DataFrame to YAML

```py
import pandas as pd
import yaml
fn = "outputs/locator-results.csv"
df = pd.read_csv(fn, index_col=0)
d = df.set_index('name')[["x", "y"]].T.to_dict()

with open('my-corrections.yaml', 'w') as yaml_file:
    yaml.dump(
        d,
        yaml_file,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )
```

## License

The code is distributed with an MIT license.

The source data has no license. Use at own risk.
