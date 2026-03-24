import os
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import sys
import time
from datetime import timedelta
from mpl_toolkits.axes_grid1.inset_locator import mark_inset, zoomed_inset_axes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("pymc_sampling")

# Custom callback to log progress
class SimpleLoggingCallback:
    """A simple callback to log the progress of PyMC sampling with timing metrics."""
    def __init__(self, total_draws, log_interval=50_000):
        self.total_draws = total_draws
        self.log_interval = log_interval
        self.current_draws = {}  # Draw counter per chain 
        self.start_times = {}  # start time per chain 
        self.first_draw = True  # Flag for first draw

    def __call__(self, draw, *args, **kwargs):
        chain = draw.chain

        # Initialize per-chain counters and start time
        if chain not in self.current_draws:
            self.current_draws[chain] = 0
            self.start_times[chain] = time.time()
            if self.first_draw:
                logger.info(f"Starting sampling for chain {chain}")
                self.first_draw = False

        # Increment draw counter
        self.current_draws[chain] += 1

        # Log at specified intervals or when done
        if (self.current_draws[chain] % self.log_interval == 0 or 
                self.current_draws[chain] == self.total_draws):
            # Calculate timing metrics
            elapsed_time = time.time() - self.start_times[chain]  # Seconds
            sampling_speed = (self.current_draws[chain] / elapsed_time) if elapsed_time > 0 else 0  # Draws/s
            remaining_draws = self.total_draws - self.current_draws[chain]
            remaining_time = (remaining_draws / sampling_speed) if sampling_speed > 0 else 0  # Seconds

            # Format times as HH:MM:SS
            elapsed_str = str(timedelta(seconds=int(elapsed_time)))
            remaining_str = str(timedelta(seconds=int(remaining_time)))

            # Log message with metrics
            logger.info(
                f"Chain {chain}: {self.current_draws[chain]}/{self.total_draws} samples drawn, "
                f"Speed: {sampling_speed:.2f} draws/s, "
                f"Elapsed: {elapsed_str}, Remaining: {remaining_str}"
            )

            # Log completion for this chain
            if self.current_draws[chain] == self.total_draws:
                logger.info(f"Completed sampling for chain {chain}")

# Load data and plot
def load_data(file_path, sheet_name, rows, cols_opt, cols_GnP, omega_limits, rcParams_plot):
    """Load experimental data and optimized model parameters, and plot the results.
    
    Args:
        file_path (dict): Dictionary containing file paths for experimental and optimized data.
        sheet_name (dict): Dictionary containing sheet names for experimental and optimized data.
        rows (dict): Dictionary containing start and end rows for loading data.
        cols_opt (list): List of column indices for optimized parameters.
        cols_GnP (dict): Dictionary mapping GnP keys to their respective column indices.
        omega_limits (dict): Dictionary containing omega limits for filtering data.
        rcParams_plot (dict): Dictionary containing plot parameters.
    
    Returns:
        v_obs_Ep (dict): Dictionary of observed storage modulus values.
        v_obs_Epp (dict): Dictionary of observed loss modulus values.
        x_data (dict): Dictionary of frequency data.
        optimized_params_df (pd.DataFrame): DataFrame of optimized model parameters.
    """
    # Load experimental data
    data_dict = {
        key: pd.read_excel(
            file_path['file_path_exp'], sheet_name=sheet_name['sheet_name_exp'], usecols=cols_GnP[key],
            skiprows=rows['start_row_exp'], nrows=rows['end_row_exp'] - rows['start_row_exp'], header=None
        ).rename(columns={cols_GnP[key][0]: "omega", cols_GnP[key][1]: "Ep", cols_GnP[key][2]: "Epp"})
        for key in cols_GnP.keys()
    }
    
    v_obs_Ep, v_obs_Epp, x_data = {}, {}, {}
    for i, key in enumerate(data_dict.keys()):
        df = data_dict[key]
        df = df[(df['omega'] >= omega_limits['omega_min'][i]) & (df['omega'] <= omega_limits['omega_max'][i])].reset_index(drop=True)
        v_obs_Ep[key] = df['Ep'].values
        v_obs_Epp[key] = df['Epp'].values
        x_data[key] = df['omega'].values

    # Optimized model parameters
    optimized_params_df = pd.read_excel(
        file_path['file_path_opt'], sheet_name=sheet_name['sheet_name_opt'], usecols=cols_opt,
        skiprows=rows['start_row_opt'], nrows=rows['end_row_opt'] - rows['start_row_opt'], header=None
    )
    optimized_params_df.columns = ['E_c1', 'tau_c1', 'alpha_1', 'E_c2', 'tau_c2', 'alpha_2']

    plt.rcParams.update({
        'font.size': rcParams_plot['font.size'],
        'axes.labelsize': rcParams_plot['axes.labelsize'],
        'xtick.labelsize': rcParams_plot['xtick.labelsize'],
        'ytick.labelsize': rcParams_plot['ytick.labelsize'],
        'legend.fontsize': rcParams_plot['legend.fontsize'],
        'axes.titlesize': rcParams_plot['axes.titlesize'],
        'font.family': rcParams_plot['font.family'],
        'mathtext.fontset': rcParams_plot['mathtext.fontset'],
        'mathtext.rm': rcParams_plot['mathtext.rm'],
        'mathtext.it': rcParams_plot['mathtext.it'],
        'mathtext.bf': rcParams_plot['mathtext.bf']
    })

    _, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes = axes.flatten()
    for i, key in enumerate(cols_GnP.keys()):
        axes[0].loglog(
            x_data[key], v_obs_Ep[key], color=f'C{i}', marker=rcParams_plot['markers'][i], linestyle='None', markersize=6, label=f'{key}')
        axes[1].loglog(
            x_data[key], v_obs_Epp[key], color=f'C{i}', marker=rcParams_plot['markers'][i], linestyle='None', markersize=6, label=f'{key}')

    axes[0].set_xlabel(r'$\omega a_T \ (rad/s)$')
    axes[0].set_xlim([0.5*1e-8, 1.5*1e2])
    axes[0].set_xticks([1e-8, 1e-6, 1e-4, 1e-2, 1e0, 1e2])
    axes[0].set_ylabel(r'$E^{\prime} \ (MPa)$')
    axes[0].legend(["0.0% xGnP", "0.5% xGnP", "1.0% xGnP", "1.5% xGnP"])
    axes[1].set_xlabel(r'$\omega a_T \ (rad/s)$')
    axes[1].set_xlim([0.5*1e-8, 1.5*1e2])
    axes[1].set_xticks([1e-8, 1e-6, 1e-4, 1e-2, 1e0, 1e2])
    axes[1].set_ylabel(r'$E^{\prime\prime} \ (MPa)$')

    plt.tight_layout()

    os.makedirs(file_path['file_path_save'], exist_ok=True)
    plt.savefig(f"{file_path['file_path_save']}/Data_{sheet_name['sheet_name_exp']}.png", dpi=300, bbox_inches='tight')
    
    return v_obs_Ep, v_obs_Epp, x_data, optimized_params_df

