import sys

import cx_Oracle
import argparse
import jprops


def trace(logged_func):
    """
    Decorator to enable tracelogging. Only use on objects that inherit LoggedObject.
    Only works when decorating methods for LoggedObjects because the
    first arg must be the object being logged (a subclass of LoggedObject)
    """

    def wrapper(*args, **kwargs):
        print(f'entering function \'{logged_func.__name__}\' with args {args}')
        val = logged_func(*args, **kwargs)
        print(f'exited function \'{logged_func.__name__}\' with return value \'{val}\'')
        return val

    return wrapper


def connect(username: str, password: str, hostname: str, db_name: str, port_no: str, logfile=sys.stdout):
    """
    :param username:
    :param password:
    :param hostname:
    :param db_name:
    :param port_no:
    :return: a Connection object
    """
    conn_str = cx_Oracle.makedsn(host=hostname, port=port_no, sid=db_name)
    print(f'connecting to DB with connection string: {conn_str}', file=logfile)
    return cx_Oracle.connect(username, password, conn_str)


def execute_query(conn, statement: str, debug=False, logfile=sys.stdout, **kwargs):
    """
    :param conn:
    :param statement:
    :param debug: enable SQL output for debugging
    :param kwargs:
    :return: a Cursor object
    """
    if debug:
        print(f'executing statement: {statement} with positional args {kwargs}', file=logfile)
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
    ORDER BY table_name ASC
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


def subtract_row_sets(conn1, conn2, table: str, cols: tuple, reverse=False, logfile=sys.stdout):
    """
    Compare the data in @table from @conn1 and @conn2 by columns @cols
    :param table:
    :param conn2:
    :param conn1:
    :param cols: tuple of columns to compare by
    :param reverse: subtract table2 rows from table1 rows instead of the opposite
    :return: rows in table1 not in table2 as compared by cols
    """

    select_count = f"""
    SELECT COUNT(*) FROM {table}
    """

    columns = str(cols).lstrip('(').rstrip(')').replace('\'', '').rstrip(',')
    select_all = f"""
    SELECT {columns} 
    FROM {table} 
    """

    c1 = conn1.cursor()
    c2 = conn2.cursor()

    # execute_query failing with ORA-00903: invalid table name ??? used string.format instead

    # ensure the entire table is fetched by setting cursor size to no. of rows that will return
    total_rows = c1.execute(select_count).fetchone()[0]
    t1_data = set(c1.execute(select_all).fetchmany(numRows=total_rows))

    try:
        total_rows = int(c2.execute(select_count).fetchone()[0])
        t2_data = set(c1.execute(select_all).fetchmany(numRows=total_rows))
    except cx_Oracle.DatabaseError as e:
        if 'ORA-00942' in str(e):
            print(f'table {table} does not exist in DB2, comparison cannot continue', file=logfile)
            return
        else:
            raise e

    if reverse:
        return tuple(t2_data - t1_data)
    return tuple(t1_data - t2_data)


def compare_table_data(args, logfile):

    conn1 = connect(
        username=args.username1,
        password=args.passwd1,
        hostname=args.hostname1,
        db_name=args.db_name1,
        port_no=args.port_no1,
        logfile=logfile
    )

    conn2 = connect(
        username=args.username2,
        password=args.passwd2,
        hostname=args.hostname2,
        db_name=args.db_name2,
        port_no=args.port_no2,
        logfile=logfile
    )

    user_tables = [result_row[0] for result_row in select_table_names_for_user(conn1, args.username1.upper())]
    for t in user_tables:
        pk = get_pk_for_table(conn1, t, args.username1.upper())
        if pk:  # filter tables that have no PK constraint or columns that begin with "ID"
            print(f'========== {t} ==========', file=logfile)
            diff_rows = subtract_row_sets(conn1, conn2, t, pk, args.reverse, logfile=logfile)
            if diff_rows:
                for row in diff_rows:
                    print(row, file=logfile)
        else:
            print(f'table {t} has no primary key constraint or column that begins with \'ID_\'', file=logfile)


