-- PROCEDURE: staging.sp_personcredentialupdate()

-- DROP PROCEDURE IF EXISTS staging.sp_personcredentialupdate();

CREATE OR REPLACE PROCEDURE staging.sp_personcredentialupdate(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN

WITH cteupdate AS
(
  SELECT DISTINCT bc.credentialnumber,
         p.personid
  FROM staging.personhistory p
    JOIN raw.credential_delta bc
      ON p.credentialnumber = bc.credentialnumber
     AND bc.primarycredential = 1
     AND p.personid IS NOT NULL
)

 
UPDATE prod.person p
   SET credentialnumber = c.credentialnumber,
		recordmodifieddate = CURRENT_TIMESTAMP
FROM cteupdate c
WHERE c.personid = p.personid
AND   (p.credentialnumber IS NULL OR c.credentialnumber <> p.credentialnumber);


END;
$BODY$;

