-- PROCEDURE: staging.sp_cdwaprovidersemploymentrelationshipprocess()

-- DROP PROCEDURE IF EXISTS staging.sp_cdwaprovidersemploymentrelationshipprocess();

CREATE OR REPLACE PROCEDURE staging.sp_cdwaprovidersemploymentrelationshipprocess()
LANGUAGE 'plpgsql'
AS $BODY$

DECLARE 
	rec_provider record;
	var_personid bigint :=-1;
	var_isactiveemploymentrelationship bool     := false;
	var_isterminatedemploymentrelationship bool := false; 
	var_minpriority         integer                     := -1;
	existing_priority_value integer                     := -1;
	cur_providers CURSOR
	FOR
	SELECT *
	FROM
		staging.vw_getproviderInfo ;
BEGIN
  -- open the cursor
  OPEN cur_providers;

  LOOP
  -- fetch row into the provider record
  FETCH cur_providers INTO rec_provider;

  -- exit when no more row to fetch
  EXIT WHEN NOT found;
            RAISE NOTICE '********Begin execution***********';
            RAISE NOTICE '******************************************************************************************';
            --Step 1 logic for termination of serviceline records
			IF (rec_provider.empstatus = 'Terminated' AND rec_provider.termination_date IS NOT NULL) THEN 
                
					RAISE NOTICE 'empstatus = Terminated and rec_provider.terminationdate IS NOT NULL';
                           -- Step 1.1 Logic to verify active Employmentrelationship record exists
                           IF EXISTS(SELECT 1
                                      FROM prod.employmentrelationship
                                      WHERE employeeid = rec_provider.employee_id
                                      AND   employerid = rec_provider.employerid::text
                                      AND   empstatus <> 'Terminated') THEN
                                      
                                      RAISE NOTICE 'Matching record exists in employmentrelationship table';
                                      RAISE NOTICE 'empstatus is Terminated, Update AuthEnd for employee id %',rec_provider.employee_id;
                                      RAISE NOTICE 'Employee id: %,empstatus: % and Classificationcode: %',rec_provider.employee_id,rec_provider.empstatus,rec_provider.classificationcode;
                                      RAISE NOTICE 'Update AuthEnd: %, EmpStatus: % in employmentrelationship table',rec_provider.termination_date,rec_provider.empstatus;
                                      -- Update AuthEnd in employmentrelationship table  
                                      UPDATE prod.employmentrelationship
                                      SET authend = rec_provider.termination_date::text,
                                          terminationdate = rec_provider.termination_date::text,
                                          recordmodifieddate = (CURRENT_TIMESTAMP at time zone 'PST'),
                                          empstatus = rec_provider.empstatus,
                                          filedate = rec_provider.filedate
                                      WHERE employeeid = rec_provider.employee_id
                                      AND   employerid = rec_provider.employerid::text;
                                                                       
                                      RAISE NOTICE 'Insert into logs.employmentrelationshiphistorylog table';
                                      -- Insert into logs.employmentrelationshiphistorylog table
                                      INSERT INTO logs.employmentrelationshiphistorylog
                                                                              ( relationshipid,personid, employeeid, branchid, workercategory,categorycode,hiredate,
                                                                                empstatus, trackingdate,modified,role, isOverride, isignored, employerid,authstart,authend,
                                                                                terminationdate,sourcekey,filedate,createdby,created
                                                                              )
                                                                              SELECT relationshipid,personid,employeeid,branchid,workercategory,categorycode,hiredate,
                                                                                      empstatus,trackingdate,recordmodifieddate,role,isOverride,isignored,employerid,authstart,
                                                                                      authend,terminationdate,source,filedate::text,createdby,(CURRENT_TIMESTAMP at time zone 'PST')
                                                                                from prod.employmentrelationship
                                                                              WHERE employeeid = rec_provider.employee_id
                                                                              AND   employerid = rec_provider.employerid::text
                                                                              ORDER BY recordmodifieddate DESC LIMIT 1;
                           --Step 1.2 No record exists                   
                           ELSE
                                   RAISE NOTICE '!!!Validation error. No record exists or record already terminated in employmentrelationship table!!!!';
                                   INSERT INTO logs.workercategoryerrors( sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                          (
                                                                                                                                            rec_provider.sourcekey,rec_provider.employee_id,'CDWA',
                                                                                                                                            rec_provider.filedate,rec_provider.employee_classification,
                                                                                                                                            rec_provider.classificationcode,
                                                                                                                                            'No record exists or record already terminated in prod.employmentrelationship table'
                                                                                                                                          );

                           END IF; --End if Step 1.1
			--Step 2: logic for classification codes other than OSAF 
			ELSEIF (rec_provider.classificationcode <> 'OSAF' AND rec_provider.empstatus <> 'Terminated' AND rec_provider.hire_date IS NOT NULL AND rec_provider.initialtrackingdate IS NOT NULL) THEN
                
                            RAISE NOTICE 'empstatus != Terminated and Classificationcode != OSAF and rec_provider.hire_date IS NOT NULL and rec_provider.initialtrackingdate IS NOT NULL';
                            RAISE NOTICE 'Employee id: %,empstatus: % and Classificationcode: % and hiredate: %  InitialTrackingDate: %',rec_provider.employee_id,rec_provider.empstatus,rec_provider.classificationcode,rec_provider.hire_date,rec_provider.initialtrackingdate;
                                        -- Step 2.1 logic to verify if active Employmentrelationship record exists
                                            IF EXISTS(SELECT 1
                                                        FROM prod.employmentrelationship
                                                        WHERE employeeid = rec_provider.employee_id
                                                        AND   employerid = rec_provider.employerid::text
                                                        AND empstatus <> 'Terminated') THEN
                                   
                                                                RAISE NOTICE 'Matching Record exists in employmentrelationship table';
                                                                -- Get existing employmentrelationship record priority value
                                                                SELECT DISTINCT wcm.priority INTO existing_priority_value
                                                                        FROM prod.employmentrelationship sl
                                                                        LEFT JOIN staging.workercategory wcm ON sl.categorycode = wcm.tccode
                                                                        WHERE sl.employeeid = rec_provider.employee_id
                                                                        AND   sl.employerid = rec_provider.employerid::text
                                                                        AND   sl.empstatus <> 'Terminated' LIMIT 1;
                                            
                                                                RAISE NOTICE 'rec_provider.priority: % , existing_priority_value: %',rec_provider.priority,existing_priority_value;
                                                      
                                                                --Step 2.1.1 Verify that Update employmentrelationship record only if new priority is lesser then existing priority and existing priority is not OSAF
                                                                IF (rec_provider.priority < existing_priority_value and existing_priority_value <> 99) THEN
                                                                    RAISE NOTICE 'rec_provider.priority < existing_priority_value, Update';
                                                                    RAISE NOTICE 'Update employmentrelationship table. Classification:  %, ClassificationCode : % Relationship: %',rec_provider.employee_classification,rec_provider.classificationcode,rec_provider.relationship;
                                    
                                                                           -- Update in prod.employmentrelationship table  
                                                                              UPDATE prod.employmentrelationship
                                                                              SET workercategory = rec_provider.employee_classification,
                                                                                  categorycode = rec_provider.ClassificationCode,
                                                                                  trackingdate = rec_provider.InitialTrackingDate,
                                                                                  relationship = rec_provider.relationship,
                                                                                  filedate = rec_provider.filedate,
                                                                                  priority = rec_provider.priority,
                                                                                  recordmodifieddate = (CURRENT_TIMESTAMP at time zone 'PST')
                                                                              WHERE employeeid = rec_provider.employee_id
                                                                              AND   employerid = rec_provider.employerid::text
                                                                              AND   empstatus <> 'Terminated';
                                             
                                                                    RAISE NOTICE 'Insert into logs.employmentrelationshiphistorylog table';
                                                                              -- insert into logs.employmentrelationshiphistorylog table                        
                                                                                INSERT INTO logs.employmentrelationshiphistorylog
                                                                                (
                                                                                 relationshipid,personid,employeeid,branchid,
                                                                                 workercategory,categorycode,hiredate,empstatus,
                                                                                 trackingdate,modified,role, isOverride,isignored,employerid,authstart,
                                                                                 authend,terminationdate,sourcekey,filedate,createdby,created
                                                                               )
                                                                               SELECT relationshipid,personid,employeeid,branchid,workercategory,
                                                                                       categorycode,hiredate,empstatus,trackingdate,
                                                                                       recordmodifieddate,role,isOverride,isignored,
                                                                                       employerid,authstart, authend,terminationdate,
                                                                                       source,filedate::text,createdby,(CURRENT_TIMESTAMP at time zone 'PST')
                                                                                FROM prod.employmentrelationship
                                                                                WHERE employeeid = rec_provider.employee_id
                                                                                AND   employerid = rec_provider.employerid::text
                                                                                ORDER BY recordmodifieddate DESC LIMIT 1;
                                                                 --Step 2.1.2 Override worker categories for IPs , in the event that the care giver is going "down" in worker classification hierarcy
                                                                 ELSEIF (rec_provider.priority > existing_priority_value or existing_priority_value = 99) THEN
                                                        
                                                                    RAISE NOTICE '************************ CDWA data correction *******************************************';
                                                                    RAISE NOTICE 'Overriding the worker category as caregiver is going down in workercatergory hierarchy';
                                                                    RAISE NOTICE 'rec_provider.priority > existing_priority_value or existing_priority_value=99, down in workercatergory hierarchy';
                                                                    RAISE NOTICE 'prod.employmentrelationship table. workercatergory:  %, categorycode : % , isoverride = true',rec_provider.employee_classification,rec_provider.ClassificationCode;
                                                                   
                                                                    RAISE NOTICE 'Update CDWA record in prod.employmentrelationship '; 
                                                                    -- Update CDWA record in prod.employmentrelationship 
                                             										   UPDATE prod.employmentrelationship
                                                                       SET workercategory = rec_provider.employee_classification,
                                                                           categorycode = rec_provider.ClassificationCode,
                                                                           trackingdate = rec_provider.InitialTrackingDate,
                                                                           relationship = rec_provider.relationship,
                                                                           filedate = rec_provider.filedate,
                                                                           priority = rec_provider.priority,
                                                                           recordmodifieddate = (CURRENT_TIMESTAMP at time zone 'PST')
                                                                    WHERE employeeid = rec_provider.employee_id
                                                                    AND   employerid = rec_provider.employerid::TEXT
                                                                    AND   empstatus <> 'Terminated';
                                                                    -- insert into logs.employmentrelationshiphistorylog table                        
                                                                    INSERT INTO logs.employmentrelationshiphistorylog
                                                                                (
                                                                                 relationshipid,personid,employeeid,branchid,
                                                                                 workercategory,categorycode,hiredate,empstatus,
                                                                                 trackingdate,modified,role, isOverride,isignored,employerid,authstart,
                                                                                 authend,terminationdate,sourcekey,filedate,createdby,created
                                                                               )
                                                                     SELECT relationshipid,personid,employeeid,branchid,workercategory,
                                                                                       categorycode,hiredate,empstatus,trackingdate,
                                                                                       recordmodifieddate,role,isOverride,isignored,
                                                                                       employerid,authstart, authend,terminationdate,
                                                                                       source,filedate::text,createdby,(CURRENT_TIMESTAMP at time zone 'PST')
                                                                     FROM prod.employmentrelationship
                                                                     WHERE employeeid = rec_provider.employee_id
                                                                     AND   employerid = rec_provider.employerid::text
                                                                     ORDER BY recordmodifieddate DESC LIMIT 1;
                                                                    --Retrieve personid from employeeid
                                                                    RAISE NOTICE 'Retrieve personid from employeeid';
                                                                    WITH ctepersonid AS
                                                                        (
                                                                        SELECT DISTINCT er.personid
                                                                        FROM prod.employmentrelationship er
                                                                        WHERE er.employeeid IS NOT NULL
                                                                        AND   er.employeeid = rec_provider.employee_id
                                                                        )

                                                                    SELECT personid INTO var_personid
                                                                                    FROM ctepersonid;


                                                                    RAISE NOTICE ' Personid: %',var_personid;
                                                                    WITH cteactiveserv AS
                                                                    (
                                                                        SELECT DISTINCT 'true' AS active 
                                                                        FROM prod.employmentrelationship s
                                                                        WHERE personid IS NOT NULL
                                                                        AND   personid = var_personid
                                                                        AND   s.employerid IS NOT NULL
                                                                        AND   s.employerid <> rec_provider.employerid::text
                                                                        AND   s.empstatus IS NOT NULL
                                                                        AND   LOWER(s.empstatus) = 'active'
                                                                        AND   s.categorycode IS NOT NULL
                                                                        AND   LOWER(s.categorycode) <> 'osaf'
                                                                    )
                                                                    SELECT active INTO var_isactiveemploymentrelationship
                                                                    FROM cteactiveserv;

                                                                    RAISE NOTICE 'Active employmentrelationship exists for other employer : %',var_isactiveemploymentrelationship::text;
                                                                    
                                                                    WITH cteterminatedServ AS
                                                                        (
                                                                        SELECT DISTINCT 'true' AS terminated
                                                                        FROM prod.employmentrelationship s
                                                                        WHERE personid IS NOT NULL
                                                                        AND   personid = var_personid
                                                                        AND   s.employerid IS NOT NULL
                                                                        AND   s.employerid <> rec_provider.employerid ::text
                                                                        AND   s.empstatus IS NOT NULL
                                                                        AND   LOWER(s.empstatus) = 'terminated'
                                                                        AND   s.categorycode IS NOT NULL
                                                                        AND   LOWER(s.categorycode) <> 'osaf'
                                                                        AND   s.isignored = 'false'
                                                                        )

                                                                    SELECT terminated INTO var_isterminatedemploymentrelationship FROM cteterminatedServ;
                                                                    RAISE NOTICE 'Terminated employmentrelationship exists for other employer : %',var_isterminatedemploymentrelationship;
                                                                    --Step 2.1.2.1
                                                                    -- No active employmentrelationship exists for another employer and historical records are present
																		                                IF (var_personid > 0 AND (var_isactiveemploymentrelationship IS NULL OR var_isactiveemploymentrelationship = false) AND var_isterminatedemploymentrelationship ) THEN
																		                                 
                                                                            RAISE NOTICE 'No active employmentrelationship exists for another employer and historical records are present'; 
                                                                            --Get min priority from serviceline      
                                                                            WITH cteminpriority AS
                                                                            (
                                                                                SELECT s.personid,
                                                                                    MIN(s.priority) AS Priority
                                                                                FROM prod.employmentrelationship s
                                                                                WHERE s.isignored = 'false'
                                                                                --AND   s.isoverride = 'false'
                                                                                AND   LOWER(s.categorycode) <> 'osaf'
                                                                                AND   s.personid = var_personid
                                                                                AND   s.employerid <> rec_provider.employerid::TEXT
                                                                                AND   LOWER(s.empstatus) = 'terminated'
                                                                                GROUP BY s.personid
                                                                            )

                                                                            SELECT Priority INTO var_minpriority
                                                                            FROM cteminpriority;

                                                                            RAISE NOTICE 'Getting Minimum priority from employmentrelationship: % ',var_minpriority;
                                                                            RAISE NOTICE 'CDWA priority : %',rec_provider.priority;  

                                                                                    IF (rec_provider.priority > var_minpriority) THEN
                                                                                      RAISE NOTICE 'Going from a higher training category to a lower category, moving from : % to % ',var_minpriority,rec_provider.priority;
                                                                                      RAISE NOTICE 'Employmentrelationship Classificationcode : %',rec_provider.classificationcode; --classificationcode
                                                                                      RAISE NOTICE 'Previous employment relationships are marked as Ignored and modified= CURRENT_TIMESTAMP, Employeeid: %',rec_provider.employee_id;
                                                                                      --Update isignored = 'true'  for previous terminated employmentrelationship records other than CDWA
                                                                                      UPDATE prod.employmentrelationship s
                                                                                         SET isignored = 'true',
                                                                                             recordmodifieddate = (CURRENT_TIMESTAMP at time zone 'PST')
                                                                                      WHERE s.personid IS NOT NULL
                                                                                      AND   s.personid = var_personid
                                                                                      AND   s.employerid IS NOT NULL
                                                                                      AND   s.employerid <> rec_provider.employerid::TEXT
                                                                                      AND   s.empstatus IS NOT NULL
                                                                                      AND   LOWER(s.empstatus) = 'terminated'
                                                                                      AND   s.isignored = 'false'
                                                                                      AND   LOWER(s.createdby) <> 'zenithlegacy';

                                                                                      RAISE NOTICE 'Update CDWA record in prod.employmentrelationship table with isoverride =true  and recordmodifieddate= CURRENT_TIMESTAMP';
                                            
                                                                                      -- Update CDWA record in prod.employmentrelationship table as patchoverride = 1 
                                                                                      UPDATE prod.employmentrelationship 
                                                                                        SET isoverride = 'true',
                                                                                          recordmodifieddate = (CURRENT_TIMESTAMP at time zone 'PST')
                                                                                        WHERE employeeid = rec_provider.employee_id
                                                                                        AND   employerid = rec_provider.employerid::text
                                                                                        AND   LOWER(empstatus) <> 'terminated';

                                                                                        RAISE NOTICE 'Insert into logs.employmentrelationshiphistorylog table';

                                                                                      -- insert into logs.employmentrelationshiphistorylog table                        
                                                                                      INSERT INTO logs.employmentrelationshiphistorylog  
                                                                                                            (
                                                                                                              relationshipid , personid,employeeid,
                                                                                                              branchid,workercategory ,authstart,authend,trackingdate , 
                                                                                                              empstatus,categorycode,employerid,filedate,created,
                                                                                                              createdby,modified,sourcekey,isignored,isoverride,
                                                                                                              hiredate,terminationdate,role
                                                                                                            )
                                                                                      SELECT relationshipid,personid,
                                                                                                                employeeid,branchid,workercategory ,
                                                                                                                authstart,authend,trackingdate,
                                                                                                                empStatus,categorycode,employerid,
                                                                                                                filedate,(CURRENT_TIMESTAMP at time zone 'PST'),
                                                                                                                createdby,recordmodifieddate,source,
                                                                                                                isignored,isoverride,hiredate,terminationdate,role
                                                                                      FROM prod.employmentrelationship
                                                                                      WHERE personid = var_personid and 
                                                                                            LOWER(createdby) <> 'zenithlegacy'
                                                                                      --AND isignored = 'true'
                                                                                      ORDER BY relationshipid;
                                                            
                                                                                     ELSE 
                                                                                     RAISE NOTICE '*******No change for Personid: % in prod.employmentrelationship table for isignored and isoverride due to priority is same or higher******',var_personid;
                                                                                     INSERT INTO logs.workercategoryerrors( sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                                (
                                                                                                                                                  rec_provider.sourcekey,rec_provider.employee_id,'CDWA',
                                                                                                                                                  rec_provider.filedate,rec_provider.employee_classification,
                                                                                                                                                  rec_provider.classificationcode,
                                                                                                                                                  CONCAT('No change for Personid: ',var_personid, ' in prod.employmentrelationship table for isignored and isoverride due to priority is same or higher')
                                                                                                                                                ); 
                                                                                    END IF;
                                  																		ELSE
                                  																			RAISE NOTICE '*******No change for Personid: %  in prod.employmentrelationship table for isignored and isoverride******',var_personid;
                                  																			INSERT INTO logs.workercategoryerrors( sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                          (
                                                                                                                                            rec_provider.sourcekey,rec_provider.employee_id,'CDWA',
                                                                                                                                            rec_provider.filedate,rec_provider.employee_classification,
                                                                                                                                            rec_provider.classificationcode,CONCAT('No change for Personid: ',var_personid, ' in prod.employmentrelationship table for isignored and isoverride')
                                                                                                                                          );  
                                  																		END IF; --END IF Step 2.1.2.1
		
                                                                  -- Step 2.1.3 No changes in Classification                
                                                                 ELSE
                                                                        RAISE NOTICE '!!!!!!No changes in Classification as rec_provider.priority >= existing_priority_value !!!!!!!!';
                                                                        RAISE NOTICE 'In prod.employmentrelationship no record is updated';
                                                                       
                                                                        INSERT INTO logs.workercategoryerrors( sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                          (
                                                                                                                                            rec_provider.sourcekey,rec_provider.employee_id,'CDWA',
                                                                                                                                            rec_provider.filedate,rec_provider.employee_classification,
                                                                                                                                            rec_provider.classificationcode,'No changes in Classification as new priority is same as the existing_priority_value'
                                                                                                                                          );           
                                                                     
                                                                 END IF; -- END IF 2.1.1
											                      -- Step 2.2 Insert a new prod.employmentrelationship record
											                      ELSE
                                                   RAISE NOTICE 'Inside else block, Matching record not found in prod.employmentrelationship';
                                                   RAISE NOTICE 'Employee id : %, EmpStatus: %,Classification: %,ClassificationCode: %,',rec_provider.employee_id,rec_provider.empstatus,rec_provider.employee_classification,rec_provider.classificationcode;
                                                   RAISE NOTICE 'Insert into prod.employmentrelationship table';
                                                   -- insert into prod.employmentrelationship table
                          													INSERT INTO prod.employmentrelationship
                          														( personid , employeeid , BranchId, workercategory, hiredate, authStart, authEnd, trackingDate, relationship
                          														  , empstatus, categoryCode, employerid, filedate, createdby, source, role, priority
                          														)
                          														VALUES
                          														( NULL, rec_provider.employee_id, (
                          															SELECT DISTINCT branchid
                                                        FROM prod.branch
                                                        WHERE employerid IN (SELECT employerid::TEXT
                                                                             FROM prod.employertrust
                                                                             WHERE employertrust.name::TEXT = 'CDWA (IP)'::TEXT
                                                                             AND   employertrust.trust::TEXT = 'TP'::TEXT)
                          															), rec_provider.employee_classification, rec_provider.hire_date, rec_provider.hire_date
                          														  , NULL, rec_provider.initialtrackingdate, rec_provider.relationship, rec_provider.empstatus
                          														  , rec_provider.classificationcode, rec_provider.employerid, rec_provider.filedate
                          														  , 'cdwaprovidersstoredprocedure', rec_provider.sourcekey,'CARE', rec_provider.priority
                          														);
															                          -- insert into logs.employmentrelationshiphistorylog table                        
                                                      INSERT INTO logs.employmentrelationshiphistorylog
                                                                                (
                                                                                 relationshipid,personid,employeeid,branchid,
                                                                                 workercategory,categorycode,hiredate,empstatus,
                                                                                 trackingdate,modified,role, isOverride,isignored,employerid,authstart,
                                                                                 authend,terminationdate,sourcekey,filedate,createdby,created
                                                                               )
                                                      SELECT relationshipid,personid,employeeid,branchid,workercategory,
                                                                                       categorycode,hiredate,empstatus,trackingdate,
                                                                                       recordmodifieddate,role,isOverride,isignored,
                                                                                       employerid,authstart, authend,terminationdate,
                                                                                       source,filedate::text,createdby,(CURRENT_TIMESTAMP at time zone 'PST')
                                                      FROM prod.employmentrelationship
                                                      WHERE employeeid = rec_provider.employee_id
                                                      AND   employerid = rec_provider.employerid::text
                                                      ORDER BY recordmodifieddate DESC LIMIT 1;
                                                      --Net New IPs in the CDWA system: CDWA hires someone as an ADCH but they worked previously as a SHCA for another agency 5 years ago.
                                                      --We need to persist the ADCH classification in our aggregations and ignore the earlier worker classifications
                                                      -- from the historical records to allow the caregiver to "train down" appropriately.
                                                      --Previous employment relationships are marked as Ignored
                                                      --Retrieve BG personid from employeeid
        
                                                        --Retrieve personid from employeeid
                                                      RAISE NOTICE 'Retrieve personid from employeeid';
                                                        WITH ctepersonid AS
                                                          (
                                                            SELECT DISTINCT er.personid
                                                            FROM prod.employmentrelationship er
                                                            WHERE er.employeeid IS NOT NULL
                                                            AND er.employeeid = rec_provider.employee_id
                                                          )

                                                        SELECT personid INTO var_personid FROM ctepersonid;
                                                                  
                                                      RAISE NOTICE ' Personid: %',var_personid;
                                                      WITH cteactiveserv AS
                                                        (
                                                          SELECT DISTINCT 'true' AS active 
                                                          FROM prod.employmentrelationship s
                                                          WHERE personid IS NOT NULL
                                                          AND   personid = var_personid
                                                          AND   s.employerid IS NOT NULL
                                                          AND   s.employerid <> rec_provider.employerid::text
                                                          AND   s.empstatus IS NOT NULL
                                                          AND   LOWER(s.empstatus) = 'active'
                                                          AND   s.categorycode IS NOT NULL
                                                          AND   LOWER(s.categorycode) <> 'osaf'
                                                        )
                                                        SELECT active INTO var_isactiveemploymentrelationship
                                                        FROM cteactiveserv;
              
                                                        RAISE NOTICE 'Active employmentrelationship exists for other employer : %',var_isactiveemploymentrelationship::text;
                                                        WITH cteterminatedServ AS
                                                          (
                                                            SELECT DISTINCT 'true' AS terminated
                                                            FROM prod.employmentrelationship s
                                                            WHERE personid IS NOT NULL
                                                            AND   personid = var_personid
                                                            AND   s.employerid IS NOT NULL
                                                            AND   s.employerid <> rec_provider.employerid::text
                                                            AND   s.empstatus IS NOT NULL
                                                            AND   LOWER(s.empstatus) = 'terminated'
                                                            AND   s.categorycode IS NOT NULL
                                                            AND   LOWER(s.categorycode) <> 'osaf'
                                                            AND   s.isignored = 'false'
                                                          )

                                                      SELECT terminated INTO var_isterminatedemploymentrelationship FROM cteterminatedServ;
                                                      RAISE NOTICE 'Terminated employmentrelationship exists for other employer : %',var_isterminatedemploymentrelationship::text;
												                            --Step 2.2.1	
                                                    -- No active employmentrelationship exists for another employer and historical records are present
                                                    IF (var_personid > 0 AND (var_isactiveemploymentrelationship IS NULL OR var_isactiveemploymentrelationship = false) AND var_isterminatedemploymentrelationship ) THEN

                                                        RAISE NOTICE 'No active employmentrelationship exists for another employer and historical records are present'; 
                                                        --Get min priority from serviceline      
                                                        WITH cteminpriority AS
                                                          (
                                                            SELECT s.personid,
                                                                  MIN(s.priority) AS Priority
                                                            FROM prod.employmentrelationship s
                                                            WHERE s.isignored = 'false'
                                                            --AND   s.isoverride = 'false'
                                                            AND   LOWER(s.categorycode) <> 'osaf'
                                                            AND   s.personid = var_personid
                                                            AND   s.employerid <> rec_provider.employerid::TEXT
                                                            AND   LOWER(s.empstatus) = 'terminated'
                                                            GROUP BY s.personid
                                                          )
                          														    SELECT Priority INTO var_minpriority
                          														    FROM cteminpriority;
                                                                                                
                                                          RAISE NOTICE 'Getting Minimum priority from employmentrelationship: % ',var_minpriority;
                                                          RAISE NOTICE 'CDWA priority : %',rec_provider.priority;  
                                                                                              
                                                                      IF (rec_provider.priority > var_minpriority) THEN
                                                                            RAISE NOTICE 'Going from a higher training category to a lower category, moving from : % to % ',var_minpriority,rec_provider.priority;
                                                                            RAISE NOTICE 'Employmentrelationship Classificationcode : %',rec_provider.classificationcode; --classificationcode
                                                                            RAISE NOTICE 'Previous employment relationships are marked as Ignored and modified= CURRENT_TIMESTAMP, Employeeid: %',rec_provider.employee_id;
                                                                            --Update isignored = 'true' for previous terminated employmentrelationship records other than CDWA
                                                                            UPDATE prod.employmentrelationship s
                                                                              SET isignored = 'true',
                                                                                recordmodifieddate = (CURRENT_TIMESTAMP at time zone 'PST')
                                                                            WHERE s.personid IS NOT NULL
                                                                            AND   s.personid = var_personid
                                                                            AND   s.employerid IS NOT NULL
                                                                            AND   s.employerid <> rec_provider.employerid::TEXT
                                                                            AND   s.empstatus IS NOT NULL
                                                                            AND   LOWER(s.empstatus) = 'terminated'
                                                                            AND   s.isignored = 'false'
                                                                            AND   LOWER(s.createdby) <> 'zenithlegacy';
                                
                                                                            RAISE NOTICE 'Update CDWA record in prod.employmentrelationship table with isoverride =true  and recordmodifieddate= CURRENT_TIMESTAMP';
                                
                                                                            -- Update CDWA record in prod.employmentrelationship table as patchoverride = 1 
                                                                            UPDATE prod.employmentrelationship
                                                                            SET isoverride = 'true',
                                                                              recordmodifieddate = (CURRENT_TIMESTAMP at time zone 'PST')
                                                                            WHERE employeeid = rec_provider.employee_id
                                                                            AND   employerid = rec_provider.employerid::TEXT
                                                                            AND   LOWER(empstatus) <> 'terminated';

                                                                            RAISE NOTICE 'Insert into logs.employmentrelationshiphistorylog table';
                                                                            -- insert into logs.employmentrelationshiphistorylog table                        
                                                                            INSERT INTO logs.employmentrelationshiphistorylog
                                                                                  (
                                                                                    relationshipid,personid,employeeid,branchid,workercategory,authstart,authend,
                                                                                    trackingdate,empstatus,categorycode,employerid,filedate,created,createdby,
                                                                                    modified,sourcekey,isignored,isoverride,hiredate,terminationdate,role
                                                                                  )
                                                                                  SELECT relationshipid,personid,employeeid,branchid,workercategory,authstart,
                                                                                        authend,trackingdate,empStatus,categorycode,employerid,
                                                                                        filedate,(CURRENT_TIMESTAMP at time zone 'PST'),createdby,recordmodifieddate,source,
                                                                                        isignored,isoverride,hiredate,terminationdate,role
                                                                                  FROM prod.employmentrelationship
                                                                                  WHERE personid = var_personid or employeeid = rec_provider.employee_id
                                                                                  AND   LOWER(createdby) <> 'zenithlegacy'
                                                                                  --AND   isignored = 'true'
                                                                                  ORDER BY relationshipid;

                      
                                                                          ELSE 
                                                                            RAISE NOTICE '*******No change for Personid: % in prod.employmentrelationship table for isignored and isoverride due to priority is same or higher******',var_personid;
                                                                              INSERT INTO logs.workercategoryerrors( sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                                (
                                                                                                                                                  rec_provider.sourcekey,rec_provider.employee_id,'CDWA',rec_provider.filedate,
                                                                                                                                                  rec_provider.employee_classification,rec_provider.classificationcode,
                                                                                                                                                  CONCAT('No change for Personid: ',var_personid, ' in prod.employmentrelationship table for isignored and isoverride due to priority is same or higher')
                                                                                                                                                );  
                                                                            END IF;

                                											ELSE
                                													RAISE NOTICE '*******No change for Personid: %  in  prod.employmentrelationship table for isignored and isoverride ******',var_personid;
                                													INSERT INTO logs.workercategoryerrors( sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                                                          (
                                                                                                                                                                            rec_provider.sourcekey,rec_provider.employee_id,
                                                                                                                                                                            'CDWA',rec_provider.filedate,rec_provider.employee_classification,
                                                                                                                                                                            rec_provider.classificationcode,
                                                                                                                                                                            CONCAT('No change for Personid: ',var_personid, ' in prod.employmentrelationship table for isignored and isoverride')
                                                                                                                                                                          );  
                                											END IF; --Step 2.2.1
                                                         											
                                            END IF; -- End if Step 2.1
			 --Step 3: logic for classification code is OSAF and hiredate is not null
			ELSEIF (rec_provider.classificationcode = 'OSAF' AND rec_provider.hire_date IS NOT NULL AND rec_provider.empstatus <> 'Terminated') THEN

                          RAISE NOTICE 'Classificationcode = OSAF and empstatus != Terminated and rec_provider.hiredate!=null';   
                          RAISE NOTICE 'Employee id: %,empstatus: % and Classificationcode: % Hiredate: % ',rec_provider.employee_id,rec_provider.empstatus,rec_provider.classificationcode,rec_provider.hire_date;

                                          --Step 3.1 Insert O&S record if no active employmentrelationship record exists for an employee                                       
                                          IF NOT EXISTS(SELECT 1
                                                         FROM   prod.employmentrelationship
                                                         WHERE  employeeid = rec_provider.employee_id
                                                         AND    employerid = rec_provider.employerid::text
                                                         AND    empstatus <> 'Terminated') THEN
                                                        
                                                          RAISE NOTICE 'Insert O&S record into employmentrelationship table as no active employmentrelationship record exists for an employee ';
                                                          -- insert into employmentrelationship table
                                                          INSERT INTO prod.employmentrelationship
                                                              ( personid, employeeid, BranchId, workercategory, hiredate, authStart
                                                                , authEnd, trackingDate, relationship, empstatus, categoryCode
                                                                , employerid, filedate, createdby, source, role, priority
                                                              )
                                                              VALUES
                                                              ( NULL
                                                                , rec_provider.employee_id, (
                                                                      SELECT DISTINCT branchid
                                                                      FROM prod.branch
                                                                      WHERE employerid IN (SELECT employerid::TEXT
                                                                                           FROM prod.employertrust
                                                                                           WHERE employertrust.name::TEXT = 'CDWA (IP)'::TEXT
                                                                                           AND   employertrust.trust::TEXT = 'TP'::TEXT)
                                                                  ), rec_provider.employee_classification, rec_provider.hire_date
                                                                , rec_provider.hire_date, NULL,
                                                                 --If there is no initialtrackingdate date for O&S training then consider hiredate
                                                                  CASE
                                                                      WHEN rec_provider.initialtrackingdate IS NOT NULL
                                                                          THEN rec_provider.initialtrackingdate
                                                                          ELSE rec_provider.hire_date
                                                                  END
                                                                , rec_provider.relationship, rec_provider.empstatus, rec_provider.classificationcode
                                                                , rec_provider.employerid, rec_provider.filedate, 'cdwaprovidersstoredprocedure'
                                                                , rec_provider.sourcekey, 'CARE', rec_provider.priority
                                                              );
															
                                        
                                                              RAISE NOTICE 'Insert into logs.employmentrelationshiphistorylog table';
                                                                            -- insert into logs.employmentrelationshiphistorylog table                        
                                                                INSERT INTO logs.employmentrelationshiphistorylog
                                                                  (
                                                                    relationshipid,personid,employeeid,branchid,workercategory,categorycode,hiredate,empstatus,
                                                                    trackingdate, modified,role,isOverride,isignored,employerid,authstart,authend,
                                                                    terminationdate,sourcekey,filedate,createdby,created
                                                                  )
                                                                  SELECT relationshipid, personid,employeeid, branchid,workercategory,categorycode,
                                                                        hiredate,empstatus,trackingdate,recordmodifieddate,role,isOverride,
                                                                        isignored,employerid,authstart,authend,terminationdate,source,filedate::TEXT,createdby,(CURRENT_TIMESTAMP at time zone 'PST')
                                                                  FROM prod.employmentrelationship
                                                                  WHERE employeeid = rec_provider.employee_id
                                                                  AND   employerid = rec_provider.employerid::TEXT
                                                                  ORDER BY recordmodifieddate DESC LIMIT 1;

															              --Step 3.2 NO changes in classification for OSAF      
                                          ELSE
                                              RAISE NOTICE '!!!!!!No changes in Classification as OSAF record exists/Active Classification exists!!!!!!!!';
                                              RAISE NOTICE 'In prod.employmentrelationship no record is updated';
                                              
                                              INSERT INTO logs.workercategoryerrors( sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                          (
                                                                                                                                            rec_provider.sourcekey,rec_provider.employee_id,'CDWA',
                                                                                                                                            rec_provider.filedate,rec_provider.employee_classification,
                                                                                                                                            rec_provider.classificationcode,'No changes in Classification as OSAF record exists/Active Classification exists'
                                                                                                                                          );                         
                                                                     
                                          END IF; -- END IF Step 3.1
			--Step 4: No changes in classification 
			ELSE
                 RAISE NOTICE '!!!!!!Employeeid: % no changes in Classification or Classification data is invalid !!!!!!!',rec_provider.employee_id;
                 INSERT INTO logs.workercategoryerrors( sourcekey, employeeid, filesource, filemodifieddate, workercategory, code, error) VALUES
                                                                                                                                          (
                                                                                                                                            rec_provider.sourcekey,rec_provider.employee_id, 'CDWA',
                                                                                                                                            rec_provider.filedate,rec_provider.employee_classification,
                                                                                                                                            rec_provider.classificationcode,'No changes in Classification or Classification data is invalid '
                                                                                                                                          );  
			END IF; --Step 1
  
existing_priority_value:= -1;
RAISE NOTICE '********End execution***********';
RAISE NOTICE '******************************************************************************************';
END LOOP;

-- close the cursor
CLOSE cur_providers;

--Insert an entry into the logs table
WITH cte AS
(
 SELECT 'glue-cdwa-providerinfo-employmentrelationship-process' AS processname,
       MAX(filemodifieddate) AS filedate,
       '1' AS success
FROM raw.cdwa where isvalid = TRUE
),
ctefinal AS
(
  SELECT *
  FROM cte c
  WHERE c.filedate NOT IN (SELECT lastprocesseddate
                         FROM logs.lastprocessed
                         WHERE processname = 'glue-cdwa-providerinfo-employmentrelationship-process'
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

END;
$BODY$;

