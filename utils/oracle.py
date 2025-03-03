import oracledb
import os
from dotenv import load_dotenv

def database_connection_exec(procedure: str): # To use when "exec xxxx" (stored procedures)
    load_dotenv()
    un = os.getenv("un")
    cs = os.getenv("cs")
    pw = os.getenv("pw")

    with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
        with connection.cursor() as cursor:
            for r in cursor.callproc(procedure):
                print(r)

def database_connection_query(sql: str): # To use when "select a from b"
    load_dotenv()
    un = os.getenv("un")
    cs = os.getenv("cs")
    pw = os.getenv("pw")

    with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
        with connection.cursor() as cursor:
            for r in cursor.execute(sql):
                print(r)
            return r