# Model functions
def modulus_func(x, model_params, model):
    """Calculate the modulus function for a given model.

    Args:
        x (float): Shifted frequency.
        model_params (dict): The model parameters including the characteristic moduli, time scales, and fractional-order derivatives.
        model (str): The model type ('storage' or 'loss').

    Returns:
        Ep (float): The storage modulus if model is 'storage'.
        Epp (float): The loss modulus if model is 'loss'.
    """
    E_c1, alpha_1 = model_params['E_c1'], model_params['alpha_1']
    E_c2, alpha_2 = model_params['E_c2'], model_params['alpha_2']
    tau_c1, tau_c2 = model_params['tau_c1'], model_params['tau_c2']
    
    num1_Ep = (x * tau_c1)**alpha_1 * np.cos(np.pi * alpha_1 / 2) + (x * tau_c1)**(2 * alpha_1)
    num2_Ep = (x * tau_c2)**alpha_2 * np.cos(np.pi * alpha_2 / 2) + (x * tau_c2)**(2 * alpha_2)
    num1_Epp = (x * tau_c1)**alpha_1 * np.sin(np.pi * alpha_1 / 2)
    num2_Epp = (x * tau_c2)**alpha_2 * np.sin(np.pi * alpha_2 / 2)
    denom1 = 1 + (x * tau_c1)**alpha_1 * np.cos(np.pi * alpha_1 / 2) + (x * tau_c1)**(2 * alpha_1)
    denom2 = 1 + (x * tau_c2)**alpha_2 * np.cos(np.pi * alpha_2 / 2) + (x * tau_c2)**(2 * alpha_2)
    
    Ep = E_c1 * num1_Ep / denom1 + E_c2 * num2_Ep / denom2
    Epp = E_c1 * num1_Epp / denom1 + E_c2 * num2_Epp / denom2
    
    if model == 'storage':
        return Ep
    
    elif model == 'loss':
        return Epp
    else:
        raise ValueError("Invalid model type. Choose 'storage' or 'loss'.")

# Define the bounds for the uniform priors
def define_bounds(model_params_opt, std_fctr=0.2):
    """Define the bounds for the uniform priors based on the optimized model parameters.

    Args:
        model_params_opt (pd.Series): The optimized model parameters.
        std_fctr (float, optional): The standard deviation factor for the bounds. Defaults to 0.2.

    Returns:
        bounds (dict): A dictionary containing the bounds for each model parameter.
    """
    bounds = {}
    bounds['E_c1'] = [
        model_params_opt['E_c1'] - np.sqrt(3) * (std_fctr * model_params_opt['E_c1']),
        model_params_opt['E_c1'] + np.sqrt(3) * (std_fctr * model_params_opt['E_c1'])
    ]
    bounds['alpha_1'] = [
        model_params_opt['alpha_1'] - np.sqrt(3) * (std_fctr * model_params_opt['alpha_1']),
        model_params_opt['alpha_1'] + np.sqrt(3) * (std_fctr * model_params_opt['alpha_1']),
    ]
    bounds['alpha_2'] = [
        model_params_opt['alpha_2'] - np.sqrt(3) * (std_fctr * model_params_opt['alpha_2']),
        model_params_opt['alpha_2'] + np.sqrt(3) * (std_fctr * model_params_opt['alpha_2']),
    ]
    return bounds

