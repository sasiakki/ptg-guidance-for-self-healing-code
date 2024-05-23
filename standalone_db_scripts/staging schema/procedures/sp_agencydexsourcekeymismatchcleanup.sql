-- PROCEDURE: staging.sp_agencydexsourcekeymismatchcleanup()

-- DROP PROCEDURE IF EXISTS staging.sp_agencydexsourcekeymismatchcleanup();

CREATE OR REPLACE PROCEDURE staging.sp_agencydexsourcekeymismatchcleanup(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN

---For agency caregivers, the migrated sourcekey from DEX will not match with the sourceky generated in DS for the same person (firstname,lastname,dob,ssn) coming from same source
---In this cleanup script we are identifying those mismatched sourcekeys and removing them from DS to avoid having duplicate relationship records  

WITH cte AS
(
  SELECT DISTINCT personid,
         sourcekey,
         SUBSTRING(MD5(concat (LPAD(RIGHT (ssn::TEXT,4),4,'0'::TEXT),dob)),0,10) AS dexsourcekey
  FROM staging.personhistory
  WHERE sourcekey NOT LIKE '%DSHS%'
  AND   sourcekey NOT LIKE '%CDWA%'
  AND   sourcekey NOT LIKE '%CRED%'
  AND   sourcekey NOT LIKE '%SFLegacy%'
),
cte1 AS
(
  SELECT personid,
         source,
         SPLIT_PART(source,'-',2) AS src
  FROM prod.employmentrelationship
),
cte2 AS
(
  SELECT DISTINCT p.*
  FROM cte1 p
    JOIN cte c
      ON p.personid = c.personid
     AND c.dexsourcekey = p.src
)

DELETE
FROM prod.employmentrelationship
WHERE personid IN (SELECT personid FROM cte2)
AND   source IN (SELECT source FROM cte2);

END;
$BODY$;
