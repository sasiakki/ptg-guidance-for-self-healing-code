-- PROCEDURE: staging.sp_icd12termupdate2()

-- DROP PROCEDURE IF EXISTS staging.sp_icd12termupdate2();

CREATE OR REPLACE PROCEDURE staging.sp_icd12termupdate2(
	)
LANGUAGE 'plpgsql'
AS $BODY$

BEGIN

DROP TABLE if exists temp_finalcte_2;

CREATE TEMPORARY TABLE temp_finalcte_2 (filemodifieddate timestamp,employeeid bigint,branchid int,source varchar,categorycode varchar);


WITH rawicd12cte AS
(
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY employeeno ORDER BY filemodifieddate DESC) rn
  FROM raw.icd12
  ORDER BY employeeno
),
cte AS
(
  SELECT pf.employeeno,
         pf.filemodifieddate,
         CASE
           WHEN CAST(pf.ru1 AS CHARACTER VARYING) ~ '^[0\.]+$' <> TRUE THEN (SELECT DISTINCT branchid
                                                                             FROM prod.branch
                                                                             WHERE LTRIM(branchcode,'0') = LTRIM(CAST(pf.ru1 AS CHARACTER VARYING),'0'))
           WHEN CAST(pf.ru1 AS CHARACTER VARYING) ~ '^[0\.]+$' = TRUE THEN (SELECT DISTINCT branchid
                                                                            FROM prod.branch
                                                                            WHERE branchcode = '0000')
           ELSE NULL
         END AS branch1
  FROM rawicd12cte pf
    INNER JOIN (SELECT MAX(filemodifieddate) mxdate,
                       employeeno
                FROM rawicd12cte
                GROUP BY employeeno) t2
            ON pf.employeeno = t2.employeeno
           AND pf.filemodifieddate = t2.mxdate
  UNION ALL
  SELECT pf.employeeno,
         pf.filemodifieddate,
         CASE
           WHEN CAST(pf.ru2 AS CHARACTER VARYING) ~ '^[0\.]+$' <> TRUE THEN (SELECT DISTINCT branchid
                                                                             FROM prod.branch
                                                                             WHERE LTRIM(branchcode,'0') = LTRIM(CAST(pf.ru2 AS CHARACTER VARYING),'0'))
           WHEN CAST(pf.ru2 AS CHARACTER VARYING) ~ '^[0\.]+$' = TRUE THEN (SELECT DISTINCT branchid
                                                                            FROM prod.branch
                                                                            WHERE branchcode = '0000')
           ELSE NULL
         END AS branch1
  FROM rawicd12cte pf
    INNER JOIN (SELECT MAX(filemodifieddate) mxdate,
                       employeeno
                FROM rawicd12cte
                GROUP BY employeeno) t2
            ON pf.employeeno = t2.employeeno
           AND pf.filemodifieddate = t2.mxdate
  UNION ALL
  SELECT pf.employeeno,
         pf.filemodifieddate,
         CASE
           WHEN CAST(pf.ru3 AS CHARACTER VARYING) ~ '^[0\.]+$' <> TRUE THEN (SELECT DISTINCT branchid
                                                                             FROM prod.branch
                                                                             WHERE LTRIM(branchcode,'0') = LTRIM(CAST(pf.ru3 AS CHARACTER VARYING),'0'))
           WHEN CAST(pf.ru3 AS CHARACTER VARYING) ~ '^[0\.]+$' = TRUE THEN (SELECT DISTINCT branchid
                                                                            FROM prod.branch
                                                                            WHERE branchcode = '0000')
           ELSE NULL
         END AS branch1
  FROM rawicd12cte pf
    INNER JOIN (SELECT MAX(filemodifieddate) mxdate,
                       employeeno
                FROM rawicd12cte
                GROUP BY employeeno) t2
            ON pf.employeeno = t2.employeeno
           AND pf.filemodifieddate = t2.mxdate
  UNION ALL
  SELECT pf.employeeno,
         pf.filemodifieddate,
         CASE
           WHEN CAST(pf.ru4 AS CHARACTER VARYING) ~ '^[0\.]+$' <> TRUE THEN (SELECT DISTINCT branchid
                                                                             FROM prod.branch
                                                                             WHERE LTRIM(branchcode,'0') = LTRIM(CAST(pf.ru4 AS CHARACTER VARYING),'0'))
           WHEN CAST(pf.ru4 AS CHARACTER VARYING) ~ '^[0\.]+$' = TRUE THEN (SELECT DISTINCT branchid
                                                                            FROM prod.branch
                                                                            WHERE branchcode = '0000')
           ELSE NULL
         END AS branch1
  FROM rawicd12cte pf
    INNER JOIN (SELECT MAX(filemodifieddate) mxdate,
                       employeeno
                FROM rawicd12cte
                GROUP BY employeeno) t2
            ON pf.employeeno = t2.employeeno
           AND pf.filemodifieddate = t2.mxdate
),
cte2 AS
(
  SELECT pf.employeeno,
         pf.filemodifieddate,
         CASE
           WHEN CAST(pf.ru1 AS CHARACTER VARYING) ~ '^[0\.]+$' <> TRUE THEN (SELECT DISTINCT branchid
                                                                             FROM prod.branch
                                                                             WHERE LTRIM(branchcode,'0') = LTRIM(CAST(pf.ru1 AS CHARACTER VARYING),'0'))
           WHEN CAST(pf.ru1 AS CHARACTER VARYING) ~ '^[0\.]+$' = TRUE THEN (SELECT DISTINCT branchid
                                                                            FROM prod.branch
                                                                            WHERE branchcode = '0000')
           ELSE NULL
         END AS branch2
  FROM rawicd12cte pf
    INNER JOIN (SELECT MAX(filemodifieddate) mxdate,
                       employeeno
                FROM rawicd12cte
                WHERE rn = 2
                GROUP BY employeeno) t2
            ON pf.employeeno = t2.employeeno
           AND pf.filemodifieddate = t2.mxdate
           AND pf.rn = 2
  UNION ALL
  SELECT pf.employeeno,
         pf.filemodifieddate,
         CASE
           WHEN CAST(pf.ru2 AS CHARACTER VARYING) ~ '^[0\.]+$' <> TRUE THEN (SELECT DISTINCT branchid
                                                                             FROM prod.branch
                                                                             WHERE LTRIM(branchcode,'0') = LTRIM(CAST(pf.ru2 AS CHARACTER VARYING),'0'))
           WHEN CAST(pf.ru2 AS CHARACTER VARYING) ~ '^[0\.]+$' = TRUE THEN (SELECT DISTINCT branchid
                                                                            FROM prod.branch
                                                                            WHERE branchcode = '0000')
           ELSE NULL
         END AS branch2
  FROM rawicd12cte pf
    INNER JOIN (SELECT MAX(filemodifieddate) mxdate,
                       employeeno
                FROM rawicd12cte
                WHERE rn = 2
                GROUP BY employeeno) t2
            ON pf.employeeno = t2.employeeno
           AND pf.filemodifieddate = t2.mxdate
           AND pf.rn = 2
  UNION ALL
  SELECT pf.employeeno,
         pf.filemodifieddate,
         CASE
           WHEN CAST(pf.ru3 AS CHARACTER VARYING) ~ '^[0\.]+$' <> TRUE THEN (SELECT DISTINCT branchid
                                                                             FROM prod.branch
                                                                             WHERE LTRIM(branchcode,'0') = LTRIM(CAST(pf.ru3 AS CHARACTER VARYING),'0'))
           WHEN CAST(pf.ru3 AS CHARACTER VARYING) ~ '^[0\.]+$' = TRUE THEN (SELECT DISTINCT branchid
                                                                            FROM prod.branch
                                                                            WHERE branchcode = '0000')
           ELSE NULL
         END AS branch2
  FROM rawicd12cte pf
    INNER JOIN (SELECT MAX(filemodifieddate) mxdate,
                       employeeno
                FROM rawicd12cte
                WHERE rn = 2
                GROUP BY employeeno) t2
            ON pf.employeeno = t2.employeeno
           AND pf.filemodifieddate = t2.mxdate
           AND pf.rn = 2
  UNION ALL
  SELECT pf.employeeno,
         pf.filemodifieddate,
         CASE
           WHEN CAST(pf.ru4 AS CHARACTER VARYING) ~ '^[0\.]+$' <> TRUE THEN (SELECT DISTINCT branchid
                                                                             FROM prod.branch
                                                                             WHERE LTRIM(branchcode,'0') = LTRIM(CAST(pf.ru4 AS CHARACTER VARYING),'0'))
           WHEN CAST(pf.ru4 AS CHARACTER VARYING) ~ '^[0\.]+$' = TRUE THEN (SELECT DISTINCT branchid
                                                                            FROM prod.branch
                                                                            WHERE branchcode = '0000')
           ELSE NULL
         END AS branch2
  FROM rawicd12cte pf
    INNER JOIN (SELECT MAX(filemodifieddate) mxdate,
                       employeeno
                FROM rawicd12cte
                WHERE rn = 2
                GROUP BY employeeno) t2
            ON pf.employeeno = t2.employeeno
           AND pf.filemodifieddate = t2.mxdate
           AND pf.rn = 2
),
cte3 AS
(
  SELECT cte.employeeno,
         cte.filemodifieddate,
         cte2.branch2 AS ru
  FROM cte
    JOIN cte2
      ON cte.employeeno = cte2.employeeno
     AND branch2 NOT IN (SELECT branch1
                                FROM cte
                                WHERE employeeno = cte2.employeeno
                                AND   branch1 IS NOT NULL)
),
cte5 AS
(
  SELECT cte.employeeno,
         cte.filemodifieddate,
         cte.branch1 AS ru
  FROM cte
  WHERE employeeno IN (SELECT a.employeeno
                       FROM rawicd12cte a
                         JOIN rawicd12cte b
                           ON a.employeeno = b.employeeno
                          AND a.rn = 1
                          AND b.rn = 2
                          AND COALESCE (NULLIF (CAST (a.ru1 AS CHARACTER VARYING),''),'0') = COALESCE (NULLIF (CAST (b.ru1 AS CHARACTER VARYING),''),'0')
                          AND COALESCE (NULLIF (CAST (a.ru2 AS CHARACTER VARYING),''),'0') = COALESCE (NULLIF (CAST (b.ru2 AS CHARACTER VARYING),''),'0')
                          AND COALESCE (NULLIF (CAST (a.ru3 AS CHARACTER VARYING),''),'0') = COALESCE (NULLIF (CAST (b.ru3 AS CHARACTER VARYING),''),'0')
                          AND COALESCE (NULLIF (CAST (a.ru4 AS CHARACTER VARYING),''),'0') = COALESCE (NULLIF (CAST (b.ru4 AS CHARACTER VARYING),''),'0'))
),
cte6 AS
(
  SELECT cte.employeeno,
         cte.filemodifieddate,
         sv.branchid AS ru
  FROM prod.employmentrelationship sv
    JOIN cte
      ON sv.employeeid = cte.employeeno
     AND CAST (sv.branchid AS VARCHAR) NOT IN (SELECT CAST(cte.branch1 AS VARCHAR)
                                                      FROM cte
                                                      WHERE cte.branch1 IS NOT NULL
                                                      AND   sv.employeeid = cte.employeeno)
     AND sv.empstatus = 'Active'
),
resultcte AS
(
  SELECT a.employeeid,
         b.employeeno,
         b.ru,
         b.filemodifieddate
  FROM prod.employmentrelationship a
    LEFT JOIN cte3 b
           ON a.employeeid = b.employeeno
          AND a.empstatus = 'Active'
          AND a.employerid = '103'
          AND b.ru IS NOT NULL
),
resultcte3 AS
(
  SELECT a.employeeid,
         b.employeeno,
         b.ru,
         b.filemodifieddate
  FROM prod.employmentrelationship a
    LEFT JOIN cte6 b
           ON a.employeeid = b.employeeno
          AND a.empstatus = 'Active'
          AND a.employerid = '103'
          AND b.ru IS NOT NULL
),
finalcte AS
(
  SELECT DISTINCT prod.employmentrelationship.employeeid,
         prod.employmentrelationship.branchid,
         resultcte.filemodifieddate,
         prod.employmentrelationship.source,
         prod.employmentrelationship.categorycode          
  FROM resultcte
    JOIN prod.employmentrelationship
      ON prod.employmentrelationship.employeeid = resultcte.employeeid
     AND prod.employmentrelationship.branchid = resultcte.ru
     AND prod.employmentrelationship.empstatus = 'Active'
     AND resultcte.ru IN (SELECT branchid
                                 FROM prod.employmentrelationship
                                 WHERE employeeid = resultcte.employeeid)
     AND resultcte.employeeid IN (SELECT employeeid FROM prod.employmentrelationship WHERE empstatus='Active' GROUP BY employeeid HAVING COUNT(employeeid)>1)
AND resultcte.filemodifieddate IS NOT NULL

UNION
SELECT DISTINCT prod.employmentrelationship.employeeid,
       prod.employmentrelationship.branchid,
       resultcte3.filemodifieddate,
       prod.employmentrelationship.source,
       prod.employmentrelationship.categorycode
FROM resultcte3
  JOIN prod.employmentrelationship
    ON prod.employmentrelationship.employeeid = resultcte3.employeeid
   AND prod.employmentrelationship.branchid = resultcte3.ru
   AND prod.employmentrelationship.empstatus = 'Active'
   AND resultcte3.ru IN (SELECT branchid
                                FROM prod.employmentrelationship
                                WHERE employeeid = resultcte3.employeeid)
   AND resultcte3.filemodifieddate IS NOT NULL
)


