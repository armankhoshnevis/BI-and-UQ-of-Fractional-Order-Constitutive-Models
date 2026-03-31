import os
import json
import argparse
import matplotlib.pyplot as plt

from Inference_Funcs_FMG import (
    load_data,
    modulus_func,
    define_bounds,
    inference_function,
    calculate_diagnostic_metrics,
    error_func,
    save_inference_results
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--HS', type=int, default=20)
    args = parser.parse_args()
    HS = args.HS

    with open(f'../configs/{HS}HSWF_FMG_Config.json', 'r') as config_file:
        config = json.load(config_file)

    file_path = config['file_path']
    sheet_name = config['sheet_name']
    rows = config['rows']
    cols_opt = config['cols_opt']
    cols_GnP = config['cols_GnP']
    GnPs = config['GnPs']

    # Update matplotlib rcParams
    rcParams_plot = config['rcParams_plot']
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

    # Initialize some variables
    idata_dict,  error_measures_dict = {}, {}
    idata_mean_dict, idata_std_dict, map_estimate_dict = {}, {}, {}
    idata_hdi_dict, Ep_Epp_hdi_dict, model_param_hdi_dict = {}, {}, {}
    ess_quantile_05_dict, ess_quantile_95_dict = {}, {}
    rhat_dict, ess_bulk_dict, mcse_dict = {}, {}, {}
    
    param_list = ['E_c1', 'alpha_1', 'E_c2', 'alpha_2', 'sigma_Ep', 'sigma_Epp']
    actual_param_name = [r'$E_{c_1}$', r'$\alpha_1$', r'$E_{c_2}$', r'$\alpha_2$',
                        r'$\sigma_{E^{\prime}}$', r'$\sigma_{E^{\prime\prime}}$']

    omega_limits = config['omega_limits']
    
    # Load the experimental data and optimized parameters
    v_obs_Ep, v_obs_Epp, x_data, optimized_params_df = load_data(file_path, sheet_name, rows, cols_opt, cols_GnP, omega_limits, rcParams_plot)

    # Perform inference for each nanocomposite system
    for GnP_idx in range(len(GnPs)):
        print(f"Running inference for {GnPs[GnP_idx]}...")

        model_params_opt = optimized_params_df.iloc[GnP_idx]

        bounds = define_bounds(model_params_opt)
        bounds['sigma_Ep'] = (0, 1)
        bounds['sigma_Epp'] = (0, 1)

        exp_data = {
            'x_data': x_data[GnPs[GnP_idx]],
            'v_obs_Ep': v_obs_Ep[GnPs[GnP_idx]],
            'v_obs_Epp': v_obs_Epp[GnPs[GnP_idx]]
        }

        hyperparams = config['hyperparams']

        idata, map_estimate = inference_function(model_params_opt, bounds, exp_data, hyperparams)
        diagnostic_metrics = calculate_diagnostic_metrics(idata, param_list)
        
        idata_dict[GnPs[GnP_idx]] = idata
        map_estimate_dict[GnPs[GnP_idx]] = map_estimate
        rhat_dict[GnPs[GnP_idx]] = diagnostic_metrics['rhat_dict']
        ess_bulk_dict[GnPs[GnP_idx]] = diagnostic_metrics['ess_bulk_dict']
        ess_quantile_05_dict[GnPs[GnP_idx]] = diagnostic_metrics['ess_quantile_05_dict']
        ess_quantile_95_dict[GnPs[GnP_idx]] = diagnostic_metrics['ess_quantile_95_dict']
        mcse_dict[GnPs[GnP_idx]] = diagnostic_metrics['mcse_dict']

        idata_mean_dict[GnPs[GnP_idx]] = {}
        idata_std_dict[GnPs[GnP_idx]] = {}
        for key in param_list:
            idata_mean_dict[GnPs[GnP_idx]][key] = idata_dict[GnPs[GnP_idx]].posterior[key].values.flatten().mean()
            idata_std_dict[GnPs[GnP_idx]][key] = idata_dict[GnPs[GnP_idx]].posterior[key].values.flatten().std()

        map_estimate_dict[GnPs[GnP_idx]]['tau_c1'] = model_params_opt['tau_c1']
        map_estimate_dict[GnPs[GnP_idx]]['tau_c2'] = model_params_opt['tau_c2']
        idata_mean_dict[GnPs[GnP_idx]]['tau_c1'] = model_params_opt['tau_c1']
        idata_mean_dict[GnPs[GnP_idx]]['tau_c2'] = model_params_opt['tau_c2']

        error_measures_dict[GnPs[GnP_idx]] = error_func(
            exp_data['v_obs_Ep'], exp_data['v_obs_Epp'],
            modulus_func(exp_data['x_data'], model_params_opt, 'storage'),
            modulus_func(exp_data['x_data'], model_params_opt, 'loss'),
            modulus_func(exp_data['x_data'], idata_mean_dict[GnPs[GnP_idx]], 'storage'),
            modulus_func(exp_data['x_data'], idata_mean_dict[GnPs[GnP_idx]], 'loss'),
            modulus_func(exp_data['x_data'], map_estimate_dict[GnPs[GnP_idx]], 'storage'),
            modulus_func(exp_data['x_data'], map_estimate_dict[GnPs[GnP_idx]], 'loss'),
        )

    to_be_saved = {
        "idata": idata_dict,
        "idata_mean": idata_mean_dict,
        "idata_std": idata_std_dict,
        "map_estimate": map_estimate_dict,
        "error_measures": error_measures_dict,
        "rhat": rhat_dict,
        "ess_bulk_dict": ess_bulk_dict,
        "ess_quantile_05_dict": ess_quantile_05_dict,
        "ess_quantile_95_dict": ess_quantile_95_dict,
        "mcse_dict": mcse_dict
    }

    save_inference_results(to_be_saved, file_path, HS)