def compare_admin_cfgs(args, logfile):

    conn1 = connect(
        username=args.admin_username1,
        password=args.admin_passwd1,
        hostname=args.hostname1,
        db_name=args.db_name1,
        port_no=args.port_no1,
        logfile=logfile
    )

    conn2 = connect(
        username=args.admin_username2,
        password=args.admin_passwd2,
        hostname=args.hostname2,
        db_name=args.db_name2,
        port_no=args.port_no2,
        logfile=logfile
    )


def main():
    parser = argparse.ArgumentParser(description='Find data in DB1 that isn\'t in DB2. Schema must be identical. ')
    parser.add_argument('hostname1', help='The name of the network host DB1 resides on')
    parser.add_argument('db_name1', help='The SID of DB1 to connect to on \'hostname1\'')
    parser.add_argument('port_no1', help='The port number that \'db_name1\' is listening on on host \'hostname1\'')
    parser.add_argument('username1', help='The name of the user to connect to \'db_name1\' with')
    parser.add_argument('passwd1', help='Password for the user supplied by \'username1\'')

    parser.add_argument('hostname2', help='The name of the network host DB2 resides on')
    parser.add_argument('db_name2', help='The SID of DB2 to connect to on \'hostname2\'')
    parser.add_argument('port_no2', help='The port number that \'db_name2\' is listening on on host \'hostname2\'')
    parser.add_argument('username2', help='The name of the user to connect to \'db_name2\' with')
    parser.add_argument('passwd2', help='Password for the user supplied by \'username2\'')

    parser.add_argument('admin_username1', help='Username for the administrator user for DB1')
    parser.add_argument('admin_passwd1', help='Password for user \'admin_username1\'')
    parser.add_argument('admin_username2', help='Username for the administrator user for DB2')
    parser.add_argument('admin_passwd2', help='Password for user \'admin_username2\'')

    opts = parser.add_mutually_exclusive_group()
    opts.add_argument('-r', '--reverse',
                      help='Find data in DB2 not in DB1, the opposite of a normal run',
                      action='store_true')

    opts.add_argument('-x', '--administrative',
                      help='Run comparison on roles, privileges and other administrative '
                           'configurations instead of regular table data',
                      action='store_true')

    with open('./out.log', 'w') as logfile:
        try:
            with open('dbs.properties') as p:
                properties = jprops.load_properties(p)

                username1 = properties['db1.username']
                password1 = properties['db1.passwd']
                hostname1 = properties['db1.hostname']
                dbname1 = properties['db1.db_name']
                port_no1 = properties['db1.port_no']

                username2 = properties['db2.username']
                password2 = properties['db2.passwd']
                hostname2 = properties['db2.hostname']
                dbname2 = properties['db2.db_name']
                port_no2 = properties['db2.port_no']

                reverse = properties['reverse']
                administrative = properties['administrative']

                admin_username1 = properties['db1.admin_username']
                admin_passwd1 = properties['db1.admin_passwd']

                admin_username2 = properties['db2.admin_username']
                admin_passwd2 = properties['db2.admin_passwd']

                # fixme allow for options when using file for input
                args = parser.parse_args([
                    hostname1, dbname1, port_no1, username1, password1,
                    hostname2, dbname2, port_no2, username2, password2,
                    admin_username1, admin_passwd1,
                    admin_username2, admin_passwd2,
                    # '--reverse' if reverse else None,
                    # '--administrative' if administrative else None
                ])
        except Exception as e:
            print('no file detected, using CLI input', file=logfile)
            print(str(e))
            args = parser.parse_args()

        if args.administrative:
            compare_admin_cfgs(args, logfile)
        else:
            compare_table_data(args, logfile)


if __name__ == '__main__':
    main()
