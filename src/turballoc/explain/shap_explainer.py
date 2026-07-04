import numpy as np
import pandas as pd
import shap
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def explain_model(predict_fn, background, instances, nsamples = "auto"):
    """SHAP values for black box prediction function.
    Returns (n_instances, n_features) DataFrame of contributions. """
    bg = background.to_numpy() if hasattr(background, "to_numpy") else np.asarray(background)
    X = instances.to_numpy() if hasattr(instances, "to_numpy") else np.asarray(instances)
    explainer = shap.KernelExplainer(predict_fn, bg)
    values = np.asarray(explainer.shap_values(X, nsamples=nsamples))
    cols = list(instances.columns) if hasattr(instances, "columns") else None
    idx = instances.index if hasattr(instances, "index") else None
    logger.info("Computed SHAP values for %d instances x %d features", values.shape[0], values.shape[1])
    return pd.DataFrame(values, columns = cols, index = idx)

def feature_importance(shap_df):
    "Mean Absolute SHAP per feature, ranked high to low."
    return shap_df.abs().mean().sort_values(ascending = False)

def simple_counterfactual(predict_fn, instance, feature, grid):
    rows = []
    for v in grid:
        x = instance.copy()
        x[feature] = v
        pred = float(predict_fn(np.asarray(x, dtype = float).reshape(1, -1))[0])
        rows.append({feature: v, "prediction": pred})
    return pd.DataFrame(rows)
