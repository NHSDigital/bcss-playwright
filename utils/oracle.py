import oracledb
import os
from dotenv import load_dotenv

# Edit to "try:"

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

def populate_ui_approved_users_table(user: str): # To add users to the UI_APPROVED_USERS table
    load_dotenv()
    un = os.getenv("un")
    cs = os.getenv("cs")
    pw = os.getenv("pw")

    try:
        print("Attempting DB connection...")
        conn = oracledb.connect(user=un, password=pw, dsn=cs)
        print(conn.version, "DB connection successful!")
        try:
            print("Attempting to write to the db...")
            cursor = conn.cursor()
            cursor.execute(f'INSERT INTO "UI_APPROVED_USERSf" (OE_USER_CODE) VALUES ({user})')
            print(conn.version, "DB write successful!")
        except Exception as connectionError:
            print(f"Failed to connect to the DB! with connection error {connectionError}")
        finally:
            if conn is not None:
                conn.close()
    except Exception as dbWriteError:
        print(f"Failed to write to the DB! with write error {dbWriteError}")









