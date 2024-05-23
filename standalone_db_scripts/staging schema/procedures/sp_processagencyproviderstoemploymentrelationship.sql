-- PROCEDURE: staging.sp_processagencyproviderstoemploymentrelationship()

-- DROP PROCEDURE IF EXISTS staging.sp_processagencyproviderstoemploymentrelationship();

CREATE OR REPLACE PROCEDURE staging.sp_processagencyproviderstoemploymentrelationship()
LANGUAGE 'plpgsql'
AS $BODY$

DECLARE
  rec_provider record;
  cur_providers CURSOR
  FOR
    SELECT *
    FROM staging.vw_getagencyclassification;

BEGIN
  -- open the cursor
  open cur_providers;

  LOOP
  -- fetch row into the provider record
  FETCH cur_providers INTO rec_provider;

  -- exit when no more row to fetch
  EXIT WHEN NOT found;
            RAISE NOTICE '********Begin execution***********';
            --Step 1 logic for termination of employmentrelationship records
            IF (rec_provider.empstatus = 'Terminated' AND rec_provider.terminationdate IS NOT NULL AND rec_provider.agencyid IS NOT NULL) THEN

                RAISE NOTICE 'empstatus = Terminated and rec_provider.terminationdate IS NOT NULL';
                           -- Step 1.1 Logic to verify active employmentrelationship record exists
                           IF EXISTS(SELECT 1
                                      FROM prod.employmentrelationship
                                      WHERE personid =  rec_provider.agencyid              --personid = rec_provider.personid
                                      AND   employerid = rec_provider.employerid
                                      AND   empstatus <> 'Terminated' AND createdby <> 'ZenithLegacy') THEN 

                                      RAISE NOTICE 'Matching record exists in prod.employmentrelationship table';
                                      RAISE NOTICE 'empstatus is Terminated, Update AuthEnd for source id %',rec_provider.source;

                                      RAISE NOTICE 'Update AuthEnd: %, EmpStatus: % in prod.employmentrelationship table',rec_provider.terminationdate,rec_provider.empstatus;
                                      -- Update AuthEnd in prod.employmentrelationship table
                                     UPDATE prod.employmentrelationship
                                     SET authend = rec_provider.terminationdate,
                                         terminationdate = rec_provider.terminationdate,
                                         recordmodifieddate = (current_timestamp at time zone 'PST'),
                                         empStatus = rec_provider.empstatus,
                                         filedate = rec_provider.filedate
                                     WHERE personid =  rec_provider.agencyid   --personid = rec_provider.personid
                                     AND   employerid = rec_provider.employerid;

                                     RAISE NOTICE 'Update EmpStatus = Terminated in bg.personsource table';
        

                                      RAISE NOTICE 'Insert into logs.servicelinelog table';
                                      -- Insert into logs.servicelinelog table
                                     -- insert into logs.employmentrelationshiphistorylog table                        
                                                                              INSERT INTO logs.employmentrelationshiphistorylog
                                                                              (
                                                                                relationshipid,
                                                                                personid,
                                                                                employeeid,
                                                                                branchid,
                                                                                workercategory,
                                                                                categorycode,
                                                                                hiredate,
                                                                                empstatus,
                                                                                trackingdate,
                                                                                modified,
                                                                                role, 
                                                                                isoverride, 
                                                                                isignored, 
                                                                                employerid,
                                                                                authstart,
                                                                                authend,
                                                                                terminationdate,
                                                                                sourcekey,
                                                                                filedate,
                                                                                createdby
                                                                              )
                                                                              SELECT relationshipid,
                                                                                      personid,
                                                                                      employeeid,
                                                                                      branchid::text,
                                                                                      workercategory,
                                                                                      categorycode,
                                                                                      hiredate::text,
                                                                                      empstatus,
                                                                                      trackingdate,
                                                                                      recordmodifieddate,
                                                                                      role,
                                                                                      isoverride::text,
                                                                                      isignored::text,
                                                                                      employerid,
                                                                                      authstart,
                                                                                      authend,
                                                                                      terminationdate,
                                                                                      source,
                                                                                      filedate::text,
                                                                                      createdby
                                                                                from prod.employmentrelationship
                                                                               WHERE personid =  rec_provider.agencyid
                                                                              AND  employerid = rec_provider.employerid
                                                                                ORDER BY relationshipid DESC LIMIT 1;
                           --Step 1.2 No record exists
                           ELSE
                                   RAISE NOTICE '!!!Validation error. No record exists or record already terminated in prod.employmentrelationship table!!!!';
                                   INSERT INTO logs.workercategoryerrors( sourcekey, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                          (
                                                                                                                                            rec_provider.source,
                                                                                                                                            'QUALTRICS_AGENCY',
                                                                                                                                            rec_provider.filedate,
                                                                                                                                            rec_provider.workercategory,
                                                                                                                                            rec_provider.categorycode,
                                                                                                                                            'Validation error. No record exists or record already terminated in prod.employmentrelationship table'
                                                                                                                                          );
                           END IF; --End if Step 1.1
          --Step 2: logic for new  employmentrelationship active record 
         ELSEIF (rec_provider.empstatus <> 'Terminated' AND rec_provider.hiredate IS NOT NULL ) THEN

                            RAISE NOTICE 'empstatus = Active and rec_provider.hiredate IS NOT NULL and rec_provider.trackingdate IS NOT NULL';
                            RAISE NOTICE 'Personid id: %,empstatus: % and Classificationcode: % and hiredate: %  trackingdate: %',rec_provider.personid,rec_provider.empstatus,
                            rec_provider.categorycode,rec_provider.hiredate,rec_provider.trackingdate;
                                              
                                          -- Insert a new employmentrelationship record
                                         IF NOT EXISTS(SELECT 1
                                                    FROM prod.employmentrelationship
                                                    WHERE (source =  rec_provider.source
                                                    AND   employerid = rec_provider.employerid
                                                    AND   empstatus <> 'Terminated'))then

                                                   RAISE NOTICE 'Insert into prod.employmentrelationship table';
                                                   -- insert into prod.employmentrelationship table
                                                          INSERT INTO prod.employmentrelationship
                                                          (
                                                             workercategory,
                                                             categorycode,
                                                             role,
                                                             source,
                                                             priority,
                                                             createdby,
                                                             filedate,
                                                             relationship,
                                                             branchid,
                                                             hiredate,
                                                             authstart,
                                                             authend,
                                                             terminationdate,
                                                             empstatus,
                                                             trackingdate,
                                                             employerid,
                                                             agencyid
                                                          )
                                                          VALUES
                                                          (
                                                            rec_provider.workercategory,
                                                            rec_provider.categorycode,
                                                             rec_provider.role,
                                                             rec_provider.source,
                                                             rec_provider.priority,
                                                             rec_provider.createdby,
                                                             rec_provider.filedate,
                                                             rec_provider.relationship,
                                                             rec_provider.branchid,
                                                             rec_provider.hiredate,
                                                             rec_provider.authstart,
                                                             rec_provider.authend,
                                                             rec_provider.terminationdate,
                                                             rec_provider.empstatus,
                                                             rec_provider.trackingdate,
                                                             rec_provider.employerid,
                                                             rec_provider.agencyid
                                                          );

                                                          RAISE NOTICE 'Insert into logs.employmentrelationshiphistorylog table';
                                                          -- insert into logs.employmentrelationshiphistorylog table
                                                          INSERT INTO logs.employmentrelationshiphistorylog
                                                                              (
                                                                                relationshipid,
                                                                                personid,
                                                                                employeeid,
                                                                                branchid,
                                                                                workercategory,
                                                                                categorycode,
                                                                                hiredate,
                                                                                empstatus,
                                                                                trackingdate,
                                                                                modified,
                                                                                role, 
                                                                                isoverride, 
                                                                                isignored, 
                                                                                employerid,
                                                                                authstart,
                                                                                authend,
                                                                                terminationdate,
                                                                                sourcekey,
                                                                                filedate,
                                                                                createdby
                                                                              )
                                                                              SELECT relationshipid,
                                                                                      personid,
                                                                                      employeeid,
                                                                                      branchid::text,
                                                                                      workercategory,
                                                                                      categorycode,
                                                                                      hiredate::text,
                                                                                      empstatus,
                                                                                      trackingdate,
                                                                                      recordmodifieddate,
                                                                                      role,
                                                                                      isOverride::text,
                                                                                      isignored::text,
                                                                                      employerid,
                                                                                      authstart,
                                                                                      authend,
                                                                                      terminationdate,
                                                                                      source,
                                                                                      filedate::text,
                                                                                      createdby
                                                                                from prod.employmentrelationship
                                                                               WHERE source =  rec_provider.source
                                                                              AND  employerid = rec_provider.employerid
                                                                                ORDER BY relationshipid DESC LIMIT 1;
                                                  ELSE
                                                        RAISE NOTICE 'Employment relationship record already exists';
                                                        

                                                  INSERT INTO logs.workercategoryerrors( sourcekey, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                          (
                                                                                                                                            rec_provider.source,
                                                                                                                                            'QUALTRICS_AGENCY',
                                                                                                                                            rec_provider.filedate,
                                                                                                                                            rec_provider.workercategory,
                                                                                                                                            rec_provider.categorycode,
                                                                                                                                            'Employment relationship record already exits in prod.employmentrelationship table'
                                                                                                                                          );

                                                  END IF;

                                           
          --Step 3: No changes in classification
          ELSE
                 RAISE NOTICE '!!!!!!Sourcekey: % no changes in Classification or Classification data is invalid !!!!!!!',rec_provider.source;
                  INSERT INTO logs.workercategoryerrors( sourcekey, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                          (
                                                                                                                                            rec_provider.source,
                                                                                                                                            'QUALTRICS_AGENCY',
                                                                                                                                            rec_provider.filedate,
                                                                                                                                            rec_provider.workercategory,
                                                                                                                                            rec_provider.categorycode,
                                                                                                                                            'No change in Classification or Classification data is invalid'
                                                                                                                                          );
          END IF;


RAISE NOTICE '********End execution***********';

END LOOP;

-- close the cursor
CLOSE cur_providers;

--Insert an entry into the logs table
WITH cte AS
(
  SELECT 'glue-ap-to-employmentrelationship' AS processname,
         MAX(filedate) as filedate,
         '1' AS success
  FROM staging.employmentrelationshiphistory
  WHERE UPPER(source::TEXT) !~~ '%DSHS%'::TEXT
  AND   UPPER(source::TEXT) !~~ '%DOH%'::TEXT
  AND   UPPER(source::TEXT) !~~ '%CDWA%'::TEXT
  AND   UPPER(source::TEXT) !~~ '%SFLegacy%'::TEXT
  AND   UPPER(source::TEXT) !~~ '%PORTAL%'::TEXT
),
ctefinal AS
(
  SELECT *
  FROM cte c
  WHERE c.filedate NOT IN (SELECT lastprocesseddate
                         FROM logs.lastprocessed
                         WHERE processname = 'glue-ap-to-employmentrelationship'
                         AND   success = '1')
)
INSERT INTO logs.lastprocessed
(
  processname,
  lastprocesseddate,
  success
)
SELECT *
FROM ctefinal;



--COMMIT;

END;
$BODY$;
