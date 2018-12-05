#! /bin/bash

function usage {
    echo "usage: $programname inputfile.txt numbergtt0lt4000 > youroutputfile.sql"
    exit 1
}

function concat_arr_str() {
	SRC_STR=$1
	START=$2
	CHUNK_LEN=$3
	FORM_STR=$4
	SLICE=${SRC_STR:$START:$CHUNK_LEN}

	echo "$FORM_STR'$SLICE', "
}

if [[ "$1" != *.txt ]] || [[ "$2" -lt 0 ]] || [[ "$2" -gt 4000 ]]; then
	usage
fi

DATA_STRING=$(head -1 "$1")
INSERT_STMT=$(tail -1 "$1")
CHUNK_LEN=$2
DATA_STRING_LEN=${#DATA_STRING}
SQL_ARR_STRING=""
ARR_LEN=0

FINAL_CHUNK=""
FINAL_CHUNK_LEN=0

>&2 echo "Data length is $DATA_STRING_LEN"
>&2 echo "Supplied chunk length is $CHUNK_LEN"
>&2 echo "Supplied INSERT statement is $INSERT_STMT"

for i in $(seq 0 "$CHUNK_LEN" "$DATA_STRING_LEN"); do
	((ARR_LEN++))
	if [ $((DATA_STRING_LEN - i)) -lt "$CHUNK_LEN" ]; then
		FINAL_CHUNK=${DATA_STRING:i:$((DATA_STRING_LEN - i))}
		FINAL_CHUNK_LEN=${#FINAL_CHUNK}
		break
	fi
	SQL_ARR_STRING=$(concat_arr_str "$DATA_STRING" "$i" $CHUNK_LEN "$SQL_ARR_STRING")
done

>&2 echo "Length of SQL array string is $ARR_LEN"

IFS='' read -r -d '' SQL <<'EOF'
DECLARE 
  blob_pointer blob; 
  bindat raw(%4);
  chunk varchar2(%4);

BEGIN 
	%1
 	dbms_lob.open( blob_pointer, dbms_lob.lob_readwrite );
 	DECLARE
 		TYPE array_t IS varray( %3 ) OF VARCHAR2( %4 );
		ARRAY array_t := array_t( %2 );
	    final_bin raw( %5 );
  		final_chunk varchar2( %5 );
	BEGIN 
		FOR i IN 1.. array.count LOOP
			chunk := array(i);
			bindat := HEXTORAW( chunk );
			dbms_lob.writeappend( blob_pointer, UTL_RAW.LENGTH(bindat), bindat );
		END LOOP;
		final_chunk := '%6';
	 	final_bin := HEXTORAW( final_chunk );
	 	dbms_lob.writeappend( blob_pointer, UTL_RAW.LENGTH(final_chunk), final_bin );	
	END;
	dbms_lob.close( LOB_LOC =>blob_pointer );
END;
EOF

SQL=$(echo "$SQL" | sed "s/%1/$INSERT_STMT/g")
SQL=$(echo "$SQL" | sed "s/%2/$SQL_ARR_STRING/g")
SQL=$(echo "$SQL" | sed "s/%3/$ARR_LEN/g")
SQL=$(echo "$SQL" | sed "s/%4/$CHUNK_LEN/g")
SQL=$(echo "$SQL" | sed "s/%5/$FINAL_CHUNK_LEN/g")
SQL=$(echo "$SQL" | sed "s/%6/$FINAL_CHUNK/g")
echo "$SQL"
