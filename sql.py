import pyodbc
import pandas as pd

from dynamics import *

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

server = "server"
port = "port"
database = "database"
username = "username"
password = "password"


conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={server},{port};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"
)


def load_data(year, region, type_mo):
    years_list = [int(year) - 1, int(year)]
    data = {}
    data['years'] = years_list
    data['region'] = region
    data['type_mo'] = type_mo

    for year in years_list:
        data[year] = {}
        try:
            conn = pyodbc.connect(conn_str)

            raw_query = """
                SELECT name_value, value
                FROM dbo.StatInfo
                WHERE year = ? AND region = ? AND tip_mo = ?
                """

            df_raw = pd.read_sql(raw_query, conn, params=[year, region, type_mo])
            conn.close()

            for _, row in df_raw.iterrows():
                name = row['name_value']
                value = row['value']
                data[year][name] = convert_to_str(value)
        except Exception as e:
            print(f"Ошибка: {e}")

    data = find_dynamics(data)
    return data

