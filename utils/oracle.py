import oracledb
import os
from dotenv import load_dotenv

class OracleDB:
    def __init__(self):
        load_dotenv()
        self.user = os.getenv("un")
        self.dns = os.getenv("cs")
        self.password = os.getenv("pw")

    def exec_bcss_timed_events(self, nhs_no: str): # Executes bcss_timed_events when given an NHS number
        try:
            print("Attempting DB connection...")
            conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dns)
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

    def populate_ui_approved_users_table(self, user: str): # To add users to the UI_APPROVED_USERS table
        try:
            print("Attempting DB connection...")
            conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dns)
            print(conn.version, "DB connection successful!")
            try:
                print("Attempting to write to the db...")
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO UI_APPROVED_USERS (OE_USER_CODE) VALUES ('{user}')")
                conn.commit()
                print(conn.version, "DB write successful!")
            except Exception as dbWriteError:
                print(f"Failed to write to the DB! with write error {dbWriteError}")
            finally:
                if conn is not None:
                    conn.close()
        except Exception as connectionError:
                print(f"Failed to connect to the DB! with connection error {connectionError}")

    def delete_all_users_from_approved_users_table(self):  # To remove all users from the UI_APPROVED_USERS table
        try:
            print("Attempting DB connection...")
            conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dns)
            print(conn.version, "DB connection successful!")
            try:
                print("Attempting to delete users from DB table...")
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM UI_APPROVED_USERS WHERE OE_USER_CODE is not null")
                conn.commit()
                print(conn.version, "DB table values successfully deleted!")
            except Exception as dbValuesDeleteError:
                print(f"Failed to delete values from the DB table! with data deletion error {dbValuesDeleteError}")
            finally:
                if conn is not None:
                    conn.close()
        except Exception as connectionError:
            print(f"Failed to connect to the DB! with connection error {connectionError}")

    # The following two functions are commented out as they are not used currently, but may be needed in future compartments

    # def execute_stored_procedure(self, procedure: str): # To use when "exec xxxx" (stored procedures)
    #     try:
    #         print("Attempting DB connection...")
    #         conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dns)
    #         print(conn.version, "DB connection successful!")
    #         try:
    #             print(f"Attempting to execute stored procedure: {procedure}")
    #             cursor = conn.cursor()
    #             cursor.callproc(procedure)
    #             print(conn.version, "stored procedure execution successful!")
    #         except Exception as executionError:
    #             print(f"Failed to execute stored procedure with execution error: {executionError}")
    #         finally:
    #             if conn is not None:
    #                 conn.close()
    #     except Exception as connectionError:
    #             print(f"Failed to connect to the DB! with connection error: {connectionError}")

    # def execute_query(self, query: str,): # To use when "select xxxx" (stored procedures)
    #     try:
    #         print("Attempting DB connection...")
    #         conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dns)
    #         print(conn.version, "DB connection successful!")
    #         try:
    #             print(f"Attempting to execute query: {query}")
    #             cursor = conn.cursor()
    #             cursor.execute(query)
    #             result = cursor.fetchall()
    #             print(conn.version, "query execution successful!")
    #         except Exception as executionError:
    #             print(f"Failed to execute query with execution error {executionError}")
    #         finally:
    #             if conn is not None:
    #                 conn.close()
    #                 return result
    #     except Exception as connectionError:
    #             print(f"Failed to connect to the DB! with connection error {connectionError}")
