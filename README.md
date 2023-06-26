# Data and scripts for interoperable and reusable LCA system models of rare earth magnet production

This repository contains the scripts and own generated data developed for the article:

Miranda Xicotencatl, B., Kleijn, R., van Nielen, S., Donati, F., Sprecher B. & Tukker, A. (2023). Data implementation matters: Effect of software choice and LCI database evolution on a comparative LCA study of permanent magnets. *Journal of Industrial Ecology*.

The data folder contains the characterized results of three alternatives for the production of rare earth magnets (REMs), calculated with several versions of the ecoinvent database (v2.2 and cut-off v3.1 to v3.6), their life cycle inventories, the foreground data to reproduce their product system models and the data plotted in Figures 3, 4 and 5 of the related article.

**Please refer to the article and the first part of the supplementary information (SI1) for further details about the context and purpose of this repository.**

The table below describes the organization of the own generated data for the referred article.

|**Name of the file**|**Location**|**File format**|**Software which can read the data**|
|:----|:----|:----|:----|
|processDataCMLCA.xlsx|data/|XLSX|custom script|
|CMLCA22_REM.txt|data/|TXT|custom script|
|00_correspondenceFilesNameAndSize.jpg|data/correspondenceFiles|JPG|custom script|
|ExpectedOutputfiles.jpg|data/bw-harmonised/|JPG|custom script|
|LCIsAsAggregatedProcesses.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|REM_replicated_2_2.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|REM_unlinked_2_2.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|REM2_2.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|REM3_1.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|REM3_2.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|REM3_3.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|REM3_4.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|REM3_5.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|REM3_6.xlsx|data/bw-harmonised/|XLSX|custom script and brightway2|
|brightway2-project-REM_aggregatedLCIs-backup.02-February-2022-07-01AM.tar.gz|data/results/|GZ|custom script and brightway2|
|software_bw_LCIA-results.csv|data/results/|CSV|text editor|
|software_editedCMLCA_LCIA-results.csv|data/results/|CSV|text editor|
|versions_CML_LCIA-results.csv|data/results/|CSV|text editor|
|Inventory_software_bw.csv|data/results/LCIs|CSV|text editor|
|Inventory_versions_CML.csv|data/results/LCIs|CSV|text editor|
|dataPlottedInFig_3_4_and_5.xlsx|results/plotted|XLSX| Excel or LibreOffice|

## Notes on the software which can read the data

* Custom script or Activity Browser: To use the file as intended, please start by opening  the file "SI1_BWimport". This document guides the user through the interaction with the custom scripts and it is available as a PDF and as an interactive Jupyter notebook (IPYNB).
* The XLSX, CSV and TXT files intended for the custom scripts can also be browsed in productivity software such as the open-source suite LibreOffice.
* The JPG files in the data folder are used by the interactive Jupyter notebook. Standard processing software is capable to render the JPG files.

## Note on foreground data

[Sprecher et al. (2014)](https://dx.doi.org/10.1021/es404596q) made their foreground data partially available in a human-readable format under a CC BY-NC 4.0 license. The file `processDataCMLCA.xlsx` is based on their complete product system model and consists of an annotated human- and machine-readable version. This modified version also includes the allocation factors used by Sprecher et al. (2014) that were not reported in their original publication.

# License

The data listed in the table above is based on the work by [Sprecher et al. (2014)](https://dx.doi.org/10.1021/es404596q) and licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/) by Brenda Miranda Xicotencatl.

The underlying source code is available in this repository under the [MIT license](LICENSE).
