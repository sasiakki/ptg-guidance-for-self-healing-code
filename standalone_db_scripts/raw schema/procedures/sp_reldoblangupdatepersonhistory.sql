-- PROCEDURE: raw.sp_reldoblangupdatepersonhistory()

-- DROP PROCEDURE IF EXISTS "raw".sp_reldoblangupdatepersonhistory();

CREATE OR REPLACE PROCEDURE "raw".sp_reldoblangupdatepersonhistory(
	)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN

--dob
UPDATE staging.personhistory ps
   SET dob = CASE
               WHEN t.dob IS NOT NULL AND raw.validatedob (TO_DATE(t.dob,'mm-dd-yyyy')) = 1 THEN TO_DATE(t.dob,'mm-dd-yyyy')::TEXT
               ELSE NULL
             END 
,
       recordmodifieddate = (CURRENT_TIMESTAMP AT TIME zone 'UTC')
FROM raw.reldoblang t
WHERE ps.dshsid = t.provider_id AND UPPER(ps.sourcekey) LIKE '%DSHS%'
AND   ps.filemodifieddate = (SELECT MAX(t2.filemodifieddate)
                             FROM staging.personhistory t2
                             WHERE UPPER(t2.sourcekey) LIKE '%DSHS%');

                           
--preferred_language
WITH languagecte1 AS
(
  SELECT DISTINCT 
         provider_id,
         preferred_language,
         value
 FROM raw.reldoblang reld
    JOIN raw.languages mast
      ON UPPER (reld.preferred_language) = UPPER (mast.code)
)

UPDATE staging.personhistory ps
   SET preferred_language = CASE
                              WHEN t.preferred_language IS NOT NULL THEN t.value
                              ELSE NULL
                            END,
                            recordmodifieddate = ( current_timestamp AT TIME zone 'UTC' ) 
FROM languagecte1 t
WHERE ps.dshsid = t.provider_id
AND UPPER(ps.sourcekey) LIKE '%DSHS%'
AND   ps.filemodifieddate = (SELECT MAX(t2.filemodifieddate)
                             FROM staging.personhistory t2
                             WHERE UPPER(t2.sourcekey) LIKE '%DSHS%');

--last_background_check_date
UPDATE staging.personhistory ps
   SET last_background_check_date = CASE
                                      WHEN t.last_background_check_date IS NOT NULL AND length(t.last_background_check_date) > 1 THEN TO_DATE(t.last_background_check_date,'mm-dd-yyyy')
                                      ELSE NULL
                                    END ,
                                    recordmodifieddate = ( current_timestamp AT TIME zone 'UTC' )
FROM raw.reldoblang t
WHERE ps.dshsid = t.provider_id
AND UPPER(ps.sourcekey) LIKE '%DSHS%'
AND   ps.filemodifieddate = (SELECT MAX(t2.filemodifieddate)
                             FROM staging.personhistory t2
                             WHERE UPPER(t2.sourcekey) LIKE '%DSHS%');

--ip_contract_expiration_date
UPDATE staging.personhistory ps
   SET ip_contract_expiration_date = CASE
                                      WHEN t.ip_contract_expiration_date IS NOT NULL  AND length(t.ip_contract_expiration_date) > 1THEN TO_DATE(t.ip_contract_expiration_date,'mm-dd-yyyy')
                                      ELSE NULL
                                    END ,
                                    recordmodifieddate = ( current_timestamp AT TIME zone 'UTC' )
FROM raw.reldoblang t
WHERE ps.dshsid = t.provider_id AND
 UPPER(ps.sourcekey) LIKE '%DSHS%'
AND   ps.filemodifieddate = (SELECT MAX(t2.filemodifieddate)
                           FROM staging.personhistory t2
                           WHERE UPPER(t2.sourcekey) LIKE '%DSHS%');

END;
$BODY$;

