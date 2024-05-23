-- PROCEDURE: staging.sp_icd12termupdate1()

-- DROP PROCEDURE IF EXISTS staging.sp_icd12termupdate1();

CREATE OR REPLACE PROCEDURE staging.sp_icd12termupdate1(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN

DROP TABLE if exists temp_finalcte;

CREATE TEMPORARY TABLE temp_finalcte (filemodifieddate timestamp,employeeid bigint,empstatus varchar,source varchar);

WITH cte AS
(
  SELECT pf.employeeno,
         pf.filemodifieddate,
         pf.safetyandorientation,
         pf.standardservicegroup,
         pf.adultchildproservforparents,
         pf.parentprovforddchildgroup,
         pf.parprovfornonddchildgroup,
         pf.limithrsgroup,
         pf.respiteprovider,
         pf.authtermflag
  FROM raw.icd12 pf
    INNER JOIN (SELECT MAX(filemodifieddate) mxdate,
                       employeeno
                FROM raw.icd12
                GROUP BY employeeno) t2
            ON pf.employeeno = t2.employeeno
           AND pf.filemodifieddate = t2.mxdate
),
icd12cte
AS
(SELECT pf.*
FROM cte pf
WHERE pf.safetyandorientation = '0'
AND   pf.standardservicegroup = '0'
AND   pf.adultchildproservforparents = '0'
AND   pf.parentprovforddchildgroup = '0'
AND   pf.parprovfornonddchildgroup = '0'
AND   pf.limithrsgroup = '0'
AND   pf.respiteprovider = '0'
AND   pf.authtermflag = '1'
)
,finalcte
AS
(SELECT a.filemodifieddate,
       b.employeeid,
       b.empstatus,
       b.source
FROM icd12cte a
  JOIN prod.employmentrelationship b ON a.employeeno = b.employeeid
WHERE a.authtermflag = '1'
AND   b.empstatus = 'Active'
AND   b.employerid = '103')



INSERT INTO temp_finalcte
(
  filemodifieddate,
  employeeid,
  empstatus,
  source
)
SELECT filemodifieddate,
       employeeid,
       empstatus,
       source
FROM finalcte;




UPDATE prod.employmentrelationship
   SET empstatus = 'Terminated',
       authEnd = CAST(temp_finalcte.filemodifieddate AS TIMESTAMP),
       terminationdate = CAST(temp_finalcte.filemodifieddate AS TIMESTAMP),
      -- modified = CURRENT_TIMESTAMP,
       recordmodifieddate = CURRENT_TIMESTAMP
FROM temp_finalcte
WHERE temp_finalcte.employeeid = prod.employmentrelationship.employeeid
AND   prod.employmentrelationship.employerid = '103'
AND   prod.employmentrelationship.empstatus = 'Active';


-- UPDATE staging.personhistory
--    SET status = 'Terminated',
--        modified = CURRENT_TIMESTAMP,
--        recordmodifieddate = CURRENT_TIMESTAMP
-- FROM temp_finalcte
-- WHERE temp_finalcte.source = staging.personhistory.sourcekey
-- AND   staging.personhistory.status <> 'Terminated';


DROP TABLE temp_finalcte;

END;
$BODY$;

