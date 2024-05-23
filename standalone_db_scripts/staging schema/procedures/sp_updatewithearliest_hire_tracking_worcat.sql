-- PROCEDURE: staging.sp_updatewithearliest_hire_tracking_worcat()

-- DROP PROCEDURE staging.sp_updatewithearliest_hire_tracking_worcat();

CREATE OR REPLACE PROCEDURE staging.sp_updatewithearliest_hire_tracking_worcat(
	)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
	--var_max_date timestamptz := NULL::timestamptz; -- lower bound .
	-- NOW() will be upper bound

	delta_timestamp_from TIMESTAMP WITHOUT TIME ZONE;
	delta_timestamp_to TIMESTAMP WITHOUT TIME ZONE;
	
BEGIN
	--select max(recordmodifieddate) into var_max_date from prod.person;
	--Get the previous execution timestamp, to deduce the delta
		SELECT MAX(lastprocesseddate) INTO delta_timestamp_from 
			FROM logs.lastprocessed WHERE processname = 'proc-updateearliest-hire-tracking-workcat' AND success = '1';
		SELECT localtimestamp INTO delta_timestamp_to;

--	var_max_date := (var_max_date-INTERVAL '1 day');

		
--update hiredate
WITH cte_person AS
(
  SELECT hiredate, personid FROM prod.person WHERE recordmodifieddate > delta_timestamp_from AND recordmodifieddate <= delta_timestamp_to
),
cte AS
(
  SELECT personid,
         MIN(hiredate) AS ehd
  FROM prod.employmentrelationship
  WHERE personid IN ( SELECT personid FROM cte_person)
  AND   hiredate IS NOT NULL
  AND   isignored = FALSE
  GROUP BY personid
),
cte_newdata AS
(
  SELECT c1.personid,
         c1.ehd
  FROM cte c1
    JOIN cte_person c2 ON c1.personid = c2.personid
  WHERE (c2.hiredate IS NULL OR c1.ehd <> c2.hiredate)
)

UPDATE prod.person p
   SET hiredate = c.ehd
FROM cte_newdata c
WHERE c.personid = p.personid 
AND ( p.hiredate IS NULL OR c.ehd <> p.hiredate );
				

	
-- update workercategory and categorycode
WITH ctemp AS
(
  SELECT MIN(priority) AS min_priority,
         personid
  FROM prod.employmentrelationship e
  WHERE isignored = FALSE
			AND   personid IS NOT NULL
  GROUP BY personid
),
ctemw AS
(
  SELECT DISTINCT workercategory,
         priority,
         tccode,
         ctemp.personid AS personid
  FROM staging.workercategory w
    JOIN ctemp ON ctemp.min_priority = w.priority
),
cte_person2 AS
(
  SELECT personid, workercategory, categorycode FROM prod.person WHERE recordmodifieddate > delta_timestamp_from  AND recordmodifieddate <= delta_timestamp_to
),
cte_newwcc AS
(
  SELECT c1.personid,
         CASE
           WHEN LOWER(c1.workercategory) = LOWER('orientation & safety') THEN NULL
           ELSE c1.workercategory
         END AS workercategory,
         c1.tccode
  FROM ctemw c1
    JOIN cte_person2 c2 ON c1.personid = c2.personid
  WHERE ((NULLIF(c2.workercategory,'NA') <> NULLIF(c1.workercategory,'NA')) OR (c1.tccode <> c2.categorycode OR c2.categorycode IS NULL)))

    UPDATE prod.person p
       SET recordmodifieddate = delta_timestamp_to,
           workercategory = newwcc.workercategory,
           categorycode = newwcc.tccode
    FROM cte_newwcc newwcc
    WHERE p.personid = newwcc.personid
	AND (
			COALESCE(p.workercategory, '') <> COALESCE(newwcc.workercategory,'')
		OR
			COALESCE(p.categorycode,'') <> COALESCE(newwcc.tccode,'' )
		);
   -- AND   lower(newwcc.workercategory) <> lower('orientation & safety');

		

  -- Update tracking date
  WITH 
    cte_persont AS
  (
    SELECT trackingdate::text, personid FROM prod.person WHERE recordmodifieddate > delta_timestamp_from  AND recordmodifieddate <= delta_timestamp_to
  ),
  ctet AS
  (
    SELECT personid,
           MIN(trackingdate) AS etd,
           workercategory,
           categorycode
    FROM prod.employmentrelationship
    WHERE personid IS NOT NULL AND personid IN (SELECT personid FROM cte_persont ) 
		AND   trackingdate IS NOT NULL
		AND   isignored = FALSE
    GROUP BY personid,workercategory,categorycode
  ),
  cte_newdatat AS
  (
    SELECT c1.personid,
           c1.etd::date,
           c1.workercategory,
           c1.categorycode,
           c2.trackingdate
    FROM ctet c1
      JOIN cte_persont c2 ON c1.personid = c2.personid
    WHERE (c2.trackingdate IS NULL OR c1.etd::date <> c2.trackingdate::date)
  )
  UPDATE prod.person p
     SET recordmodifieddate = delta_timestamp_to,
         trackingdate = c.etd
  FROM cte_newdatat c
  WHERE c.personid = p.personid
   AND  (p.trackingdate IS NULL OR c.etd::date <> p.trackingdate::date);
   
   
