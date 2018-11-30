-- get latest 'OPEN' or 'CLOSE' event for a given store
SELECT STRING_VALUE, RTL_LOC_ID, TIME_STAMP
FROM loc_state_journal 
WHERE STATUS_TYPCODE = 'RTL_LOC_STATE'
AND RTL_LOC_ID = '800' 
AND ORGANIZATION_ID = '1'
AND TIME_STAMP = (
	SELECT MAX(TIME_STAMP)
	FROM loc_state_journal 
	WHERE STATUS_TYPCODE = 'RTL_LOC_STATE'
	AND RTL_LOC_ID = '800' 
	AND ORGANIZATION_ID = '1'
);

-- get latest OPEN or CLOSED event for each register for a given organization and store
SELECT WKSTN_ID, STRING_VALUE, max(TIME_STAMP) timeof
FROM LOC_STATE_JOURNAL
WHERE STATUS_TYPCODE = 'WKSTN_STATE'
AND RTL_LOC_ID = '800'
AND ORGANIZATION_ID = '1'
GROUP BY WKSTN_ID, STRING_VALUE
ORDER BY timeof DESC
