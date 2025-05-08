import pyodbc
import json

def connect():
    with open('db_config.json') as f:
        config = json.load(f)

    if config.get("trusted_connection", "").lower() == "yes":
        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"Trusted_Connection=yes"
        )
    else:
        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"UID={config['user']};"
            f"PWD={config['password']}"
        )

    return pyodbc.connect(conn_str)
