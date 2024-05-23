-- PROCEDURE: raw.sp_cdwaemployemtrelationshiptraindown_cleanup()

-- DROP PROCEDURE IF EXISTS "raw".sp_cdwaemployemtrelationshiptraindown_cleanup();

CREATE OR REPLACE PROCEDURE "raw".sp_cdwaemployemtrelationshiptraindown_cleanup(
	)
LANGUAGE 'plpgsql'
AS $BODY$

DECLARE 
  rec_provider record;
  var_personid bigint :=-1;
  var_isactiveemploymentrelationship bool := false;
  var_isterminatedemploymentrelationship bool := false;
  var_minpriority integer := -1;
  cur_providers CURSOR FOR
         SELECT DISTINCT personid,
           s.employeeid,
           s.workercategory,
           s.empstatus,
           s.categorycode ,
           s.employerid,
           s.isoverride,
           s.source ,
           s.priority,
           s.relationshipid
   FROM  prod.employmentrelationship  s 
        WHERE s.employerid IS NOT NULL
        AND   s.employerid = '426' --CDWA employer id
        AND   s.personid IS NOT NULL
        AND   lower(s.categorycode) <> 'osaf' 
        AND   s.isoverride <> 'true' 
        AND   lower(s.empstatus) ='active'
		order by s.relationshipid
		;
  
  BEGIN
  -- open the cursor
  open cur_providers;

  LOOP
      -- fetch row into the provider record
      FETCH cur_providers INTO rec_provider;

      -- exit when no more row to fetch
      EXIT WHEN NOT found;
      RAISE NOTICE '^^^^^^^^^Begin execution^^^^^^^^^^^^^';
      
      --Retrieve personid from employeeid
       RAISE NOTICE 'Retrieve personid from employeeid';
        WITH ctepersonid
        AS
        (SELECT DISTINCT er.personid
        FROM prod.employmentrelationship  er
           where er.employeeid IS NOT NULL 
		 --and er.personid = '552499088996'  
			and er.employeeid = rec_provider.employeeid
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
          AND   s.employerid <> rec_provider.employerid
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
            AND   s.employerid <> rec_provider.employerid
            AND   s.empstatus IS NOT NULL
            AND   LOWER(s.empstatus) = 'terminated'
            AND   s.categorycode IS NOT NULL
            AND   LOWER(s.categorycode) <> 'osaf'
            AND   s.isignored = 'false'
          )

       SELECT terminated INTO var_isterminatedemploymentrelationship FROM cteterminatedServ;
       RAISE NOTICE 'Terminated employmentrelationship exists for other employer : %',var_isterminatedemploymentrelationship::text;
       
        -- No active employmentrelationship exists for another employer and historical records are present
       IF (var_personid > 0 AND (var_isactiveemploymentrelationship IS NULL OR var_isactiveemploymentrelationship = false) AND var_isterminatedemploymentrelationship ) THEN
                                                                                      
            RAISE NOTICE 'No active employmentrelationship exists for another employer and historical records are present'; 
                                                                                            --Get min priority from serviceline      
            WITH cteminpriority
            AS
            (SELECT s.personid,
                MIN(s.priority) AS Priority
              FROM prod.employmentrelationship s
              	WHERE s.isignored = 'false' 
			 	AND s.isoverride='false'
              	AND   LOWER(s.categorycode) <> 'osaf'
                AND   s.personid = var_personid
                AND   s.employerid <> rec_provider.employerid
              AND   LOWER(s.empstatus) = 'terminated'
              GROUP BY s.personid
              )
            SELECT Priority INTO var_minpriority
            FROM cteminpriority;
                                                                                                
             RAISE NOTICE 'Getting Minimum priority from employmentrelationship: % ',var_minpriority;
             RAISE NOTICE 'CDWA priority : %',rec_provider.priority;  
                                                                                              
                     IF (rec_provider.priority > var_minpriority) THEN
                          RAISE NOTICE 'Going from a higher training category to a lower category, moving from : % to % ',var_minpriority,rec_provider.priority;
                          RAISE NOTICE 'Employmentrelationship Classificationcode : %',rec_provider.categorycode; --classificationcode
                          --Update isignored = 'true' , isoverride='true' for previous terminated employmentrelationship records other than CDWA
                             UPDATE prod.employmentrelationship s
                                 SET isignored = 'true' , isoverride='true' , recordmodifieddate = (CURRENT_TIMESTAMP at time zone 'UTC') 
                              WHERE s.personid IS NOT NULL 
                              AND   s.personid = var_personid
                              AND   s.employerid IS NOT NULL
                              AND   s.employerid <> rec_provider.employerid
                              AND   s.empstatus IS NOT NULL
                              AND   LOWER(s.empstatus) = 'terminated'
                              AND   s.isignored = 'false'
                              AND LOWER(s.createdby) <> 'zenithlegacy';
                          RAISE NOTICE 'Previous employment relationships are marked as Ignored and modified= CURRENT_TIMESTAMP, Employeeid: %',rec_provider.employeeid;
						  RAISE NOTICE 'Update CDWA record in prod.employmentrelationship table with isoverride =true  and recordmodifieddate= CURRENT_TIMESTAMP';
                          RAISE NOTICE 'Insert into logs.employmentrelationshiphistorylog table';
                              
							 
                              -- insert into logs.servicelinelog table                        
                              INSERT INTO logs.employmentrelationshiphistorylog  
                                (
                                  relationshipid ,      
                                  personid,
                                  employeeid,
                                  branchid,
                                  workercategory ,               
                                  authstart,
                                  authend,
                                  trackingdate , 
                                  empstatus,
                                  categorycode,
                                  employerid,
                                  filedate,
                                  created,
                                  createdby,
                                 modified,     
                                  sourcekey,
                                  isignored,
                              isoverride
                                )
                                SELECT relationshipid,
                                       personid,
                                       employeeid,
                                       branchid,
                                       workercategory ,---Classification
                                       authstart,--AuthStart
                                       authend,---AuthEnd
                                       trackingdate,--InitialTrackingDate
                                       empStatus,---EmpStatus
                                       categorycode,---ClassificationCode
                                       employerid,---EmployerId
                                       filedate,
                                       (CURRENT_TIMESTAMP at time zone 'UTC'),
                                       recordcreateddate , ---createdby
                                       recordmodifieddate, ---modified
									   source,---sourcekey
                                       isignored,
                                       isoverride --patchoverride
                                FROM prod.employmentrelationship
                                WHERE personid = var_personid and 
					
                                 LOWER(createdby) <> 'zenithlegacy'
                              ORDER BY relationshipid;

                       ELSE 
                            RAISE NOTICE '*******No change for Personid: % in prod.employmentrelationship table for isignored and isoverride due to priority is same or higher******',var_personid;
                       END IF;
    ELSE
    RAISE NOTICE '*******No change for Personid: %  in prod.employmentrelationship table for isignored and isoverride******',var_personid;
  END IF;
      
   RAISE NOTICE '^^^^^^^^^^End execution^^^^^^^^^^^';

  var_personid := -1;
  var_isactiveemploymentrelationship := false;
  var_isterminatedemploymentrelationship:= false;
  var_minpriority := -1;
END LOOP;

-- close the cursor
CLOSE cur_providers;

END;
$BODY$;

