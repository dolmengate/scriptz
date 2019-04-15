import cx_Oracle
import argparse


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


def execute_query(conn, statement, **kwargs):
    """
    :param conn:
    :param statement:
    :param kwargs:
    :return: a Cursor object
    """
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
    :param conn:
    :param table:
    :return: a tuple consisting of columns which make up the PK for the table
    """

    # first check for an actual constraint
    pk = find_pk_constraint_for_table(conn, table, owner_user)
    if pk:
        return pk   # fixme this is returning a Cursor?
    # else use the first 'ID' column in the table
    else:
        return find_first_id_col_for_tab(conn, table, owner_user)


def find_first_id_col_for_tab(conn, table, table_owner):
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
    execute_query(conn, stmt, owner_user=table_owner, tab=table)


def find_pk_constraint_for_table(conn, table: str, owner_user: str):
    stmt = """
    SELECT *
    FROM all_constraints
    WHERE table_name = :tab 
    AND owner = :owner_user 
    AND constraint_type = 'P'
    """
    return execute_query(conn, stmt, tab=table, owner_user=owner_user)


def compare_data(table1: str, table2: str, cols: list):
    """
    :param table1:
    :param table2:
    :param cols:  columns to compare by
    :return: rows in table1 not in table2 as compared by cols
    """
    pass


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
    args = parser.parse_args()

    conn = connect(
        username=args.username,
        password=args.passwd,
        hostname=args.hostname,
        db_name=args.db_name,
        port_no=args.port_no)
    tables = [table_name[0] for table_name in select_table_names_for_user(conn, args.username.upper())]
    for t in tables:
        print(get_pk_for_table(conn, t, args.username.upper()))


if __name__ == '__main__':
    main()
