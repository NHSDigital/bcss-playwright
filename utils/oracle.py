import oracledb
import os
from dotenv import load_dotenv

def database_connection_exec(procedure: str): # To use when "exec xxxx" (stored procedures)
    load_dotenv()
    un = os.getenv("un")
    cs = os.getenv("cs")
    pw = os.getenv("pw")

    try:
        print("Attempting DB connection...")
        conn = oracledb.connect(user=un, password=pw, dsn=cs)
        print(conn.version, "DB connection successful!")
        try:
            print(f"Attempting to execute stored procedure: {procedure}")
            cursor = conn.cursor()
            cursor.callproc(procedure)
            print(conn.version, "stored procedure execution successful!")
        except Exception as executionError:
            print(f"Failed to execute stored procedure with execution error: {executionError}")
        finally:
            if conn is not None:
                conn.close()
    except Exception as connectionError:
            print(f"Failed to connect to the DB! with connection error: {connectionError}")

def exec_bcss_timed_events(nhs_no: str): # To use when "exec xxxx" (stored procedures)
    load_dotenv()
    un = os.getenv("un")
    cs = os.getenv("cs")
    pw = os.getenv("pw")

    try:
        print("Attempting DB connection...")
        conn = oracledb.connect(user=un, password=pw, dsn=cs)
        print(conn.version, "DB connection successful!")
        try:
            print(f"Attempting to get subject_id from nhs number: {nhs_no}")
            cursor = conn.cursor()
            cursor.execute(f"SELECT SCREENING_SUBJECT_ID FROM SCREENING_SUBJECT_T WHERE SUBJECT_NHS_NUMBER = {int(nhs_no)}")
            result = cursor.fetchall()
            subject_id = result[0][0]
            print(conn.version, "Able to extract subject ID")
            try:
                print(f"Attempting to execute stored procedure: {f"'bcss_timed_events', [subject_id,'Y']"}")
                cursor = conn.cursor()
                cursor.callproc('bcss_timed_events', [subject_id,'Y'])
                print(conn.version, "stored procedure execution successful!")
            except Exception as spExecutionError:
                print(f"Failed to execute stored procedure with execution error: {spExecutionError}")
        except Exception as queryExecutionError:
            print(f"Failed to to extract subject ID with error: {queryExecutionError}")
        finally:
            if conn is not None:
                conn.close()
    except Exception as connectionError:
            print(f"Failed to connect to the DB! with connection error: {connectionError}")

def database_connection_query(query: str,): # To use when "exec xxxx" (stored procedures)
    load_dotenv()
    un = os.getenv("un")
    cs = os.getenv("cs")
    pw = os.getenv("pw")

    try:
        print("Attempting DB connection...")
        conn = oracledb.connect(user=un, password=pw, dsn=cs)
        print(conn.version, "DB connection successful!")
        try:
            print(f"Attempting to execute query: {query}")
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            print(conn.version, "query execution successful!")
        except Exception as executionError:
            print(f"Failed to execute query with execution error {executionError}")
        finally:
            if conn is not None:
                conn.close()
                return result
    except Exception as connectionError:
            print(f"Failed to connect to the DB! with connection error {connectionError}")

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
        except Exception as dbWriteError:
            print(f"Failed to write to the DB! with write error {dbWriteError}")
        finally:
            if conn is not None:
                conn.close()
    except Exception as connectionError:
            print(f"Failed to connect to the DB! with connection error {connectionError}")








