-- PROCEDURE: staging.sp_clean_quarantinetable()

-- DROP PROCEDURE IF EXISTS staging.sp_clean_quarantinetable();

CREATE OR REPLACE PROCEDURE staging.sp_clean_quarantinetable(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN 

DROP TABLE IF EXISTS temp_prod_sourcekey;

CREATE TEMPORARY TABLE IF NOT EXISTS temp_prod_sourcekey 
(
  personid           BIGINT,
  sourcekey          VARCHAR(50),
  person_unique_id   BIGINT
);


--Checking if the matched_sourcekeys from staging.personquarantine already exists in prod.person matched_sourcekeys
WITH cte AS
(
  SELECT person_unique_id,
         matched_sourcekeys,
         UNNEST(STRING_TO_ARRAY(matched_sourcekeys,';','')) AS sourcekey
  FROM staging.personquarantine
),
cte1 AS
(
  SELECT personid,
         matched_sourcekeys,
         UNNEST(STRING_TO_ARRAY(matched_sourcekeys,';','')) AS sourcekey
  FROM prod.person p
  ORDER BY personid
),
cte2 AS
(
  SELECT c2.person_unique_id,
         c1.personid,
         c1.sourcekey
  FROM cte1 c1
    JOIN cte c2 ON c1.sourcekey = c2.sourcekey
)

--Inserting the records into a temp table

INSERT INTO temp_prod_sourcekey
(
  personid,
  sourcekey,
  person_unique_id
)
SELECT personid,
       sourcekey,
       person_unique_id
FROM cte2;

 
--Updating the personid into staging.personhistory for those sourcekeys that are found in staging.personquarantine and prod.person
UPDATE staging.personhistory p
   SET personid = c.personid
FROM temp_prod_sourcekey AS c
WHERE p.sourcekey = c.sourcekey
AND   p.personid IS NULL;


----Updating the personid into staging.employmentrelationshiphistory for those sourcekeys that are found in staging.personquarantine and prod.person
UPDATE staging.employmentrelationshiphistory p
   SET personid = c.personid
FROM temp_prod_sourcekey AS c
WHERE p.source = c.sourcekey
AND   p.personid IS NULL;

----Updating the personid into prod.employmentrelationship for those sourcekeys that are found in staging.personquarantine and prod.person
UPDATE prod.employmentrelationship p
   SET personid = c.personid
FROM temp_prod_sourcekey AS c
WHERE p.source = c.sourcekey
AND   p.personid IS NULL;


--Deleting the sourcekeys from staging.personquarantine which are already found in matched_sourcekeys in prod.person
DELETE
FROM staging.personquarantine
WHERE person_unique_id IN (SELECT person_unique_id FROM temp_prod_sourcekey);



--Deleting the sourcekeys from staging.employmentrelationshipquarantine which are already found in matched_sourcekeys in prod.person
-- DELETE
-- FROM staging.employmentrelationshipquarantine
-- WHERE source IN (SELECT sourcekey FROM temp_prod_sourcekey);

--Drop temp table
DROP TABLE IF EXISTS temp_prod_sourcekey;


END;
$BODY$;

