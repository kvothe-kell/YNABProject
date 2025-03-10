# Third-Party Imports
from data import database
from sqlalchemy import create_engine
import pandas as pd
from flask_caching import Cache

# Create a cache instance
cache = Cache()


def init_cache(app):
    """Call this function in the main app file to initialize caching."""
    cache.init_app(app, config={"CACHE_TYPE": "SimpleCache"})  # Note: SimpleCache in newer versions


def fetch_transactions():
    @cache.memoize(timeout=300)  # Cache data for 5 minutes
    def get_transactions():
        engine = create_engine(database.DATABASE_URI)
        df = pd.read_sql("SELECT * FROM transactions", engine)
        return df

    return get_transactions()