# Inference function
def inference_function(model_params_opt, bounds, exp_data, hyperparams):
    """Perform Bayesian inference using PyMC to estimate model parameters.

    Args:
        model_params_opt (pd.Series): The optimized model parameter values.
        bounds (dict): The bounds for the uniform prior distribution of model parameters.
        exp_data (dict): The experimental data (both storage and loss moduli).
        hyperparams (dict): The hyperparameters for the inference (draws, tune, etc.).

    Returns:
        idata (arviz.InferenceData): Inference data (trace) from the sampling.
        map_estimate (dict): MAP estimate of the model parameters.
    """
    
    with pm.Model() as _:
        # Priors
        sigma_Ep = pm.Uniform(
            'sigma_Ep',
            lower=bounds['sigma_Ep'][0],
            upper=bounds['sigma_Ep'][1]
        )
        sigma_Epp = pm.Uniform(
            'sigma_Epp',
            lower=bounds['sigma_Epp'][0],
            upper=bounds['sigma_Epp'][1]
        )
        E_c1 = pm.Uniform(
            'E_c1',
            lower=bounds['E_c1'][0],
            upper=bounds['E_c1'][1]
        )
        alpha_1 = pm.Uniform(
            'alpha_1',
            lower=bounds['alpha_1'][0],
            upper=bounds['alpha_1'][1]
        )
        alpha_2 = pm.Uniform(
            'alpha_2',
            lower=bounds['alpha_2'][0],
            upper=bounds['alpha_2'][1]
        )

        # Enforce the DN constraint for E_c2
        E_c2 = pm.Deterministic(
            'E_c2',
            E_c1 * (model_params_opt['tau_c1'] / model_params_opt['tau_c2'])**2
        )
        
        # Model predictions
        model_params = {
            'E_c1': E_c1,
            'E_c2': E_c2,
            'alpha_1': alpha_1,
            'alpha_2': alpha_2,
            'tau_c1': model_params_opt['tau_c1'],
            'tau_c2': model_params_opt['tau_c2']
        }
        Ep_pred = pm.Deterministic("Ep_pred", modulus_func(exp_data['x_data'], model_params, 'storage'))
        Epp_pred = pm.Deterministic("Epp_pred", modulus_func(exp_data['x_data'], model_params, 'loss'))

        # Likelihood (Log-based squares error)
        _ = pm.Normal("likelihood_Ep", mu=pm.math.log(Ep_pred), sigma=sigma_Ep, observed=pm.math.log(exp_data['v_obs_Ep']))
        _ = pm.Normal("likelihood_Epp", mu=pm.math.log(Epp_pred), sigma=sigma_Epp, observed=pm.math.log(exp_data['v_obs_Epp']))
        
        # Inference magic
        idata = pm.sample(
            draws=hyperparams['draws'],
            tune=hyperparams['tune'],
            return_inferencedata=True,
            chains=hyperparams['chains'],
            cores=hyperparams['cores'],
            progressbar=False,
            discard_tuned_samples=True,
            nuts={'target_accept': hyperparams['target_accept']},
            idata_kwargs={'log_likelihood': True},
            callback=SimpleLoggingCallback(total_draws=hyperparams['draws'], log_interval=10_000)
        )
        
        # Maximum A Posteriori (MAP) estimate
        map_estimate = pm.find_MAP(
            start={
                'E_c1': model_params_opt['E_c1'],
                'E_c2': model_params_opt['E_c2'],
                'alpha_1': model_params_opt['alpha_1'],
                'alpha_2': model_params_opt['alpha_2'],
                'sigma_Ep': (bounds['sigma_Ep'][0] + bounds['sigma_Ep'][1]) / 2,
                'sigma_Epp': (bounds['sigma_Epp'][0] + bounds['sigma_Epp'][1]) / 2
            },
            method='L-BFGS-B',
            include_transformed=False,
            progressbar=False
        )
        del map_estimate['Ep_pred'], map_estimate['Epp_pred']
        
        # Posterior predictive checks
        pm.sample_posterior_predictive(
            idata,
            extend_inferencedata=True,
            return_inferencedata=True,
            progressbar=False
        )
    
    return idata, map_estimate

# Calculate diagnostic metrics function
def calculate_diagnostic_metrics(idata, param_list):
    """Calculate diagnostic metrics such as R-hat, ESS (bulk, 5% and 95% quantiles), and MCSE for the sampled parameters.

    Args:
        idata (arviz.InferenceData): The inference data object.
        param_list (list): List of parameter names for which to calculate diagnostics.

    Returns:
        calculated_diagnostic_metrics (dict): Dictionary containing the calculated diagnostic metrics.
    """
    # Calculate rhat
    rhat = az.rhat(idata, var_names=param_list, method="rank")    
    rhat_dict = {
        name: rhat.values.item()
        for name, rhat in rhat.data_vars.items()
    }
    
    # Calculate ESS
    ess_bulk = az.ess(idata, method="bulk").to_dataframe() # .reset_index(inplace=True)
    ess_bulk.reset_index(inplace=True)
    ess_bulk_dict = ess_bulk[param_list].mean(axis=0).to_dict()

    ess_quantile_05 = az.ess(idata, method="quantile", prob=0.05).to_dataframe()
    ess_quantile_05.reset_index(inplace=True)
    ess_quantile_05_dict = ess_quantile_05[param_list].mean(axis=0).to_dict()

    ess_quantile_95 = az.ess(idata, method="quantile", prob=0.95).to_dataframe()
    ess_quantile_95.reset_index(inplace=True)
    ess_quantile_95_dict = ess_quantile_95[param_list].mean(axis=0).to_dict()
    
    # Calculate MCSE
    mcse = az.mcse(idata, var_names=param_list)
    mcse_dict = {
        name: mcse.values.item()
        for name, mcse in mcse.data_vars.items()
    }

    calculated_diagnostic_metrics = {
        'rhat_dict': rhat_dict,
        'ess_bulk_dict': ess_bulk_dict,
        'ess_quantile_05_dict': ess_quantile_05_dict,
        'ess_quantile_95_dict': ess_quantile_95_dict,
        'mcse_dict': mcse_dict
    }
    
    return calculated_diagnostic_metrics

