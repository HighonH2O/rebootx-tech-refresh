"""Sample main.py for the test fixture — simulates a FastAPI app."""

from fastapi import FastAPI
from db import get_connection

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/customers")
def get_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    return cursor.fetchall()