INSERT INTO temp_finalcte_2
(
  filemodifieddate,
  employeeid,
  branchid,
  source,
  categorycode
)
SELECT filemodifieddate,
       employeeid,
       branchid,
       source,
       categorycode
FROM finalcte;


UPDATE prod.employmentrelationship
   SET empstatus = 'Terminated',
       authend = temp_finalcte_2.filemodifieddate,
       terminationdate = temp_finalcte_2.filemodifieddate,
      -- modified = CURRENT_TIMESTAMP,
       recordmodifieddate = CURRENT_TIMESTAMP
FROM temp_finalcte_2
WHERE prod.employmentrelationship.employeeid = temp_finalcte_2.employeeid
AND   prod.employmentrelationship.branchid = temp_finalcte_2.branchid
AND   prod.employmentrelationship.empstatus = 'Active'
AND   prod.employmentrelationship.employerid = '103'
AND   prod.employmentrelationship.source = temp_finalcte_2.source;


-- UPDATE staging.personhistory
--    SET status = 'Terminated',
--        modified = CURRENT_TIMESTAMP,
--        recordmodifieddate = CURRENT_TIMESTAMP
-- FROM temp_finalcte_2
-- WHERE temp_finalcte_2.source = staging.personhistory.sourcekey
-- AND   temp_finalcte_2.categorycode = staging.personhistory.categorycode
-- AND   staging.personhistory.status <> 'Terminated';



DROP TABLE temp_finalcte_2;


END;
$BODY$;

