-- PROCEDURE: raw.sp_dohtables_cleandata()

-- DROP PROCEDURE IF EXISTS "raw".sp_dohtables_cleandata();

CREATE OR REPLACE PROCEDURE "raw".sp_dohtables_cleandata(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN
DELETE FROM raw.dohclassified
where  credentialnumber is NULL  OR credentialstatus is NULL OR applicationdate is NULL OR filelastname= 'HMCC - DSHS Benefit Classified File' OR filelastname= 'File Last Name';
DELETE FROM raw.dohcompleted
where dohname is NULL OR credentialnumber is NULL OR filelastname= 'HMCC – DSHS Benefit Training Completed File' OR filelastname= 'File Last Name';
END;
$BODY$;
