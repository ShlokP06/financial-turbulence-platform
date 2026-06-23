from skopt import gp_minimize
from skopt.space import Real
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

def optimize_risk_av(objective_fn, bounds = (0.5, 10.0), n_calls = 25, seed = None):
    """Bayesian search over risk-aversion delta to MAXIMIZE objective_function.
    Objective Function returns a score to maximize (e.g. Sharpe Ratio).
    gp_minimize minimizes, so we negate. Returns (best_delta, best_score)."""
    space = [Real(bounds[0], bounds[1], name = "risk_aversion")]
    result = gp_minimize(lambda params: -objective_fn(params[0]), space,
                         n_calls = n_calls, random_state = seed)
    best_delta = result.x[0]
    best_score = -result.fun
    logger.info("Best risk aversion = %.4f score = %.4f", best_delta, best_score)
    return best_delta, best_score

