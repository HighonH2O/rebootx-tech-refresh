"""Sample ETL script for the test fixture — imports pandas and the local db module."""

import pandas as pd
from db import get_engine


def load_customers():
    """Load customers from PostgreSQL into a DataFrame."""
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM customers", engine)
    return df


def transform(df):
    """Simple transformation."""
    df["full_name"] = df["first_name"] + " " + df["last_name"]
    return df


if __name__ == "__main__":
    data = load_customers()
    result = transform(data)
    print(result.head())
