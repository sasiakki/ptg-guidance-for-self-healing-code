-- PROCEDURE: staging.sp_updatecarinaeligibility()

-- DROP PROCEDURE staging.sp_updatecarinaeligibility();

CREATE OR REPLACE PROCEDURE staging.sp_updatecarinaeligibility(
	)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE 

	delta_timestamp_from TIMESTAMP WITH TIME ZONE;
	delta_timestamp_to TIMESTAMP WITH TIME ZONE;
	
BEGIN

--Get the previous execution timestamp, to deduct the delta
SELECT MAX(lastprocesseddate) INTO delta_timestamp_from FROM logs.lastprocessed WHERE processname = 'proc-carina-processing' AND success = '1';
SELECT CURRENT_TIMESTAMP INTO delta_timestamp_to;

--Get all CDWA providers carinaeligible status
WITH cte_phc AS
(
 SELECT CASE
         WHEN l.iscarinaeligible THEN TRUE
         WHEN l.ie_date IS NOT NULL THEN TRUE
         ELSE FALSE
       END AS iscarinaeligible,
       l.personid
FROM (SELECT ph.personid,
             ph.iscarinaeligible,
             ph.ie_date,
             ph.cdwa_id,
             ROW_NUMBER() OVER (PARTITION BY ph.cdwa_id ORDER BY ph.recordmodifieddate DESC) AS rn
      FROM staging.personhistory ph
      WHERE ph.sourcekey LIKE '%CDWA%'
			AND   ph.personid IS NOT NULL
			AND ( ph.recordmodifieddate > delta_timestamp_from AND  ph.recordmodifieddate <= delta_timestamp_to ) ) l
WHERE l.rn = 1
)

--select * from cte_phc;	
	--Update carinaeligible status in bg.person table for CDWA Providers
  UPDATE prod.person p
   SET iscarinaeligible = cte.iscarinaeligible,
      recordmodifieddate = delta_timestamp_to
  FROM cte_phc cte
  WHERE p.personid = cte.personid
  and p.iscarinaeligible <> cte.iscarinaeligible;

--- carina eligibility logic end--------

INSERT INTO logs.lastprocessed(processname, lastprocesseddate, success)
VALUES ('proc-carina-processing',delta_timestamp_to, '1');

END;
$BODY$;
