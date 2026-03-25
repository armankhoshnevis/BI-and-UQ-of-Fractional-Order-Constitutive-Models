Config json files are embedded to facilitate some general and preliminary code configuration setups. Here, different components of config files are reviewed:

| Name            | Type | Description |
|-----------------|------|-------------|
| `file_path`     | dict | Dictionary containing the file paths for experimental data, optimized model parameters, and saved results. |
| `sheet_names`   | dict | Dictionary containing the corresponding sheet names for the CSV file that stores synthesized experimental data and optimized model parameter values. |
| `rows`          | dict | Dictionary containing the start and end rows for reading from csv files for experimental and optimized model parameter values.
| `cols_opt`      | list | List containing the column numbers for the optimized model parameter values.
| `cols_GnP`      | dict | Dictionary containing column numbers for experimental data corresponding to each GnP value.
| `GnPs`          | list | List containing string equivalence of GnP values.
| `omega_limits`  | dict | Dictionary containing the lists for the min and max omega values to limit the dataset.
| `rcParams_plot` | dict | Dictionary containing the plot settings.
| `hyperparams`   | dict | Dictionary containing the hyper-parameters used for the inference.