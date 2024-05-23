-- PROCEDURE: staging.sp_temp_cleanssn()

-- DROP PROCEDURE IF EXISTS staging.sp_temp_cleanssn();

CREATE OR REPLACE PROCEDURE staging.sp_temp_cleanssn(
	)
LANGUAGE 'plpgsql'
AS $BODY$
 BEGIN 

WITH cte
AS
(SELECT sourcekey,
       LPAD(RIGHT (ssn::TEXT,9),9,'0') AS ssnnew
FROM staging.personhistory
WHERE ssn IS NOT NULL)

UPDATE staging.personhistory p SET ssn = cte.ssnnew FROM cte WHERE p.sourcekey = cte.sourcekey;

WITH cte1
AS
(SELECT sourcekey,
       RIGHT (ssn,4) AS ssnnew1
FROM staging.personhistory
WHERE ssn IS NOT NULL) 

UPDATE staging.personhistory p SET ssn = cte1.ssnnew1 FROM cte1 WHERE p.sourcekey = cte1.sourcekey;

END;

$BODY$;

