import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "futbols_secret_2025"

# ── Database connection ──────────────────────────────────────────
def get_db():
    db = Path(__file__).parent / "futbols.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_path = Path(__file__).parent / "futbols.db"
    if db_path.exists():
        return
