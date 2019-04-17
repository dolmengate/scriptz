import cx_Oracle
import argparse


def trace(logged_func):
    """
    Decorator to enable tracelogging. Only use on objects that inherit LoggedObject.
    Only works when decorating methods for LoggedObjects because the
    first arg must be the object being logged (a subclass of LoggedObject)
    """
    def wrapper(*args, **kwargs):
        print('entering function \'{}\' with args {}'.format(logged_func.__name__, args))
        val = logged_func(*args, **kwargs)
        print('exited function \'{}\' with return value \'{}\''.format(logged_func.__name__, val))
        return val
    return wrapper


def connect(username: str, password: str, hostname: str, db_name: str, port_no: str):
    """
    :param username:
    :param password:
    :param hostname:
    :param db_name:
    :param port_no:
    :return: a Connection object
    """
    conn_str = cx_Oracle.makedsn(host=hostname, port=port_no, sid=db_name)
    return cx_Oracle.connect(username, password, conn_str)


def execute_query(conn, statement: str, **kwargs):
    """
    :param conn:
    :param statement:
    :param kwargs:
    :return: a Cursor object
    """
    print('executing statement: {} with positional args {}'.format(statement, kwargs))
    cursor = conn.cursor()
    cursor.execute(statement, kwargs)
    return cursor


def select_table_names_for_user(conn, user: str):
    """
    Get all tables user owns
    :param conn:
    :param user:
    :return: Cursor object
    """

    stmt = """
    SELECT DISTINCT table_name
    FROM all_tab_cols 
    WHERE owner = :owner_user
    """
    return execute_query(conn, stmt, owner_user=user)


def get_pk_for_table(conn, table: str, owner_user: str):
    """
    Find the primary key for a given table
    :param owner_user:
    :param conn:
    :param table:
    :return: a tuple consisting of columns which make up the PK for the table
    """

    # first check for an actual constraint
    pk = find_pk_constraint_for_table(conn, table, owner_user)
    if pk:
        return pk
    # else use the first 'ID' column in the table
    else:
        return find_first_id_col_for_table(conn, table, owner_user)


def find_first_id_col_for_table(conn, table, table_owner):
    stmt = """
        SELECT * 
        FROM (SELECT column_name 
            FROM all_tab_cols 
            WHERE owner = :owner_user
            AND table_name = :tab 
            AND column_name LIKE 'ID_%' 
            ORDER BY column_id) 
        WHERE ROWNUM  = 1
        """
    return execute_query(conn, stmt, owner_user=table_owner, tab=table).fetchone()


def find_pk_constraint_for_table(conn, table: str, owner_user: str):
    """
    Find and return the list of columns that make up a table's Primary key
    :param conn:
    :param table:
    :param owner_user:
    :return:    a tuple of columns for @table's PK
    """

    stmt = """
    SELECT acc.column_name
    FROM all_constraints ac, all_cons_columns acc 
    WHERE acc.constraint_name = ac.constraint_name 
    AND ac.table_name = :tab
    AND ac.owner = :owner_user
    AND ac.constraint_type = 'P'
    """
    return tuple([col[0] for col in execute_query(conn, stmt, tab=table, owner_user=owner_user)])


def subtract_row_sets(conn1, conn2, table: str, cols: tuple):
    """
    Compare the data in @table from @conn1 and @conn2 by columns @cols
    :param table:
    :param conn2:
    :param conn1:
    :param cols: tuple of columns to compare by
    :return: rows in table1 not in table2 as compared by cols
    """

    select_count = """
    SELECT COUNT(*) FROM {table}
    """.format(table=table)

    select_all = """
    SELECT {cols} 
    FROM {table} 
    """.format(cols=str(cols).lstrip('(').rstrip(')').replace('\'', '').rstrip(','),
               table=table)

    c1 = conn1.cursor()
    c2 = conn2.cursor()

    # execute_query failing with ORA-00903: invalid table name ??? used string.format instead

    # ensure the entire table is fetched by setting cursor size to rows that will return
    total_rows = c1.execute(select_count).fetchone()[0]
    set1 = set(c1.execute(select_all).fetchmany(numRows=total_rows))

    total_rows = int(c2.execute(select_count).fetchone()[0])
    set2 = set(c1.execute(select_all).fetchmany(numRows=total_rows))

    return tuple(set1 - set2)


def print_record(table1: str, table2: str, record):
    """
    print a formatted record in @table1 that's not in @table2
    :param user:
    :param table:
    :param record:
    :return:
    """
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hostname', help='The name of the network host the DB resides on')
    parser.add_argument('db_name', help='The SID of the database to connect to on the \'hostname\' argument')
    parser.add_argument('port_no', help='The port number that \'db_name\' is listening on on host \'hostname\'')
    parser.add_argument('username', help='The name of the user to connect to \'db_name\' with')
    parser.add_argument('passwd', help='Password for the user supplied by \'username\'')
    args = parser.parse_args(['localhost', 'orcl', '1522', 'owner', 'dbowner'])

    conn = connect(
        username=args.username,
        password=args.passwd,
        hostname=args.hostname,
        db_name=args.db_name,
        port_no=args.port_no)
    tables = [result_row[0] for result_row in select_table_names_for_user(conn, args.username.upper())]
    for t in tables:
        pk = get_pk_for_table(conn, t, args.username.upper())
        if pk:  # filter tables that have no PK constraint or columns that begin with "ID"
            diff_rows = subtract_row_sets(conn, conn, t, pk)
            if diff_rows:
                for row in diff_rows:
                    print(row)
        else:
            print('table {} has no primary key constraint or column that begins with \'ID_\''.format(t))


if __name__ == '__main__':
    main()
