-- create new user
CREATE USER user_name_here IDENTIFIED BY user_pw_here DEFAULT TABLESPACE users TEMPORARY TABLESPACE TEMP QUOTA UNLIMITED ON users;


-- search all tables for column with specific value
SET SERVEROUTPUT ON SIZE 100000

DECLARE
  match_count INTEGER;
  v_owner VARCHAR2(255) :='TABLE OWNER';

-- VARCHAR2, NUMBER, etc.
  v_data_type VARCHAR2(255) :='VARCHAR2';

  v_search_string VARCHAR2(4000) :='search string'

BEGIN
  FOR t IN (SELECT table_name, column_name FROM all_tab_cols where owner=v_owner and data_type = v_data_type) LOOP

    EXECUTE IMMEDIATE 
    'SELECT COUNT(*) FROM '||t.table_name||' WHERE '||t.column_name||' = :1'
    INTO match_count
    USING v_search_string;

    IF match_count > 0 THEN
      dbms_output.put_line( t.table_name ||' '||t.column_name||' '||match_count );
    END IF;

  END LOOP;
END;


-- create new role
CREATE ROLE schema_owner_role;

-- grant user privilege or privileges
GRANT ALTER SESSION TO XSTORE_1500_800;

-- find user privileges
SELECT * FROM DBA_SYS_PRIVS WHERE grantee = 'OWNER';
SELECT * FROM DBA_SYS_PRIVS WHERE grantee = 'USERUSER';


-- find role for user
SELECT * FROM dba_role_privs WHERE grantee = 'OWNER'
SELECT * FROM dba_role_privs WHERE grantee = 'USERUSER'


-- find roles GRANTED TO ROLE
select * from role_role_privs WHERE ROLE = 'SCHEMA_OWNER_ROLE'
SELECT * FROM role_role_privs WHERE ROLE = 'DATA_SOURCE_ROLE'


-- find ROLE PRIVILEGES
SELECT * FROM ROLE_SYS_PRIVS WHERE ROLE = 'SCHEMA_OWNER_ROLE'
SELECT * FROM ROLE_SYS_PRIVS WHERE ROLE = 'DATA_SOURCE_ROLE'

commit

select * from all_synonyms WHERE table_owner = 'OWNER'
select * from dba_synonyms

-- grant link creation privilege
GRANT CREATE DATABASE LINK TO DBOWNER

-- create a link to a remote database connecting as the remote user schemao
CREATE SHARED DATABASE LINK schemao_00101_3
CONNECT TO schemao IDENTIFIED BY schemao AUTHENTICATED BY schemao IDENTIFIED BY schemao
USING '(DESCRIPTION = (ADDRESS = (PROTOCOL = TCP)(HOST = bo-test1.fffo.local)(PORT = 1521)) (CONNECT_DATA = (SERVER = DEDICATED) (SERVICE_NAME = ORCL00101)))'

-- delete a created database link
DROP DATABASE LINK schemao_00101_3;

-- view user's database link
SELECT * FROM user_db_links;

-- set service names to be referenced by database link
 ALTER system SET SERVICE_NAMES='ORCL00101', 'BOPRDDB'

-- view various database parameters
select name, value from v$parameter where name in ('db_name', 'db_domain', 'global_names', 'service_names');  

-- find max open cursors at any point vs max cursors
SELECT  max(a.value) as highest_open_cur, p.value as max_open_cur 
FROM v$sesstat a, v$statname b, v$parameter p 
WHERE  a.statistic# = b.statistic#  
and b.name = 'opened cursors current' 
and p.name= 'open_cursors' 
group by p.value;


-- find all open cursors
select a.value, s.username, s.sid, s.serial#
from v$sesstat a, v$statname b, v$session s
where a.statistic# = b.statistic#  and s.sid=a.sid
and b.name = 'opened cursors current';

-- change number of max open cursors
ALTER SYSTEM SET open_cursors = 500 SCOPE=BOTH;

-- request kill OF inactive sessions
-- this can FREE up cursors FROM the 'Max cursors exceeded' error
BEGIN
  FOR r IN (select sid,serial# from v$session where status = 'INACTIVE')
  LOOP
    EXECUTE IMMEDIATE 'alter system kill session ''' || r.sid 
      || ',' || r.serial# || '''';
  END LOOP;
END;

-- delete all tables starting/ending with a given string
BEGIN
  FOR c IN ( SELECT table_name FROM user_tables WHERE table_name LIKE 'EXT_%' )
  LOOP
    EXECUTE IMMEDIATE 'DROP TABLE ' || c.table_name;
  END LOOP;
END;


-- user account unlock
ALTER USER useruser ACCOUNT UNLOCK;
-- change user password
alter user useruser identified by user;
ALTER USER owner IDENTIFIED BY owner;

-- do both at once
alter user myuser identified by mynewpassword account unlock;

SELECT resource_name, limit
FROM dba_profiles 
WHERE profile = 'DEFAULT'
AND resource_type = 'PASSWORD';

ALTER PROFILE DEFAULT LIMIT PASSWORD_LIFE_TIME UNLIMITED;
ALTER PROFILE DEFAULT LIMIT FAILED_LOGIN_ATTEMPTS UNLIMITED;
ALTER PROFILE DEFAULT LIMIT PASSWORD_LOCK_TIME UNLIMITED;


-- view errors from procedure call
select * from user_errors where name='SP_SELECT_CUSTOMER'
