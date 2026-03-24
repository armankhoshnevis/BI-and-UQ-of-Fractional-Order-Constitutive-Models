## Bayesian Calibration

We model the experimental data $\boldsymbol{D} = \{E'(x_i), E''(x_i)\}_{i=1}^{N_d}$ using the statistical relation

$$
\boldsymbol{D} = \boldsymbol{\mathcal{M}}(\boldsymbol{x}, \boldsymbol{\theta}_m) + \boldsymbol{\varepsilon},
$$

where $\boldsymbol{\mathcal{M}}$ denotes the deterministic model predictions and $\boldsymbol{\varepsilon}$ represents measurement error. Both model parameters $\boldsymbol{\theta}_m$ and errors are treated as random variables.

### Error Model

Measurement errors are assumed independent and Gaussian:

$$
\varepsilon_{i,E'} \sim \mathcal{N}(0, \sigma_{E'}), \quad
\varepsilon_{i,E''} \sim \mathcal{N}(0, \sigma_{E''}),
$$

with unknown standard deviations $\boldsymbol{\theta}_e = [\sigma_{E'}, \sigma_{E''}]$. The full parameter vector is

$$
\boldsymbol{\theta} = [\boldsymbol{\theta}_m, \boldsymbol{\theta}_e].
$$

### Bayesian Inference

The posterior distribution is obtained via Bayes’ rule:

$$
\pi(\boldsymbol{\theta} \mid \boldsymbol{D})
=
\frac{\pi(\boldsymbol{D} \mid \boldsymbol{\theta}) \, \pi_0(\boldsymbol{\theta})}
{\pi(\boldsymbol{D})}.
$$

Under Gaussian error assumptions, the likelihood becomes

$$
\pi(\boldsymbol{D} \mid \boldsymbol{\theta})
=
\frac{1}{(2\pi)^{N_d} \sigma_{E'}^{N_d} \sigma_{E''}^{N_d}}
\exp\left(
-\sum_{i=1}^{N_d}
\left[
\frac{r_{i,E'}^2}{2\sigma_{E'}^2}
+
\frac{r_{i,E''}^2}{2\sigma_{E''}^2}
\right]
\right),
$$

with logarithmic residuals

$$
r_{i,E'} = \log\!\left(\frac{E'(x_i)}{\mathcal{M}_{E'}(x_i, \boldsymbol{\theta}_m)}\right), \quad
r_{i,E''} = \log\!\left(\frac{E''(x_i)}{\mathcal{M}_{E''}(x_i, \boldsymbol{\theta}_m)}\right).
$$

This formulation is consistent with the deterministic calibration objective while incorporating uncertainty.

### Prior Distributions

Weakly-informative uniform priors are assigned:

$$
\theta_i \sim \mathcal{U}(a_i, b_i), \quad
(a_i, b_i) = (\mu_i - \sqrt{3}\sigma_i,\; \mu_i + \sqrt{3}\sigma_i), \quad \sigma_i = 0.2\,\mu_i.
$$

Error parameters are assigned broad priors:

$$
\sigma_{E'} \sim \mathcal{U}(0,1), \quad
\sigma_{E''} \sim \mathcal{U}(0,1).
$$

### Dimensionality Reduction

Sensitivity analysis identifies $\{\tau_{c_1}, \tau_{c_2}, \beta_1\}$ as non-influential; these are fixed at deterministic values. A physical constraint enforces

$$
E_{c_2} = E_{c_1} \left(\frac{\tau_{c_1}}{\tau_{c_2}}\right)^2,
$$

reducing the inference problem to

$$
\boldsymbol{\theta} = [E_{c_1}, \alpha_1, \alpha_2, \sigma_{E'}, \sigma_{E''}].
$$

Please refer to our [previous](https://onlinelibrary.wiley.com/doi/full/10.1002/eng2.70367) and current papers regarding the sensitivity analysis, influential parameter identification, and proposed constraint linking phases.

### Sampling

Posterior inference is performed using PyMC with the No-U-Turn Sampler (NUTS). Four chains are run with 4,000 tuning iterations and $10^6$ posterior samples per chain, enabling efficient exploration of the parameter space.