-- Lasttermdate and rehiredate for the emergency rehire caregivers  
with rehiredate_erh_cte AS
(
  select personid,cast(min(rehiredate) as date) as rehiredate 
  	from prod.employmentrelationship e 
  where rehiredate is not null 
  and isignored = false
  and empstatus  <> 'Terminated'
  group by personid
),
lasttermdate_erh_cte as (
select personid ,cast(max(terminationdate) as date) as lasttermdate
  from prod.employmentrelationship
  where personid is not null
  and isignored = true
  and empstatus  = 'Terminated'
  and personid in (select personid from rehiredate_erh_cte)
  group by personid
),
erh_person_cte as (
	select a.personid as emp_personid,a.rehiredate, b.lasttermdate 
	from rehiredate_erh_cte a join lasttermdate_erh_cte b on a.personid = b.personid
)--select * from erh_person_cte
UPDATE prod.person p
  SET recordmodifieddate = delta_timestamp_to
  		,lasttermdate = empl.lasttermdate
  		,rehiredate = empl.rehiredate
FROM erh_person_cte empl
WHERE p.personid = empl.emp_personid
AND (
		(p.lasttermdate IS NULL OR p.lasttermdate <> empl.lasttermdate)
		OR
		(p.rehiredate IS NULL OR p.rehiredate <> empl.rehiredate)
	);

-- Lasttermdate for the non-rehire caregivers
WITH rehiredate_erh_cte AS
(
  select personid
  	from prod.employmentrelationship e 
  where rehiredate is not null 
  and isignored = false
  and empstatus  <> 'Terminated'
  group by personid
),lastterm_bis_cte AS
(
  select personid as emp_personid,cast(max(terminationdate) as date) as lasttermdate
  from prod.employmentrelationship
  where personid is not null
  and terminationdate is not null
  and empstatus  = 'Terminated'
  and isignored = false
  and personid not in (select personid from rehiredate_erh_cte)
  group by personid
)
UPDATE prod.person p
  SET recordmodifieddate = delta_timestamp_to,
      lasttermdate = empl.lasttermdate
FROM lastterm_bis_cte empl
WHERE p.personid = empl.emp_personid 
and (p.lasttermdate IS NULL OR p.lasttermdate <> empl.lasttermdate);

						
-- add to learner table (end date in et is missing)
	WITH pendinglearners AS
  	(
    	SELECT p.personid,
       BOOL_OR(CASE WHEN etm.employerid IS NULL THEN FALSE ELSE TRUE END) AS istp
      FROM prod.person p
        JOIN prod.employmentrelationship sl
          ON p.personid = sl.personid  AND UPPER(sl.role) = 'CARE'
        JOIN prod.employertrust etm
          ON etm.employerid::CHARACTER VARYING = sl.employerid AND enddate IS NULL AND UPPER(trust) = 'TP'
        LEFT JOIN staging.learner l ON p.personid = l.personid
      WHERE l.personid IS NULL 
			AND l.recordmodifieddate > delta_timestamp_from 
				AND l.recordmodifieddate <= delta_timestamp_to
      GROUP BY p.personid
  	)
  	INSERT INTO staging.learner (personid, created, modified)
		SELECT personid, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP FROM pendinglearners WHERE istp = true;
		
		
-- update status
	WITH cte AS
	(
		SELECT s.personid,
       ARRAY_AGG(DISTINCT s.empstatus),
       CASE
         WHEN 'Active' = ANY (ARRAY_AGG(DISTINCT s.empstatus)) THEN 'Active'
         ELSE 'Terminated'
       END AS final,
       p.status
    FROM prod.employmentrelationship s
      JOIN prod.person p ON s.personid = p.personid
    WHERE upper(s.role) = 'CARE' AND p.recordmodifieddate > delta_timestamp_from  AND p.recordmodifieddate <= delta_timestamp_to
    GROUP BY s.personid,p.status

	)

	UPDATE prod.person p
		SET status = cte.final,
		recordmodifieddate = delta_timestamp_to
		FROM cte
	WHERE cte.personid = p.personid
	AND COALESCE (UPPER(cte.final),'') <> COALESCE ( UPPER(p.status),'');

--Calculate Provider Type (IP,AP,DP)
-- Logic (only applies to active caregivers):
-- Only DSHS -> IP
-- Only CDWA -> IP
-- Only Agency -> AP
-- DSHS and CDWA -> IP
-- DSHS/CDWA and Agency -> DP

WITH ctetype AS
(
 SELECT personid,
       STRING_AGG(DISTINCT(CASE WHEN employerid::TEXT IN ('103','426') THEN 'IP' 
                                WHEN employerid::TEXT IN ('116','121','142','113','125','153','105','120','107','159','101','122','102','112','108','109','177','118','104','106','111','127','110','123','126') 
                                THEN 'AP' END),',') AS providertype
FROM prod.employmentrelationship S
WHERE LOWER(empstatus) = 'active'
	AND s.recordmodifieddate > delta_timestamp_from  AND s.recordmodifieddate <= delta_timestamp_to
GROUP BY personid
), ctetype1 AS
(SELECT personid,
       CASE
         WHEN providertype IN ('AP,IP','IP,AP') THEN 'DP'
         ELSE providertype
       END AS providertypes
FROM ctetype) 

UPDATE prod.person p
   SET TYPE = c.providertypes,
		recordmodifieddate = delta_timestamp_to
FROM ctetype1 c
WHERE c.personid = p.personid
AND   c.providertypes IS NOT NULL
AND   COALESCE (p.TYPE,'') <> COALESCE(c.providertypes,'');

INSERT INTO logs.lastprocessed(processname, lastprocesseddate, success)
VALUES ('proc-updateearliest-hire-tracking-workcat',delta_timestamp_to, '1');

		
END;
$BODY$;
