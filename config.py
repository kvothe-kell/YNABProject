from data import database
from dash import callback_context
from flask_caching import Cache
from sqlalchemy import create_engine
import pandas as pd

# Caching example to prevent redundant queries
cache = Cache(config={"CACHE_TYPE": 'simple'})


def fetch_transactions():
    if callback_context.triggered:  # Check if this was triggered by an event
        return cache.get("transactions")

    engine = create_engine(database.DATABASE_URI)
    df = pd.read_sql("SELECT * FROM transactions", engine)
    cache.set("transactions", df, timeout=300)  # Cache for 5 minutes
    return df
