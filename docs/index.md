# Bayesian Calibration and Uncertainty Quantification for Fractional-Order Constitutive Models

Welcome to the documentation for the **Bayesian Inference and Uncertainty Quantification of Fractional-Order Constitutive Models** framework. This repository provides computational tools to apply machine learning and Bayesian inference techniques to complex mechanical models.

## Overview
Fractional-order constitutive models are powerful tools for capturing the memory-dependent and anomalous behavior of materials, especially thoese with power-law behavior spanned across decades of time scales. In this study and repository, Bayesian calibration with MCMC sampling technique (NUTS algorithm in PyMC package) are utilized to infere the model parameters, construct their posterior distributions, and quantify the uncertainties in the model responses.

## Repository Structure
* **`configs/`**: Configuration files for setting up MCMC chains, priors, and model hyperparameters.
* **`datasets/`**: Synthetic experimental dataset and optimized model parameters used for the calibration process.
* **`notebooks/`**: Jupyter notebook equivalents of the python codes for interactive use.
* **`scripts/`**: Main inference script, helper functions, and post-processing scripts.
* **`results/`**: Output directories for trace plots, posterior distributions, predictive checks, etc.

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

## Citation Requirements
If you use this software, please cite it and its corresponding paper, as:

- Software citation:
  - APA style: Khoshnevis, A. (2026). Bayesian Calibration and Uncertainty Quantification for Fractional-Order Constitutive Models (Version 1.0.0) [Computer software]. https://github.com/armankhoshnevis/BI-and-UQ-of-Fractional-Order-Constitutive-Models

  - BibTeX entry:<br>
    @software{Khoshnevis_Bayesian_Calibration_and_2026, <br>
    author = {Khoshnevis, Arman},<br>
    license = {Apache-2.0},<br>
    month = mar,<br>
    title = {{Bayesian Calibration and Uncertainty Quantification for Fractional-Order Constitutive Models}},<br>
    url = {https://github.com/armankhoshnevis/BI-and-UQ-of-Fractional-Order-Constitutive-Models},<br>
    version = {1.0.0},<br>
    year = {2026}<br>
    }

- Paper citation: Will be provided once published.