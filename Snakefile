configfile: "configs/workflow/workflow_cases.yaml"

HS_VALUES = [str(x) for x in config["hs_values"]]

wildcard_constraints:
    HS=r"\d+"

rule fmg_all:
    input:
        expand("results/MCMC_FMG_{HS}HSWF/.{HS}HSWF_fmg_vis_done", HS=HS_VALUES)
    default_target: True

rule fmm_all:
    input:
        expand("results/MCMC_FMM_{HS}HSWF/.{HS}HSWF_fmm_vis_done", HS=HS_VALUES)

rule run_fmg:
    output:
        touch("results/MCMC_FMG_{HS}HSWF/.{HS}HSWF_fmg_run_done")
    log:
        "logs/FMG/{HS}HSWF_run.log"
    shell:
        r"""
        mkdir -p results/MCMC_FMG_{wildcards.HS}HSWF logs/FMG
        cd scripts
        python MCMC_FMG_Inference.py --HS {wildcards.HS} > ../{log} 2>&1
        """

rule vis_fmg:
    input:
        "results/MCMC_FMG_{HS}HSWF/.{HS}HSWF_fmg_run_done"
    output:
        touch("results/MCMC_FMG_{HS}HSWF/.{HS}HSWF_fmg_vis_done")
    log:
        "logs/FMG/{HS}HSWF_vis.log"
    shell:
        r"""
        mkdir -p results/MCMC_FMG_{wildcards.HS}HSWF logs/FMG
        cd scripts
        python MCMC_FMG_Inference_PostProcessing.py --HS {wildcards.HS} > ../{log} 2>&1
        """

rule run_fmm:
    output:
        touch("results/MCMC_FMM_{HS}HSWF/.{HS}HSWF_fmm_run_done")
    log:
        "logs/FMM/{HS}HSWF_run.log"
    shell:
        r"""
        mkdir -p results/MCMC_FMM_{wildcards.HS}HSWF logs/FMM
        cd scripts
        python MCMC_FMM_Inference.py --HS {wildcards.HS} > ../{log} 2>&1
        """

rule vis_fmm:
    input:
        "results/MCMC_FMM_{HS}HSWF/.{HS}HSWF_fmm_run_done"
    output:
        touch("results/MCMC_FMM_{HS}HSWF/.{HS}HSWF_fmm_vis_done")
    log:
        "logs/FMM/{HS}HSWF_vis.log"
    shell:
        r"""
        mkdir -p results/MCMC_FMM_{wildcards.HS}HSWF logs/FMM
        cd scripts
        python MCMC_FMM_Inference_PostProcessing.py --HS {wildcards.HS} > ../{log} 2>&1
        """