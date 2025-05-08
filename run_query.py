from db_connect import connect
import pandas as pd

def run_query(sql):
    conn = connect()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df
