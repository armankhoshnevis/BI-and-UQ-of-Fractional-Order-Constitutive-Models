# Bayesian Calibration and Uncertainty Quantification for Fractional-Order Constitutive Models

Welcome to the repository for the **BI and UQ of Fractional-Order Constitutive Models** framework. This repository provides computational tools to apply Bayesian inference to fractional consitutive models for linear viscoelastic behavior of complex materials.

## Overview
Fractional-order constitutive models are powerful tools for capturing the memory-dependent and anomalous behavior of materials. However, identifying their parameters requires robust probabilistic frameworks. This project utilizes Bayesian calibration to not only estimate these parameters but also quantify the underlying uncertainties in the data and the model itself.

## Documentaion
A thorough documentation is provided [here](https://armankhoshnevis.github.io/BI-and-UQ-of-Fractional-Order-Constitutive-Models/).

## Repository Structure
* **`Configs/`**: Configuration files for setting up MCMC chains, priors, and model hyperparameters.
* **`Data/`**: Synthetic experimental dataset and optimized model parameters used for the calibration process.
* **`Jupyter_Notebooks/`**: Jupyter notebook equivalents of the python codes for interactive use.
* **`Python_Scripts/`**: Main inference script, helper functions, and post-processing scripts.
* **`Results/`**: Output directories for trace plots, posterior distributions, predictive checks, etc.
* **`docs/`**: Documentaions.

## Installation
Clone the repository and install the required dependencies:

```bash
git clone git@github.com:armankhoshnevis/BI-and-UQ-of-Fractional-Order-Constitutive-Models.git
cd BI-and-UQ-of-Fractional-Order-Constitutive-Models
pip install -r requirements.txt
```

## Quick Run
With the following commands, you can run the inference and post-processing scripts
```bash
python MCMC_FMG_Inference.py --HS 20
python MCMC_FMG_Inference_PostProcessing.py --HS 20
```