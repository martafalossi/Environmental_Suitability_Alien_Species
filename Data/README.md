# Data

The analysis relies on environmental suitability datasets, a compilation of marine alien species observations, and external environmental and geographical datasets.

### 1. Future suitability projections (ds)

The variable ds refers to the future environmental suitability dataset used to generate the figures. It is an xarray.Dataset containing the projected suitability values under one of the following climate scenarios:

SSP2-4.5 (ssp245)

SSP5-8.5 (ssp585)

The corresponding dataset should be loaded before running the plotting functions. The exact scenario used depends on the figure being reproduced.

### 2. Past suitability dataset (ds_past)

ds_past is the historical environmental suitability dataset, provided as an xarray.Dataset. It is used to represent past suitability and, where relevant, to compare historical and future conditions.

### 3. Marine alien species observations (Alien_data / observation_Df)

Alien_data (also referred to as observation_Df in the code) is the compiled dataset of marine alien species observations used in the study.

The dataset was obtained by standardizing and combining available sources, as described in the associated scientific paper. It contains the observation records used in the analysis and plotting procedures.

Please refer to the paper for further details on the original sources, data standardization, and filtering procedures.

### 4. External datasets

The analysis also uses the following external data sources:

Copernicus Marine Service: environmental datasets used in the study. Data can be accessed through the Copernicus Marine Data Store. The specific products and variables used are  Escudier, R., Clementi, E., Omar, M., Cipollone, A., Pistoia, J., Aydogdu, A., Drudi, M., Grandi, A., Lyubartsev, V., Lecci, R., Cretí, S., Masina, S., Coppini, G., & Pinardi, N. (2020). Mediterranean Sea Physical Reanalysis (CMEMS MED-Currents) (Version 1) [Data set]. Copernicus Monitoring Environment Marine Service (CMEMS). https://doi.org/10.25423/CMCC/MEDSEA_MULTIYEAR_PHY_006_004_E3R1 and further described in the paper.

Zenodo: future projections downscaled at mediterranean scale used in the analysis. See the relevant Zenodo documentation : Zenodo : Kristiansen, T., & Butenschön, M. (2024). An ensemble of trend preserving statistically downscaled projections for key marine variables under three different future scenarios for the Mediterranean Sea (Version 2.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.10794636.

Natural Earth: geographical boundaries used for map plotting, specifically the 1:10m Admin 0 – Countries shapefile, available here https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/.
