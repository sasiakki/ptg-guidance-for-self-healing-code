-- FUNCTION: raw.validatedob(date)

-- DROP FUNCTION IF EXISTS "raw".validatedob(date);

CREATE OR REPLACE FUNCTION "raw".validatedob(
	birthdate date)
    RETURNS integer
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$

BEGIN
 IF EXTRACT(year FROM birthdate) BETWEEN 1900 AND 2100 AND 
    EXTRACT(month FROM birthdate) BETWEEN 01 AND 12 AND 
    EXTRACT(day FROM birthdate) BETWEEN 01 AND 31 AND 
    (EXTRACT(year FROM CURRENT_DATE) -EXTRACT(year FROM birthdate)) >= 18 AND 
    (EXTRACT(year FROM CURRENT_DATE) -EXTRACT(year FROM birthdate)) <= 80 AND 
    (EXTRACT(year FROM birthdate) <> 1900 OR EXTRACT(year FROM birthdate) <> 1901) AND birthdate <> '01/01/2000' THEN RETURN 1;
ELSE RETURN 0;
END IF;

END;
$BODY$;

