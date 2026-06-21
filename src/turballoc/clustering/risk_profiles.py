import pandas as pd
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from turballoc.config import settings
from turballoc.ingest.store import FeatureStore
from turballoc.clustering.features import build_risk_features
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

class RiskClusterer:
    """Unsupervised clustering of daily market-risk states (k-means or GMM)."""

    def __init__(self, n_clusters = 4, method = "kmeans", seed = None):
        self.n_clusters = n_clusters
        self.method = method
        self.seed = settings.random_seed if seed is None else seed
        self.scaler = StandardScaler()
        self.model = None
        self.columns = None

    def fit(self, features):
        self.columns = list(features.columns)
        X = self.scaler.fit_transform(features.to_numpy())
        if self.method == "kmeans":
            self.model = KMeans(n_clusters=self.n_clusters, random_state=self.seed, n_init=10)
        elif self.method == "gmm":
            self.model = GaussianMixture(n_components=self.n_clusters, random_state=self.seed)
        else:
            raise ValueError(f"method must be 'kmeans' or 'gmm', got {self.method!r}")
        self.model.fit(X)
        logger.info("Fitted %s with %d clusters on %d samples",
                    self.method, self.n_clusters, len(features))
        return self

    def predict(self, features):
        if self.model is None:
            raise RuntimeError("call fit() before predict()")
        X = self.scaler.transform(features[self.columns].to_numpy())
        return pd.Series(self.model.predict(X), index=features.index, name="risk_cluster")

    def profiles(self, features, labels = None):
        """Mean (unscaled) feature values per cluster -- the 'profile' of each risk state."""
        labels = self.predict(features) if labels is None else labels
        df = features.copy()
        df["risk_cluster"] = labels.to_numpy()
        return df.groupby("risk_cluster").mean()

def build_risk_clusters(n_clusters = 4, method = "kmeans", store = None):
    """Fit clusters from the feature store and persist day-level labels."""
    store = store or FeatureStore()
    features = build_risk_features(store=store)
    clusterer = RiskClusterer(n_clusters=n_clusters, method=method).fit(features)
    out = features.copy()
    out["risk_cluster"] = clusterer.predict(features)
    out.index.name = "date"
    store.write("risk_clusters", out)
    logger.info("Wrote risk_clusters: %d rows", len(out))
    return clusterer, out
