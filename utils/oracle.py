import oracledb

def database_connection_exec(procedure: str): # To use when "exec xxxx" (stored procedures)
    un = 'MPI'
    cs = 'bcss-oracle-bcss-bcss-18680.cqger35bxcwy.eu-west-2.rds.amazonaws.com/TSTBCS01'
    pw = 'g0blin'

    with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
        with connection.cursor() as cursor:
            for r in cursor.callproc(procedure):
                print(r)

def database_connection_query(sql: str): # To use when "select a from b"
    un = 'MPI'
    cs = 'bcss-oracle-bcss-bcss-18680.cqger35bxcwy.eu-west-2.rds.amazonaws.com/TSTBCS01'
    pw = 'g0blin'

    with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
        with connection.cursor() as cursor:
            for r in cursor.execute(sql):
                print(r)