# Error metrics function
def error_func(Ep_exp, Epp_exp, Ep_opt, Epp_opt, Ep_MCMC_mean, Epp_MCMC_mean, Ep_MCMC_map, Epp_MCMC_map):
    """Calculate the error metrics between experimental and model data.

    Args:
        Ep_exp (np.ndarray): Experimental data for Ep.
        Epp_exp (np.ndarray): Experimental data for Epp.
        Ep_opt (np.ndarray): Optimized model data for Ep.
        Epp_opt (np.ndarray): Optimized model data for Epp.
        Ep_MCMC_mean (np.ndarray): MCMC mean model data for Ep.
        Epp_MCMC_mean (np.ndarray): MCMC mean model data for Epp.
        Ep_MCMC_map (np.ndarray): MCMC map model data for Ep.
        Epp_MCMC_map (np.ndarray): MCMC map model data for Epp.

    Returns:
        error_measures (dict): Dictionary containing the calculated error metrics.
    """
    log_mse_Ep_opt = np.mean((np.log(Ep_exp / Ep_opt))**2)
    log_mse_Epp_opt = np.mean((np.log(Epp_exp / Epp_opt))**2)
    log_mse_opt = np.mean((np.log(Ep_exp / Ep_opt))**2 + (np.log(Epp_exp / Epp_opt))**2)

    log_mse_Ep_MCMC_mean = np.mean((np.log(Ep_exp / Ep_MCMC_mean))**2)
    log_mse_Epp_MCMC_mean = np.mean((np.log(Epp_exp / Epp_MCMC_mean))**2)
    log_mse_MCMC_mean = np.mean((np.log(Ep_exp / Ep_MCMC_mean))**2 + (np.log(Epp_exp / Epp_MCMC_mean))**2)

    log_mse_Ep_MCMC_map = np.mean((np.log(Ep_exp / Ep_MCMC_map))**2)
    log_mse_Epp_MCMC_map = np.mean((np.log(Epp_exp / Epp_MCMC_map))**2)
    log_mse_MCMC_map = np.mean((np.log(Ep_exp / Ep_MCMC_map))**2 + (np.log(Epp_exp / Epp_MCMC_map))**2)

    num_opt = np.sum( (np.log(Ep_exp / Ep_opt))**2 ) + np.sum( (np.log(Epp_exp / Epp_opt))**2 )
    denum_opt = np.sum( (np.log(Ep_exp))**2 ) + np.sum( (np.log(Epp_exp))**2 )
    relative_error_opt = np.sqrt(num_opt/denum_opt) * 100

    num_MCMC_mean = np.sum( (np.log(Ep_exp / Ep_MCMC_mean))**2 ) + np.sum( (np.log(Epp_exp / Epp_MCMC_mean))**2 )
    denum_MCMC_mean = np.sum( (np.log(Ep_exp))**2 ) + np.sum( (np.log(Epp_exp))**2 )
    relative_error_MCMC_mean = np.sqrt(num_MCMC_mean/denum_MCMC_mean) * 100

    num_MCMC_map = np.sum( (np.log(Ep_exp / Ep_MCMC_map))**2 ) + np.sum( (np.log(Epp_exp / Epp_MCMC_map))**2 )
    denum_MCMC_map = np.sum( (np.log(Ep_exp))**2 ) + np.sum( (np.log(Epp_exp))**2 )
    relative_error_MCMC_map = np.sqrt(num_MCMC_map/denum_MCMC_map) * 100

    error_measures = {
        'log_mse_Ep_opt': log_mse_Ep_opt,
        'log_mse_Epp_opt': log_mse_Epp_opt,
        'log_mse_Ep_MCMC_mean': log_mse_Ep_MCMC_mean,
        'log_mse_Epp_MCMC_mean': log_mse_Epp_MCMC_mean,
        'log_mse_Ep_MCMC_map': log_mse_Ep_MCMC_map,
        'log_mse_Epp_MCMC_map': log_mse_Epp_MCMC_map,
        'log_mse_opt': log_mse_opt,
        'log_mse_MCMC_mean': log_mse_MCMC_mean,
        'log_mse_MCMC_map': log_mse_MCMC_map,
        'relative_error_opt': relative_error_opt,
        'relative_error_MCMC_mean': relative_error_MCMC_mean,
        'relative_error_MCMC_map': relative_error_MCMC_map
    }
    return error_measures

# Save results function
def save_inference_results(to_be_saved, file_path, HS):
    """Save the inference results, diagnostic metrics, and error measures to specified file paths.

    Args:
        to_be_saved (dict): Dictionary containing the inference results to be saved.
        file_path (dict): Dictionary containing the file paths for saving the results.
        HS (int): The number of hidden states in the model.
    """
    idata = to_be_saved["idata"]
    idata_mean = to_be_saved["idata_mean"]
    idata_std = to_be_saved["idata_std"]
    map_estimate = to_be_saved["map_estimate"]
    error_measures = to_be_saved["error_measures"]
    rhat = to_be_saved["rhat"]
    ess_bulk = to_be_saved["ess_bulk_dict"]
    ess_quantile_05 = to_be_saved["ess_quantile_05_dict"]
    ess_quantile_95 = to_be_saved["ess_quantile_95_dict"]
    mcse = to_be_saved["mcse_dict"]
    
    for key in idata.keys():
        nc_filename = f"{file_path['file_path_save']}/EpEpp_FMG_{HS}HS_{key}.nc"
        az.to_netcdf(idata[key], nc_filename)
        print(f"Saved inference data for {key} to {nc_filename}")
    
    df_mean = pd.DataFrame(idata_mean).T.reset_index().rename(columns={'index': 'GnP'})
    df_mean.to_csv(f"{file_path['file_path_save']}/Mean_Inference_{HS}HS_FMG.csv", index=False)

    df_std = pd.DataFrame(idata_std).T.reset_index().rename(columns={'index': 'GnP'})
    df_std.to_csv(f"{file_path['file_path_save']}/std_Inference_{HS}HS_FMG.csv", index=False)

    df_map = pd.DataFrame(map_estimate).T.reset_index().rename(columns={'index': 'GnP'})
    df_map.to_csv(f"{file_path['file_path_save']}/Map_Estimate_{HS}HS_FMG.csv", index=False)

    df_error_measures = pd.DataFrame(error_measures).T.reset_index().rename(columns={'index': 'GnP'})
    df_error_measures.to_csv(f"{file_path['file_path_save']}/Error_Measures_{HS}HS_FMG.csv", index=False)

    df_rhat = pd.DataFrame(rhat).T.reset_index().rename(columns={'index': 'GnP'})
    df_rhat.to_csv(f"{file_path['file_path_save']}/Rhat_{HS}HS_FMG.csv", index=False)

    df_ess_bulk = pd.DataFrame(ess_bulk).T.reset_index().rename(columns={'index': 'GnP'})
    df_ess_bulk.to_csv(f"{file_path['file_path_save']}/ESS_Bulk_{HS}HS_FMG.csv", index=False)

    df_ess_quantile_05 = pd.DataFrame(ess_quantile_05).T.reset_index().rename(columns={'index': 'GnP'})
    df_ess_quantile_05.to_csv(f"{file_path['file_path_save']}/ESS_Quantile_05_{HS}HS_FMG.csv", index=False)

    df_ess_quantile_95 = pd.DataFrame(ess_quantile_95).T.reset_index().rename(columns={'index': 'GnP'})
    df_ess_quantile_95.to_csv(f"{file_path['file_path_save']}/ESS_Quantile_95_{HS}HS_FMG.csv", index=False)

    df_mcse = pd.DataFrame(mcse).T.reset_index().rename(columns={'index': 'GnP'})
    df_mcse.to_csv(f"{file_path['file_path_save']}/MCSE_{HS}HS_FMG.csv", index=False)

    print("Done! ...")

