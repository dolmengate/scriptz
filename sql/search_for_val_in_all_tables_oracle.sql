DECLARE
  match_count INTEGER;
-- Type the owner of the tables you are looking at
  v_owner VARCHAR2(255) :='DBOWNER';

-- Type the data type you are look at (in CAPITAL)
-- VARCHAR2, NUMBER, etc.
  v_data_type VARCHAR2(255) :='VARCHAR2';

-- Type the string you are looking at
  v_search_string VARCHAR2(4000) :='00101';

BEGIN
 
  FOR t IN (SELECT table_name, column_name FROM all_tab_cols where owner=v_owner and data_type = v_data_type) LOOP

    EXECUTE IMMEDIATE 
    'SELECT COUNT(*) FROM '||t.table_name||' WHERE '||t.column_name||' = :1'
    INTO match_count
    USING v_search_string;

    IF match_count > 0 THEN
      dbms_output.put_line( output whatever you want here );
    END IF;

  END LOOP;
END;
