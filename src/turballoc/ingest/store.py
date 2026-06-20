from pathlib import Path
import duckdb
import pandas as pd
from turballoc.config import settings
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

class FeatureStore:
    def __init__(self, path: Path | None = None):
        self.path = Path(path or settings.feature_store_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, table, frame):
        df = frame.reset_index() if frame.index.name is not None else frame.copy()
        con = duckdb.connect(str(self.path))
        try:
            con.register("df_tmp", df)
            con.execute(f'CREATE OR REPLACE TABLE "{table}" AS SELECT * FROM df_tmp')
        finally:
            con.unregister("df_tmp")
            con.close()
        logger.info("Wrote %d rows to table", len(df))

    def read(self, table):
        con = duckdb.connect(str(self.path))
        try:
            df = con.execute(f'SELECT * FROM "{table}"').df()
        finally:
            con.close()
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()
        return df

    def list_tables(self):
        con = duckdb.connect(str(self.path))
        try:
            rows = con.execute("SHOW TABLES").fetchall()
        finally:
            con.close()
        return [t[0] for t in rows]