# --------------------------------------------------
# Plot functions
# --------------------------------------------------
# Plot posterior distributions
def plot_posterior_distributions(idata, idata_mean, param_list, actual_param_name, plt_set, rcParams_plot):
    """Plot the posterior distributions of model parameters and compare with experimental data.

    Args:
        idata (arviz.InferenceData): Inference data from the sampling.
        idata_mean (dict): Dictionary containing the mean values of the posterior distributions.
        param_list (list): List of parameter names to plot.
        actual_param_name (list): List of actual parameter names for labeling.
        plt_set (dict): Dictionary containing plot settings.
        rcParams_plot (dict): Dictionary containing plot style parameters.
    """
    plt.rcParams.update({
        'font.size': rcParams_plot['font.size'],
        'axes.labelsize': rcParams_plot['axes.labelsize'],
        'xtick.labelsize': rcParams_plot['xtick.labelsize'],
        'ytick.labelsize': rcParams_plot['ytick.labelsize'],
        'axes.titlesize': rcParams_plot['axes.titlesize'],
        'legend.fontsize': rcParams_plot['legend.fontsize'],
        'font.family': rcParams_plot['font.family'],
        'mathtext.fontset': rcParams_plot['mathtext.fontset'],
        'mathtext.rm': rcParams_plot['mathtext.rm'],
        'mathtext.it': rcParams_plot['mathtext.it'],
        'mathtext.bf': rcParams_plot['mathtext.bf'],
    })
    
    hdi_prob = 0.95
    model_param_hdi = {
        'E_c1': az.hdi(idata.posterior['E_c1'].values.flatten(), hdi_prob=hdi_prob),
        'E_c2': az.hdi(idata.posterior['E_c2'].values.flatten(), hdi_prob=hdi_prob),
        'alpha_1': az.hdi(idata.posterior['alpha_1'].values.flatten(), hdi_prob=hdi_prob),
        'alpha_2': az.hdi(idata.posterior['alpha_2'].values.flatten(), hdi_prob=hdi_prob)
    }
    
    _, axes = plt.subplots(1, 4, figsize=(16, 4))
    axes = axes.flatten()

    for i, param in enumerate(param_list[:-2]):
        az.plot_kde(
            idata.posterior[param].values.flatten(),
            plot_kwargs={'color': 'C0', 'linewidth': 3}, ax=axes[i]
        )
        axes[i].set_xlabel(actual_param_name[i])
        axes[i].set_ylabel(r'$\boldsymbol{\pi}(' + actual_param_name[i][1:-1] + r'|\boldsymbol{D})$')
        
        axes[i].plot(idata_mean[param], 0, marker='o', linestyle='None', markersize=10, color='C7', label='Mean')  # GnP_idx ...
        axes[i].plot(model_param_hdi[param], [0, 0], marker='^', linestyle='None', markersize=10, color='C9', label='95% HDI')
        
        axes[i].tick_params()
    # Modifications
    axes[0].set_xlabel(r"$E_{c_1} \ (MPa)$")
    axes[2].set_xlabel(r"$E_{c_2} \ (MPa)$")
    axes[0].legend(loc='center right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.99])
    plt.savefig(plt_set['savefig_path'], dpi=300, bbox_inches='tight')

# Rank plots and trace plots
def plot_diagnostic(idata, var_names, xticks, xticklabels, plt_set, rcParams_plot):
    """Plot the diagnostic plots (rank and trace plots) for the inferred model parameters.

    Args:
        idata (arviz.InferenceData): Inference data from the sampling.
        var_names (list): List of variable names to plot.
        xticks (list): List of x-axis tick positions.
        xticklabels (list): List of x-axis tick labels.
        plt_set (dict): Dictionary containing plot settings.
        rcParams_plot (dict): Dictionary containing plot style parameters.
    """
    plt.rcParams.update({
        'font.size': rcParams_plot['font.size'],
        'axes.labelsize': rcParams_plot['axes.labelsize'],
        'xtick.labelsize': rcParams_plot['xtick.labelsize'],
        'ytick.labelsize': rcParams_plot['ytick.labelsize'],
        'legend.fontsize': rcParams_plot['legend.fontsize'],
        'axes.titlesize': rcParams_plot['axes.titlesize'],
        'font.family': rcParams_plot['font.family'],
        'mathtext.fontset': rcParams_plot['mathtext.fontset'],
        'mathtext.rm': rcParams_plot['mathtext.rm'],
        'mathtext.it': rcParams_plot['mathtext.it'],
        'mathtext.bf': rcParams_plot['mathtext.bf']
    })

    axes = az.plot_rank(idata, var_names=var_names, grid=(1, 4), figsize=(16, 4))
    axes = axes.flatten()
    axes[0].set_title(r"$E_{c_1}$")
    axes[0].set_xlabel("Rank (All Chains)")
    axes[0].set_xticks(xticks)
    axes[0].set_xticklabels(xticklabels)
    axes[0].set_yticklabels([1, 2, 3, 4])

    axes[1].set_title(r"$\alpha_1$")
    axes[1].set_xlabel("Rank (All Chains)")
    axes[1].set_xticks(xticks)
    axes[1].set_xticklabels(xticklabels)
    axes[1].set_yticklabels([1, 2, 3, 4])

    axes[2].set_title(r"$E_{c_2}$")
    axes[2].set_xlabel("Rank (All Chains)")
    axes[2].set_xticks(xticks)
    axes[2].set_xticklabels(xticklabels)
    axes[2].set_yticklabels([1, 2, 3, 4])

    axes[3].set_title(r"$\alpha_2$")
    axes[3].set_xlabel("Rank (All Chains)")
    axes[3].set_xticks(xticks)
    axes[3].set_xticklabels(xticklabels)
    axes[3].set_yticklabels([1, 2, 3, 4])

    plt.tight_layout()
    plt.savefig(plt_set['savefig_path_rank'], dpi=300, bbox_inches='tight')
    plt.show()
    
    _, axes = plt.subplots(1, 4, figsize=(16, 3.5))
    axes = axes.flatten()
    for i, param in enumerate(var_names):
        axes[i].plot(idata.posterior[param].values[0, :], color='C0', alpha=0.15, linestyle='-')
        axes[i].plot(idata.posterior[param].values[1, :], color='C0', alpha=0.40, linestyle='--')
        axes[i].plot(idata.posterior[param].values[2, :], color='C0', alpha=0.65, linestyle='-.')
        axes[i].plot(idata.posterior[param].values[3, :], color='C0', alpha=0.90, linestyle=':')
        axes[i].set_xlabel('Sample Draws')
    axes[0].set_ylabel(r'$E_{c_1} \ (MPa)$')
    axes[1].set_ylabel(r'$\alpha_1$')
    axes[2].set_ylabel(r'$E_{c_2} \ (MPa)$')
    axes[3].set_ylabel(r'$\alpha_2$')

    plt.tight_layout()
    plt.savefig(plt_set['savefig_path_trace'], dpi=300, bbox_inches='tight')
    plt.show()

# Plot posterior predictive with HDI
def plot_posterior_predictive(idata_dict, v_obs_Ep, v_obs_Epp, x_data, GnPs, GnP_idx, xylims, plt_set, rcParams_plot):
    """Plot the storage and loss mooduli predictions with uncertainty intervals (HDI) from the posterior predictive distribution, and compare with the observed data.

    Args:
        idata_dict (arviz.InferenceData): Inference data from the sampling.
        v_obs_Ep (np.ndarray): Observed storage modulus data.
        v_obs_Epp (np.ndarray): Observed loss modulus data.
        x_data (np.ndarray): Frequency data.
        GnPs (list): List of GnP values.
        GnP_idx (int): Index of the current GnP value.
        xylims (dict): Limits for the x and y axes of the insets.
        plt_set (dict): Description of the plot settings.
        rcParams_plot (dict): Description of the plot parameters.
    """
    plt.rcParams.update({
        'font.size': rcParams_plot['font.size'],
        'axes.labelsize': rcParams_plot['axes.labelsize'],
        'xtick.labelsize': rcParams_plot['xtick.labelsize'],
        'ytick.labelsize': rcParams_plot['ytick.labelsize'],
        'legend.fontsize': rcParams_plot['legend.fontsize'],
        'axes.titlesize': rcParams_plot['axes.titlesize'],
        'font.family': rcParams_plot['font.family'],
        'mathtext.fontset': rcParams_plot['mathtext.fontset'],
        'mathtext.rm': rcParams_plot['mathtext.rm'],
        'mathtext.it': rcParams_plot['mathtext.it'],
        'mathtext.bf': rcParams_plot['mathtext.bf']
    })
    fig, axes = plt.subplots(1, 2, figsize=(16, 5), constrained_layout=True)
    axes = axes.flatten()

    Ep_pred = idata_dict[GnPs[GnP_idx]].posterior["Ep_pred"]
    Ep_pred_mean = Ep_pred.mean(dim=["draw", "chain"])
    Epp_pred = idata_dict[GnPs[GnP_idx]].posterior["Epp_pred"]
    Epp_pred_mean = Epp_pred.mean(dim=["draw", "chain"])

    # Plot for Ep_pred
    axes[0].scatter(x_data[GnPs[GnP_idx]], v_obs_Ep[GnPs[GnP_idx]], label='Observed', marker='o', s=64, color='C3')
    axes[0].plot(x_data[GnPs[GnP_idx]], Ep_pred_mean, label='Mean Predicted', linestyle='-', color='C0', linewidth=1.1)
    az.plot_hdi(
        x_data[GnPs[GnP_idx]],
        Ep_pred,
        hdi_prob=0.95,
        smooth=False,
        plot_kwargs={'color': 'C0', 'alpha': 0.3},
        fill_kwargs={'color': 'C0', 'alpha': 0.3, 'label': r'95% HDI'},
        ax=axes[0]
    )
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel(r"$\omega a_T \ (rad/s)$")
    axes[0].set_ylabel(r"$E^{\prime}$ (MPa)")
    axes[0].set_xlim([0.5*1e-8, 1.5*1e2])
    axes[0].set_xticks([1e-8, 1e-6, 1e-4, 1e-2, 1e0, 1e2])
    axes[0].set_ylim([1.1e1, 4e3])
    axes[0].text(
        0.012, 0.92, r'$(a)$',
        transform=axes[0].transAxes,
    )
    axes[0].legend(fontsize=16, loc='lower right')

    # First inset for Ep_pred
    axins1 = zoomed_inset_axes(axes[0], zoom=1.5, loc=xylims['Ep_inset1']['loc'])
    axins1.loglog(x_data[GnPs[GnP_idx]], Ep_pred_mean, color='C0')
    axins1.scatter(x_data[GnPs[GnP_idx]], v_obs_Ep[GnPs[GnP_idx]], color='C3', s=64)
    az.plot_hdi(
        x_data[GnPs[GnP_idx]],
        Ep_pred,
        hdi_prob=0.95,
        smooth=False,
        plot_kwargs={'color': 'C0', 'alpha': 0.3},
        fill_kwargs={'color': 'C0', 'alpha': 0.3},
        ax=axins1
    )
    
    axins1.set_xlim(xylims['Ep_inset1']['xlim'])
    axins1.set_ylim(xylims['Ep_inset1']['ylim'])
    axins1.xaxis.set_visible(False)
    axins1.yaxis.set_visible(False)
    mark_inset(axes[0], axins1, loc1=2, loc2=4, fc="none", ec="0.5")

    # Second inset for Ep_pred
    axins2 = zoomed_inset_axes(axes[0], zoom=1.5, loc=xylims['Ep_inset2']['loc'])
    axins2.loglog(x_data[GnPs[GnP_idx]], Ep_pred_mean, color='C0')
    axins2.scatter(x_data[GnPs[GnP_idx]], v_obs_Ep[GnPs[GnP_idx]], color='C3', s=64)
    az.plot_hdi(
        x_data[GnPs[GnP_idx]],
        Ep_pred,
        hdi_prob=0.95,
        smooth=False,
        plot_kwargs={'color': 'C0', 'alpha': 0.3},
        fill_kwargs={'color': 'C0', 'alpha': 0.3},
        ax=axins2
    )
    axins2.set_xlim(xylims['Ep_inset2']['xlim'])
    axins2.set_ylim(xylims['Ep_inset2']['ylim'])
    axins2.xaxis.set_visible(False)
    axins2.yaxis.set_visible(False)
    mark_inset(axes[0], axins2, loc1=2, loc2=4, fc="none", ec="0.5")

    # Epp
    axes[1].scatter(x_data[GnPs[GnP_idx]], v_obs_Epp[GnPs[GnP_idx]], label='Observed', marker='o', s=64, color='C3')
    axes[1].plot(x_data[GnPs[GnP_idx]], Epp_pred_mean, label='Mean Predicted', linestyle='-', color='C0', linewidth=1.1)
    az.plot_hdi(
        x_data[GnPs[GnP_idx]],
        Epp_pred,
        hdi_prob=0.95,
        smooth=False,
        plot_kwargs={'color': 'C0', 'alpha': 0.3},
        fill_kwargs={'color': 'C0', 'alpha': 0.3},
        ax=axes[1]
    )
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel(r"$\omega a_T \ (rad/s)$")
    axes[1].set_ylabel(r"$E^{\prime\prime}$ (MPa)")
    axes[1].set_xlim([0.5*1e-8, 1.5*1e2])
    axes[1].set_xticks([1e-8, 1e-6, 1e-4, 1e-2, 1e0, 1e2])
    axes[1].set_ylim([1.1e0, 1.1e3])
    axes[1].text(
        0.012, 0.92, r'$(b)$',
        transform=axes[1].transAxes,
    )

    # First inset for Epp_pred
    axins3 = zoomed_inset_axes(axes[1], zoom=1.5, loc=xylims['Epp_inset3']['loc'])
    axins3.loglog(x_data[GnPs[GnP_idx]], Epp_pred_mean, color='C0')
    axins3.scatter(x_data[GnPs[GnP_idx]], v_obs_Epp[GnPs[GnP_idx]], color='C3', s=64)
    az.plot_hdi(
        x_data[GnPs[GnP_idx]],
        Epp_pred,
        hdi_prob=0.95,
        smooth=False,
        plot_kwargs={'color': 'C0', 'alpha': 0.3},
        fill_kwargs={'color': 'C0', 'alpha': 0.3},
        ax=axins3
    )
    axins3.set_xlim(xylims['Epp_inset3']['xlim'])
    axins3.set_ylim(xylims['Epp_inset3']['ylim'])
    axins3.xaxis.set_visible(False)
    axins3.yaxis.set_visible(False)
    mark_inset(axes[1], axins3, loc1=2, loc2=4, fc="none", ec="0.5")

    # Second inset for Epp_pred
    axins4 = zoomed_inset_axes(axes[1], zoom=1.25, loc=xylims['Epp_inset4']['loc'])

    axins4.loglog(x_data[GnPs[GnP_idx]], Epp_pred_mean, color='C0')
    axins4.scatter(x_data[GnPs[GnP_idx]], v_obs_Epp[GnPs[GnP_idx]], color='C3', s=64)
    az.plot_hdi(
        x_data[GnPs[GnP_idx]],
        Epp_pred,
        hdi_prob=0.95,
        smooth=False,
        plot_kwargs={'color': 'C0', 'alpha': 0.3},
        fill_kwargs={'color': 'C0', 'alpha': 0.3},
        ax=axins4
    )
    axins4.set_xlim(xylims['Epp_inset4']['xlim'])
    axins4.set_ylim(xylims['Epp_inset4']['ylim'])
    axins4.xaxis.set_visible(False)
    axins4.yaxis.set_visible(False)
    mark_inset(axes[1], axins4, loc1=2, loc2=4, fc="none", ec="0.5")

    plt.savefig(plt_set['savefig_path'], dpi=300, bbox_inches='tight')
    plt.show()

# Plot posterior predictive checks
def plot_posterior_predictive_checks(idata, range1, range2, plt_set, rcParams_plot):
    """Plot the posterior predictive checks for the model with the inferred model parameters.

    Args:
        idata (arviz.InferenceData): Inference data from the sampling.
        range1 (tuple): The range for the first subplot.
        range2 (tuple): The range for the second subplot.
        rcParams_plot (dict): Dictionary containing plot style parameters.
    """
    plt.rcParams.update({
        'font.size': rcParams_plot['font.size'],
        'axes.labelsize': rcParams_plot['axes.labelsize'],
        'xtick.labelsize': rcParams_plot['xtick.labelsize'],
        'ytick.labelsize': rcParams_plot['ytick.labelsize'],
        'axes.titlesize': rcParams_plot['axes.titlesize'],
        'legend.fontsize': rcParams_plot['legend.fontsize'],
        'font.family': rcParams_plot['font.family'],
        'mathtext.fontset': rcParams_plot['mathtext.fontset'],
        'mathtext.rm': rcParams_plot['mathtext.rm'],
        'mathtext.it': rcParams_plot['mathtext.it'],
        'mathtext.bf': rcParams_plot['mathtext.bf'],
    })
    
    ax = az.plot_ppc(idata, figsize=(16, 5), num_pp_samples=500)

    ax[0].set_xlabel("Likelihood of E\' ")
    ax[1].set_xlabel("Likelihood of E\'\' ")

    ax[0].set_ylabel("Density")
    ax[1].set_ylabel("Density")

    ax[0].set_xlim(range1)
    ax[1].set_xlim(range2)

    ax[0].legend().remove()
    ax[1].legend(loc='upper left')

    plt.savefig(plt_set['savefig_path'], dpi=300, bbox_inches='tight')
    plt.show()

# Pairplots
def plot_pairplot(idata, var_names, subset_data_number, plt_set, rcParams_plot):
    """Plot the pairplot of the sampled parameters to visualize their joint distributions and correlations.

    Args:
        idata (arviz.InferenceData): Inference data from the sampling.
        var_names (list): List of variable names to plot.
        subset_data_number (int): Number of samples to include in the subset.
        rcParams_plot (dict): Dictionary containing plot style parameters.
    """
    data = az.extract(idata, var_names=var_names).to_dataframe()
    data = data[var_names]
    data.reset_index(inplace=True)
    data.drop(columns=['chain', 'draw'], inplace=True)
    subdata = data.iloc[:subset_data_number]
    
    plt.rcParams.update({
        'font.size': rcParams_plot['font.size'],
        'axes.labelsize': rcParams_plot['axes.labelsize'],
        'xtick.labelsize': rcParams_plot['xtick.labelsize'],
        'ytick.labelsize': rcParams_plot['ytick.labelsize'],
        'axes.titlesize': rcParams_plot['axes.titlesize'],
        'legend.fontsize': rcParams_plot['legend.fontsize'],
        'font.family': rcParams_plot['font.family'],
        'mathtext.fontset': rcParams_plot['mathtext.fontset'],
        'mathtext.rm': rcParams_plot['mathtext.rm'],
        'mathtext.it': rcParams_plot['mathtext.it'],
        'mathtext.bf': rcParams_plot['mathtext.bf'],
    })

    g = sns.PairGrid(subdata, diag_sharey=False)
    g.map_upper(sns.scatterplot, s=30, alpha=0.99, edgecolor='black', linewidth=0.5, color=sns.color_palette("Paired")[1])
    g.map_lower(sns.kdeplot, fill=False, thresh=0.05, levels=5, cmap=sns.color_palette("viridis", as_cmap=True))  # plt.cm.viridis
    g.map_diag(sns.kdeplot, lw=2, color=sns.color_palette("Paired")[0])

    for ax in g.axes.flat:
        ax.spines['right'].set_visible(True)
        ax.spines['top'].set_visible(True)
        ax.spines['right'].set_color('black')
        ax.spines['top'].set_color('black')
        ax.spines['right'].set_linewidth(0.75)
        ax.spines['top'].set_linewidth(0.75)

    g.axes[0, 0].set_ylabel(r"$E_{c_1}$")
    g.axes[1, 0].set_ylabel(r"$\alpha_1$")
    g.axes[2, 0].set_ylabel(r"$\alpha_2$")
    g.axes[3, 0].set_ylabel(r"$E_{c_2}$")

    g.axes[3, 0].set_xlabel(r"$E_{c_1}$")
    g.axes[3, 1].set_xlabel(r"$\alpha_1$")
    g.axes[3, 2].set_xlabel(r"$\alpha_2$")
    g.axes[3, 3].set_xlabel(r"$E_{c_2}$")
    plt.savefig(plt_set['savefig_path'], dpi=300, bbox_inches='tight')
    plt.show()
