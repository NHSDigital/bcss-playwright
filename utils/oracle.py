import getpass
import oracledb

def database_connection():
    un = 'scott'
    cs = 'localhost/orclpdb'
    pw = getpass.getpass(f'Enter password for {un}@{cs}: ')

    with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
        with connection.cursor() as cursor:
            sql = """select sysdate from dual"""
            for r in cursor.execute(sql):
                print(r)
