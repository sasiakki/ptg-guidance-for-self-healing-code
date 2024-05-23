-- PROCEDURE: staging.sp_cleaningquarantineagencyterm()

-- DROP PROCEDURE staging.sp_cleaningquarantineagencyterm();

CREATE OR REPLACE PROCEDURE staging.sp_cleaningquarantineagencyterm(
	)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE 
delta_timestamp_from TIMESTAMP WITH TIME ZONE;
delta_timestamp_to TIMESTAMP WITh TIME ZONE;

BEGIN

--Get the previous execution timestamp, to deduct the delta

SELECT MAX(lastprocesseddate) INTO delta_timestamp_from FROM logs.lastprocessed WHERE processname = 'proc-cleaningquarantineagencyterm' AND success = '1';
SELECT CURRENT_TIMESTAMP INTO delta_timestamp_to;

/*
	RAISE NOTICE 'delta_timestamp_from from logs table %', delta_timestamp_from;
	RAISE NOTICE 'delta_timestamp_to from fn_gethistory table %', delta_timestamp_to;

*/

--1-Filter record in quarantine where status='Terminated' and agencyid  in pro.person 
DROP TABLE IF EXISTS tempctetermagency;
CREATE TEMP TABLE tempctetermagency  AS

WITH quaperson AS
(
  SELECT UNNEST(STRING_TO_ARRAY(matched_sourcekeys,';')) AS sourcekey,
         person_unique_id
  FROM staging.personquarantine
),
cte AS
(
  SELECT person_unique_id,
         q.sourcekey,
         p.agencyid
  FROM quaperson q
    JOIN staging.personhistory p ON p.sourcekey = q.sourcekey
  WHERE p.agencyid IS NOT NULL
  AND   p.status = 'Terminated'
  AND p.recordmodifieddate > delta_timestamp_from AND p.recordmodifieddate <= delta_timestamp_to
)
SELECT DISTINCT *
FROM cte
WHERE agencyid IN (SELECT personid FROM prod.person );

--2-Update the staging.personhistory personid for those sourcekey with their agencyids

  UPDATE staging.personhistory q
   SET personid = c.agencyid,
	recordmodifieddate = delta_timestamp_to
FROM tempctetermagency c
WHERE c.sourcekey = q.sourcekey
AND   personid IS NULL; 

 UPDATE staging.employmentrelationshiphistory q
   SET personid = c.agencyid,
   recordmodifieddate = delta_timestamp_to
FROM tempctetermagency c
WHERE c.sourcekey = q.source
AND   personid IS NULL;

 UPDATE prod.employmentrelationship q
   SET personid = c.agencyid,
   recordmodifieddate = delta_timestamp_to
FROM tempctetermagency c
WHERE c.sourcekey = q.source
AND   personid IS NULL;

--3-Update prod.person matched_sourcekeys with sourcekeys of those agencyids 

  UPDATE prod.person p
   SET matched_sourcekeys = concat(p.matched_sourcekeys,c.sourcekey,';'),
   recordmodifieddate = delta_timestamp_to
FROM tempctetermagency c
WHERE p.personid = c.agencyid
AND COALESCE(matched_sourcekeys,'') <> COALESCE(CONCAT(p.matched_sourcekeys,c.sourcekey,';'));

--4- Remove those sourcekeys from staging.personquarantine

DELETE
FROM staging.personquarantine
WHERE person_unique_id IN (SELECT person_unique_id FROM tempctetermagency);

INSERT INTO logs.lastprocessed(processname, lastprocesseddate, success)
VALUES ('proc-cleaningquarantineagencyterm',delta_timestamp_to, '1');

END;
$BODY$;
