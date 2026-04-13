# Bayesian Calibration and Uncertainty Quantification for Fractional-Order Constitutive Models

This repository provides a computational framework for conducting Bayesian inference and uncertainty quantification on fractional-order constitutive models. The framework relies on the PyMC package, a probabilistic programming library design for robust construction of inference problems. Specifically, Bayesian calibration with MCMC sampling technique (NUTS algorithm in PyMC package) are utilized to infere the model parameters, construct their posterior distributions, and quantify the uncertainties in the model responses.

# Big Picture
This repository is a part of a larger project aiming to develop a framework for deterministic and probabilistic calibration of fractional-order constitutive models capturing the linear viscoelastic response of polyurea nanocomposites. Deterministic calibration has been accomplished with PSO ([Optimization Repository](https://github.com/armankhoshnevis/Optimization-of-Fractional-Order-Constitutive-Models)), while derivative-based local sensitivity analysis (LSA) and variance-based global sensitivity analysis (GSA) have been conducted as a bridge toward a probabilistic perspective ([Sensitivity Analysis Repository](https://github.com/armankhoshnevis/Sensitivity-Analysis-of-Fractional-Order-Constitutive-Models)). These analyses facilitate factor prioritization and dimensionality reduction by identifying non-influential parameters that can be treated deterministically. Finally, Bayesian inference and uncertainty quantification (UQ) have been performed to conclude this comprehensive model development and analysis framework. Figure 1 depicts a schematic overview of this framework. This repository focuses specifically on the Bayesian inference and uncertainty quantification components.

![Overview of Deterministic and Probabilistic Calibration of Fractional-Order Constitutive Models](images/Overview.jpg)

## Repository Structure
* **`configs/`**: Configuration files for setting up MCMC chains, priors, and model hyperparameters.
* **`datasets/`**: Synthetic experimental dataset and optimized model parameters used for the calibration process.
* **`notebooks/`**: Jupyter notebook equivalents of the python codes for interactive use.
* **`scripts/`**: Main inference script, helper functions, and post-processing scripts.
* **`results/`**: Output directories for trace plots, posterior distributions, predictive checks, etc.

## Installation
First, clone the repository and navigate into the project directory:
```bash
git clone git@github.com:armankhoshnevis/BI-and-UQ-of-Fractional-Order-Constitutive-Models.git
cd BI-and-UQ-of-Fractional-Order-Constitutive-Models
```

### Option A: Python venv & pip (Recommended for Running Locally)
If it is preferred to use standard Python virtual environments locally, `pip` alongside the `requirements.txt` file can be used. Then, execute the following commands:
```bash
python -m venv env

# On Windows:
.\env\Scripts\activate

# On macOS/Linux:
source env/bin/activate

pip install -r requirements.txt
```

### Option B: Conda (Recommended for Running on Clusters)
If it is preferred to run the codes on a cluster, `environment.yml` file is used to ensure exact dependency and Python version matching. Then, execute the following commands:
```bash
module load Miniforge3 # Replace with your specific cluster's module if different
conda env create -f environment.yml
conda activate UQ_Project
```

## Quick Run
### Running Locally
Once your environment is activated (via Conda or venv), navigate to the `script` directory and execute the Python files directly from your terminal:
```bash
cd scripts
python MCMC_FMG_Inference.py --HS 20
python MCMC_FMG_Inference_PostProcessing.py --HS 20
```

### Running on a SLURM Cluster
If you are running the inference on a cluster that uses the SLURM workload manager, a sample batch script (`MCMC_FMG.sh` and `MCMC_FMM.sh`) is provided. The script is pre-configured to activate the UQ_Project conda environment.
```bash
cd scripts
sbatch MCMC_FMG.sb
```

**Note:** The script's output and any errors will be automatically logged to standard `.out` and `.err` files in the working directory.

## Documentation
Please refer to this [link](https://armankhoshnevis.github.io/BI-and-UQ-of-Fractional-Order-Constitutive-Models/) for more comprehensive documentations.

## Citation Requirements
If you use this software, please cite it and its corresponding paper, as:

* **Software citation:**
  * **APA style:** Khoshnevis, A. (2026). Bayesian Calibration and Uncertainty Quantification for Fractional-Order Constitutive Models (Version 1.0.0) [Computer software]. https://github.com/armankhoshnevis/BI-and-UQ-of-Fractional-Order-Constitutive-Models

  * **BibTeX entry:** <br>
    @software{Khoshnevis_Bayesian_Calibration_2026, <br>
    author = {Khoshnevis, Arman},<br>
    license = {Apache-2.0},<br>
    month = mar,<br>
    title = {{Bayesian Calibration and Uncertainty Quantification for Fractional-Order Constitutive Models}},<br>
    url = {https://github.com/armankhoshnevis/BI-and-UQ-of-Fractional-Order-Constitutive-Models},<br>
    version = {1.0.0},<br>
    year = {2026}<br>
    }

  * **Paper citation:** Will be provided once published.

## Contributions
This repository is a static archive of the project code. The software is provided "as-is" and is not actively maintained. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more details.
