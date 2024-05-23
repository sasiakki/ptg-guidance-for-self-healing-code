-- PROCEDURE: raw.sp_processcdwaprovidersdatavalidation()

-- DROP PROCEDURE IF EXISTS "raw".sp_processcdwaprovidersdatavalidation();

CREATE OR REPLACE PROCEDURE "raw".sp_processcdwaprovidersdatavalidation(
	)
LANGUAGE 'plpgsql'
AS $BODY$

DECLARE 
     in_isvalid BOOLEAN   := TRUE;
     in_issoftError BOOLEAN := FALSE;
     in_hardError VARCHAR := ' Errortype: Hard,';
	   in_softError VARCHAR := ' Errortype: Soft,';
	   in_ruleno TEXT       := ' Ruleno: ';
     in_errormsg TEXT     := ''; 
	   in_message TEXT      := ' ErrMessage: ';
	   row_countid INTEGER  := 1;
	   ROW  record;
     cur_cdwaproviders CURSOR 	 
    FOR 
      SELECT *
      FROM raw.fn_getcdwaprovidersbymodifieddate('false');
  
BEGIN

  OPEN cur_cdwaproviders;	   

  LOOP  
      FETCH FROM cur_cdwaproviders INTO row; 
      EXIT WHEN NOT found ;

          in_errormsg := 'BEGIN VALIDATION   ';
          --employeeid (for Pre-Qualified IP this field will be NULL)
          IF (row.employeeid IS NOT NULL AND (CAST(row.employeeid AS TEXT) !~ '^(\d{9})?$' OR CAST(row.employeeid AS TEXT) ~ '^([0-9])\1*$')) THEN 
          in_isvalid := FALSE;
          in_errormsg := CONCAT (in_ruleno , 1 , in_hardError , in_message , 'Employeeid is not valid : ' , row.employeeid);
          END IF;
          -- personid
          IF (row.personid IS NULL OR CAST(row.personid AS TEXT) !~ '^(\d{7}|\d{9})?$' OR CAST(row.personid AS TEXT) ~ '^([0-9])\1*$') THEN 
          in_isvalid := FALSE;
          in_errormsg := CONCAT (in_errormsg,' ', in_ruleno,2,in_hardError,in_message,'Personid is not valid : ',row.personid);
          END IF;
          --firstname
          IF(row.firstname IS NULL OR CAST(row.firstname AS TEXT) !~'^[A-Za-z \-]+$' OR LENGTH(row.firstname::TEXT) > 50) THEN
        	in_isvalid := FALSE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 3 , in_hardError , in_message,'Firstname is not valid : ' , row.firstname);   
          END IF;   
         --middlename
          IF(row.middlename IS NOT NULL AND (CAST(row.middlename AS TEXT) !~'^[A-Za-z \-]+$' OR LENGTH(row.middlename::TEXT) > 50)) THEN
          in_issoftError := TRUE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 4 , in_softError , in_message , 'Middlename is not valid : ',row.middlename); 
          END IF;         	
        --lastname
         IF(row.lastname  IS NULL OR CAST(row.lastname AS TEXT) !~'^[A-Za-z \-]+$' OR LENGTH(row.lastname::TEXT) > 100 ) THEN
          in_isvalid := FALSE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 5 , in_hardError , in_message ,'Lastname is not valid : ' , row.lastname);	
         END IF;  
        --ssn
         IF (row.ssn IS NULL OR CAST(row.ssn AS TEXT) !~ '^(\d{4}|\d{7}|\d{8}|\d{9})?$') THEN
         	in_isvalid := FALSE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 6 , in_hardError , in_message ,'SSN is not valid : ' , row.ssn);
        -- Duplicate SSN exits 
          ELSEIF (EXISTS (SELECT 1
                      FROM (SELECT distinct personid
                            FROM raw.cdwaduplicatessnerrors) tableWithduplicates
                      WHERE personid = row.personid)) THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 6 , in_hardError , in_message , 'Duplicate SSN value : ' , row.ssn);
         END IF; 	
      --dob
       IF(row.dob IS NULL OR row.dob <= 19000101 OR (CAST(row.dob AS TEXT) !~'^[\d]+$'  AND  CAST(row.dob AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$')) THEN
      	in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 7 , in_hardError , in_message , 'DOB is not valid : ', row.dob);	
       --Age is lesser
       ELSEIF (date(row.dob::TEXT) > ((current_date - '18 years'::interval)::date)) THEN
        in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 7 , in_hardError , in_message , 'Age is lesser than 18 years : ', row.dob);	
       END IF;  
       --gender
       IF(row.gender IS NULL OR LENGTH(row.gender::TEXT) <> 1 OR NOT EXISTS(select 1 from raw.gender WHERE code = row.gender)) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 8 , in_softError , in_message , 'Gender is not valid : ', row.gender);
      END IF;  
      --ethnicity (for Pre-Qualified IP this field will be NULL)
      IF(row.employeeid IS NOT NULL AND (row.ethnicity IS NULL OR LENGTH(row.ethnicity::TEXT)<>2 OR NOT EXISTS (select 1 from raw.ethnicity WHERE code = row.ethnicity ))) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 9 , in_softError , in_message , 'Ethnicity is not valid : ', row.ethnicity);
      END IF;  
      --race (for Pre-Qualified IP this field will be NULL)
      IF(row.employeeid IS NOT NULL AND (row.race IS NULL OR LENGTH(row.race::TEXT) <> 2 OR NOT EXISTS(select 1 from raw.race WHERE code = row.race ))) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 10 , in_softError , in_message , 'Race is not valid : ', row.race);       	
      END IF;  
      --language (Not required)
      IF(row.language IS NOT NULL AND (NOT EXISTS (select 1 from raw.languages WHERE code = row.language) OR LENGTH(row.language::TEXT) > 5 )) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 11 , in_softError , in_message , 'Language is not valid : ', row.language);	
      END IF;  
      --maritalstatus (Not required)
      IF(row.maritalstatus IS NOT NULL AND (LENGTH(row.maritalstatus::TEXT) <> 1 OR NOT EXISTS (select 1 from raw.maritalstatus WHERE code = row.maritalstatus))) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 12 , in_softError, in_message ,'Maritalstatus is not valid : ', row.maritalstatus);	
       END IF;  
      --phone1
      IF(row.phone1 IS NULL OR CAST(row.phone1 AS  text) !~'^(\d{10})?$' OR CAST(row.phone1 AS TEXT) ~'^([0-9])\1*$') THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 13 , in_softError , in_message ,'Phone1 is not valid : ',row.phone1);	
      END IF;  
      --phone2
      IF(row.phone2 IS NOT NULL AND (CAST(row.phone2 AS  text) !~'^(\d{10})?$' OR CAST(row.phone2 AS TEXT)~'^([0-9])\1*$')) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 14 , in_softError , in_message , 'Phone2 is not valid : ', row.phone2);
      END IF;  
      --email
      IF(row.email IS NULL OR row.email !~ '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$' OR LENGTH(row.email::TEXT) > 150 ) THEN
      	 in_isvalid := FALSE;
         in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 15 , in_hardError , in_message ,'Email is not valid : ', row.email);
      --unique email
      ELSEIF(EXISTS(SELECT 1 FROM raw.cdwa GROUP BY employee_id, email HAVING COUNT(*) >= 1 and employee_id != row.employeeid and email = row.email)) THEN
      	 in_isvalid := FALSE;
         in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 15 , in_hardError , in_message ,'Email is not unique : ', row.email);
      END IF; 
       --mailingadd1
      IF(row.mailingadd1 IS NULL OR LENGTH(row.mailingadd1::TEXT) > 150 OR row.mailingadd1 !~'^[A-Za-z0-9:. _\-#,&/"'']+$') THEN
         in_issoftError := TRUE;
         in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno,16 , in_softError , in_message , 'Mailingadd1 is not valid : ' , row.mailingadd1);	
      END IF;  
      --mailingadd2
      IF(row.mailingadd2 IS NOT NULL AND (LENGTH(row.mailingadd2::TEXT) > 150 OR (LENGTH(row.mailingadd2::TEXT) > 1 AND row.mailingadd2 !~'^[A-Za-z0-9:. _\-#,&/"'']+$'))) THEN
      	 in_issoftError := TRUE;
         in_errormsg := CONCAT(in_errormsg , ' ', in_ruleno , 17 , in_softError , in_message , 'Mailingadd2 is not valid : ', row.mailingadd2);
      END IF;  
      --mailingadd3
      --IF(row.mailingadd3 IS NOT NULL AND (LENGTH(row.mailingadd3::TEXT) > 150 OR (LENGTH(row.mailingadd3::TEXT) > 1 AND row.mailingadd3 !~'^[A-Za-z0-9:. _\-#,&/"'']+$'))) THEN
       --  in_issoftError := TRUE;
        -- in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 18 , in_softError , in_message , 'Mailingadd3 is not valid : ', row.mailingadd3);    
     -- END IF;  
      --mailingcity
      IF(row.mailingcity IS NULL OR CAST(row.mailingcity AS TEXT) !~'^[A-Za-z _.\-"'']+$' OR LENGTH(row.mailingcity::TEXT) > 50) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 19 , in_softError , in_message , 'Mailingcity is not valid : ', row.mailingcity);
      END IF;  
      --mailingstate
      IF(row.mailingstate IS NULL OR LENGTH(row.mailingstate::TEXT) <> 2 ) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 20 , in_softError , in_message , 'Mailingstate is not valid : ' , row.mailingstate);
      END IF;  
      --mailingzip
      IF(row.mailingzip IS NULL OR row.mailingzip ~'[^0-9]' OR row.mailingzip !~'^(\d{5}|\d{9}|\d{10})?$' ) THEN
      	in_issoftError := TRUE; 
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 21 , in_softError , in_message , 'Mailingzip is not valid : ' , row.mailingzip);       		
      END IF;  
      --physicaladd1 (for Pre-Qualified IP this field will be NULL)
       IF(row.employeeid IS NOT NULL AND (row.physicaladd1 IS NULL OR LENGTH(row.physicaladd1::TEXT) > 150 OR row.physicaladd1 !~ '^[A-Za-z0-9:. _\-#,&/"'']+$')) THEN
      	in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 22 , in_hardError , in_message , 'Physicaladd1 is not valid : ' , row.physicaladd1);
      END IF;  
      --physicaladd2
      IF( row.physicaladd2 IS NOT NULL AND (LENGTH(row.physicaladd2::TEXT) > 150  OR (LENGTH(row.physicaladd2::TEXT) > 1 AND row.physicaladd2 !~'^[A-Za-z0-9:. _\-#,&/"'']+$'))) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 23 , in_softError , in_message , 'Physicaladd2 is not valid : ' , row.physicaladd2);
      END IF;  
      --physicaladd3
      --IF(row.physicaladd3 IS NOT NULL AND (LENGTH(row.physicaladd3::TEXT) > 150 OR (LENGTH(row.physicaladd3::TEXT) > 1 AND row.physicaladd3 !~'^[A-Za-z0-9:. _\-#,&/"'']+$'))) THEN
      --	in_issoftError := TRUE;
      --  in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 24 , in_softError , in_message , 'Physicaladd3 is not valid : ' , row.physicaladd3);
      --END IF;  
      --physicalcity (for Pre-Qualified IP this field will be NULL)
      IF(row.employeeid IS NOT NULL AND (row.physicalcity IS NULL OR CAST(row.physicalcity AS TEXT) !~ '^[A-Za-z _.\-"'']+$' OR LENGTH(row.physicalcity::TEXT) > 50)) THEN
          in_isvalid := FALSE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 25 , in_hardError , in_message , 'Physicalcity is not valid : ', row.Physicalcity);
      END IF;  
      --physicalstate (for Pre-Qualified IP this field will be NULL)
      IF(row.employeeid IS NOT NULL AND (row.physicalstate IS NULL  OR LENGTH(row.physicalstate::TEXT) <> 2 OR CAST(row.physicalstate AS TEXT) !~'^[A-Za-z]+$')) THEN
      	  in_isvalid := FALSE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 26 , in_hardError , in_message , 'Physicalstate is not valid : ' , row.physicalstate);
      END IF;  
      --physicalzip (for Pre-Qualified IP this field will be NULL)
      IF(row.employeeid IS NOT NULL AND (row.physicalzip IS NULL OR row.physicalzip ~'[^0-9]' OR row.physicalzip !~ '^(\d{5}|\d{9}|\d{10})?$' )) THEN
      	in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 27 , in_hardError , in_message , 'Physicalzip is not valid: ' , row.physicalzip);               	
       END IF;  
       
      --employeeclassification
      IF(row.employeeclassification IS NULL OR row.employeeclassification !~'^[A-Za-z _&]+$' OR LENGTH(row.employeeclassification::TEXT) > 100 ) THEN
        in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 28 , in_softError , in_message , 'Employeeclassification is not valid : ', row.employeeclassification);
       END IF; 
      IF(row.employeeclassification IS NOT NULL AND row.employeeclassification NOT IN ('Respite Provider','DD Parent Provider','Adult Child Provider','Family Provider','Limited Service Provider','Standard HCA','Orientation & Safety')) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 28 , in_softError , in_message , 'Employeeclassification is not valid : ' , row.employeeclassification);
      END IF;
      IF(row.employeeclassification IS NOT NULL AND row.classificationcode <> 'OSAF' AND row.oscompleteddate IS NULL) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 28 , in_softError , in_message , 'Care giver should complete O&S before they can take care of a client. Invalid data! ' , row.employeeclassification);
      END IF;
      
      -- If OSAF training is active/pending and new classification is received
      IF (row.employeeclassification IS NOT NULL AND EXISTS (SELECT 1
                     FROM prod.employmentrelationship
                     WHERE employeeid = CAST(row.employeeid AS bigint)
                        AND   employerid = CAST(row.employerid AS character varying)
                        AND   empstatus = 'Active'
                        AND   categorycode = 'OSAF') AND row.employeeclassification <> 'Orientation & Safety' AND (row.classificationstartdate IS NOT NULL OR row.oscompleteddate IS NOT NULL)) THEN
          in_issoftError := TRUE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 28 , in_softError , in_message , 'Caregiver need to complete O&S before they can take care of a client. Invalid data! ' , row.classificationcode);  
       -- If new classification priority is greater then existing serviceline priority then soft error
      ELSEIF (row.classificationcode IS NOT NULL AND row.classificationcode <> 'SHCA' AND EXISTS(SELECT DISTINCT 1
                                                                                               FROM prod.employmentrelationship s
                                                                                               LEFT JOIN prod.person p ON p.personid = s.personid
                                                                                               LEFT JOIN staging.personhistory ps ON ps.personid  = p.personid
                                                                                               LEFT JOIN raw.cdwa c ON CONCAT('CDWA-', c.personid) = ps.sourcekey
                                                                                               WHERE c.employee_id = row.employeeid
                                                                                                 AND cast(s.employerid as int) <> row.employerid
                                                                                                 --AND s.source NOT ilike 'zenith%'
                                                                                                 AND LOWER(s.empstatus) = 'active')) THEN

            in_issoftError := TRUE;
            in_errormsg := CONCAT(in_errormsg, ' ', in_ruleno, 28, in_softError, in_message,
                                  'Caregiver is also working with an Agency ',
                                  row.classificationcode);
      END IF;
      --exemptstatus
      IF(row.exemptstatus IS NOT NULL AND LENGTH(row.exemptstatus::TEXT) > 1 AND row.exemptstatus NOT IN ('No','Yes')) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 29 , in_softError , in_message , 'Exemptstatus is not valid :', row.exemptstatus);   
      END IF;  
      --backgroundcheckdate
      IF (row.backgroundcheckdate IS NULL OR row.backgroundcheckdate <= 19000101 OR CAST(row.backgroundcheckdate AS TEXT) !~ '^(\d{8})?$' OR (CAST(row.backgroundcheckdate AS TEXT) !~ '^[\d]+$' AND
          CAST(row.backgroundcheckdate AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$') OR (CAST(row.backgroundcheckdate AS TEXT) !~ '^[\d]+$' AND CAST(row.backgroundcheckdate AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$')) THEN
        	in_issoftError := TRUE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 30 , in_softError , in_message , 'Background Check Date is not valid : ' , row.backgroundcheckdate);
       END IF;
       IF ((((DATE(row.backgroundcheckdate::TEXT) + '2 years'::INTERVAL)::DATE) < CURRENT_DATE AND 
                (row.terminationdate IS NULL OR row.carinaeligible = '1'))) THEN
        	in_issoftError := TRUE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 30 , in_softError , in_message , 'Background Check Date is expired and termination date is null or carinaeligible=1: ' , row.backgroundcheckdate);
      END IF;  
      --iedate
      IF( row.iedate IS NULL OR row.iedate <= 19000101 OR CAST(row.iedate AS text) !~ '^(\d{8})?$' OR (CAST(row.iedate AS TEXT) !~ '^[\d]+$' AND  CAST(row.iedate AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$')) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 31 , in_softError , in_message , 'I&E Date is not valid : ', row.iedate);
      END IF; 
       IF(row.iedate IS NOT NULL AND row.backgroundcheckdate IS NULL) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 31 , in_softError , in_message , 'I&E Date is present but Background Check Date is not valid : ', row.backgroundcheckdate);
      END IF;  
      
      --hiredate ProviderOne number is present then hire date must also be 
      IF(row.employeeid IS NOT NULL AND (row.hiredate IS NULL OR row.hiredate <= 19000101 OR CAST(row.hiredate AS text) !~'^(\d{8})?$' OR CAST(row.hiredate AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$') AND row.terminationdate IS NULL)	THEN
		in_isvalid := FALSE;
		in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 32 , in_hardError , in_message , 'Hire Date is not valid : ' , row.hiredate);
      END IF;

--       IF(row.employeeid IS NOT NULL AND row.hiredate IS NOT NULL AND row.backgroundcheckdate IS NULL) 	THEN
--       	in_isvalid := FALSE;
--         in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 32 , in_hardError , in_message , 'Hire Date is present but Background Check Date is null/empty');
--       END IF;  
--       IF(row.employeeid IS NOT NULL AND row.hiredate IS NOT NULL AND row.iedate IS NULL) 	THEN
--       	in_isvalid := FALSE;
--         in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 32 , in_hardError , in_message , 'Hire Date is present but I&E Date is not valid');
--       END IF;  
       IF(row.employeeid IS NOT NULL AND row.hiredate IS NOT NULL AND CAST(row.hiredate AS text) ~ '^(\d{8})?$' AND 
          CAST(row.hiredate AS TEXT) ~ '^(\d{4})(\d{2})(\d{2})+$' AND DATE(row.hiredate::TEXT) > CURRENT_DATE)	THEN
      	in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 32 , in_hardError , in_message , 'Hire Date is greater than the current date : ' , row.hiredate);
      END IF;  
      
      --classificationstartdate
      IF( row.classificationstartdate IS NOT NULL AND (LENGTH(row.classificationstartdate::TEXT) <> 8 OR row.classificationstartdate <= 19000101 OR 
        (CAST(row.classificationstartdate AS TEXT) !~'^[\d]+$' AND CAST(row.classificationstartdate AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$'))) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 33 , in_softError , in_message , 'Classificationstartdate is not valid : ' , row.classificationstartdate);
      END IF;  
      --carinaeligible
      IF(row.carinaeligible IS NULL OR row.carinaeligible NOT IN  ('0','1') OR (((date(row.backgroundcheckdate ::TEXT) + '2 years'::interval)::date) < current_date 
      and row.carinaeligible ='1')) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 34 , in_softError , in_message , 'carinaeligible is not valid : ' , row.carinaeligible);  
      END IF; 
      --ahcaseligible
      IF( row.ahcaseligible IS NOT NULL AND row.ahcaseligible not in ('0','1')) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 35 , in_softError , in_message , 'ahcaseligible is not valid : ' , row.ahcaseligible);
      END IF;  
      --oscompleteddate
      IF( (row.oscompleteddate IS NOT NULL AND (CAST(row.oscompleteddate AS text) !~'^(\d{8})?$')  OR
         row.oscompleteddate <= 19000101 OR  CAST(row.oscompleteddate AS TEXT) !~'^[\d]+$' AND CAST(row.oscompleteddate AS TEXT) !~'^(\d{4})(\d{2})(\d{2})+$')) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 36 , in_softError , in_message , 'oscompleteddate is not valid : ' , row.oscompleteddate);  
      END IF;  
      --terminationdate
      IF( row.terminationdate IS NOT NULL AND (CAST(row.terminationdate AS  text) !~'^(\d{8})?$'  OR row.terminationdate <= 19000101 OR 
          CAST(row.terminationdate AS TEXT) !~'^[\d]+$' AND CAST(row.terminationdate AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$')) THEN
      	in_issoftError := TRUE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 37 , in_softError , in_message , 'Terminationdate is not valid : ' , row.terminationdate);
       END IF; 
      -- No employment relationship record exists and Termination date is received   
      IF ( NOT EXISTS (SELECT 1
                         FROM prod.employmentrelationship
                         WHERE employeeid =  CAST(row.employeeid AS bigint)
                          AND   employerid = CAST(row.employerid AS character varying) AND empstatus = 'Active') AND row.terminationdate IS NOT NULL) THEN
       in_issoftError := TRUE;
       in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 37 , in_softError , in_message , 'No records exists in employment relationship to Terminate. Invalid data!' , row.terminationdate);  
     
     END IF;  
      -- authorizedstartdate        
      IF( row.authorizedstartdate IS NOT NULL AND (CAST(row.authorizedstartdate AS  text) !~'^(\d{8})?$' OR row.authorizedstartdate <= 19000101 OR CAST(row.authorizedstartdate AS TEXT)!~'^[\d]+$' AND 
      CAST(row.authorizedstartdate AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$')) THEN
      	 	in_issoftError := TRUE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 38 , in_softError , in_message , 'Authorizedstartdate is not valid : ' , row.authorizedstartdate);
      END IF;  
      --authorizedenddate
      IF(row.authorizedenddate IS NOT NULL AND (CAST(row.authorizedenddate AS text) !~'^(\d{8})?$' OR row.authorizedenddate <= 19000101 OR 
        CAST(row.authorizedenddate AS TEXT) !~'^[\d]+$' AND CAST(row.authorizedenddate AS TEXT) !~ '^(\d{4})(\d{2})(\d{2})+$'))THEN
          in_issoftError := TRUE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 39 , in_softError , in_message , 'Authorizedenddate is not valid : ' , row.authorizedenddate);
      END IF;  
      --clientcount
--    IF( row.clientcount IS NOT NULL AND LENGTH(row.clientcount::TEXT) > 2 OR (row.clientcount = 0 AND row.terminationdate IS NULL)) THEN
      IF( row.clientcount IS NOT NULL AND CAST(row.clientcount AS TEXT) !~'^[\d]+$') THEN
      	  in_issoftError := TRUE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno, 40 , in_softError , in_message , 'Clientcount is not valid : ' , row.clientcount);
      END IF; 
      --clientrelationship
      IF(row.clientrelationship IS NOT NULL AND CAST(row.clientrelationship AS TEXT) !~ '^[ A-Za-z0-9/\-\)\(]*$') THEN
      	 	in_issoftError := TRUE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 41 , in_softError , in_message , 'Clientrelationship is not valid : ', row.clientrelationship);
      END IF;  
      --clientid
      IF( row.clientid  IS NOT NULL AND (CAST(row.clientid  AS TEXT) !~ '[0-9A-Za-z]' OR CAST(row.clientid AS TEXT) !~ '^[0-9a-zA-Z]{9,11}?$' )) THEN
      	  in_issoftError := TRUE;
          in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 42 , in_softError , in_message , 'Clientid  is not valid : ' , row.clientid) ;
      END IF;  
      --filename
      IF(row.filename = NULL OR row.filename <> CONCAT('CDWA-O-BG-ProviderInfo' , '-' , row.filemodifieddate, '.' , 'csv' )) THEN
      	in_isvalid := FALSE;
        in_errormsg := CONCAT(in_errormsg , ' ' , in_ruleno , 43 , in_hardError , in_message , 'Filename is not valid : ', row.filename);
      END IF;
      
    in_errormsg := CONCAT ('RowId: ' ,row_countid,' ', in_errormsg , '  END VALIDATION        ');

  --If all rows are valid then mark record as valid
    IF(in_isvalid) THEN
        IF(row.clientid IS NOT NULL AND row.clientid != '0' AND row.employeeid IS NOT NULL) THEN
              -- Hired IP with multiple clients
              UPDATE raw.cdwa
                 SET isvalid = in_isvalid,
                     error_message = NULL
              WHERE client_id = row.clientid
              AND   employee_id = row.employeeid
              AND   personid = row.personid
              AND   COALESCE(hire_date,0) = COALESCE(row.hiredate,0)
              AND   filename = row.filename;
         ELSEIF(row.clientid IS NULL AND row.employeeid IS NOT NULL) THEN
            --Hired IP with no client
             UPDATE raw.cdwa
                 SET isvalid = in_isvalid,
                     error_message = NULL
              WHERE employee_id = row.employeeid
              AND   personid = row.personid
              AND   filename = row.filename;
         ELSE
            --Pre-qualifed Ip with employeeid as NULL
             UPDATE raw.cdwa
                 SET isvalid = in_isvalid,
                     error_message = NULL
              WHERE employee_id IS NULL
              AND   personid = row.personid
              AND   filename = row.filename;
         END IF;   

    END IF;
    
    RAISE NOTICE ' % ',in_errormsg;
         
    IF (in_isvalid = FALSE or in_issoftError) THEN
    
      -- if we have any soft error or hard errors then update errormessage 
      -- if clientid is present
          IF(row.clientid IS NOT NULL AND row.clientid != '0' AND row.employeeid IS NOT NULL) THEN
           
               IF(row.hiredate IS NOT NULL AND row.iedate IS NOT NULL) THEN
           
                  UPDATE raw.cdwa
                     SET error_message = in_errormsg
                  WHERE client_id = row.clientid
                  AND   employee_id = row.employeeid
                  AND   personid = row.personid
                  AND   hire_date = row.hiredate
                  AND   ie_date  = row.iedate
                  AND   filename = row.filename;
              ELSEIF(row.hiredate IS NULL AND row.iedate IS NOT NULL) THEN
               
                 UPDATE raw.cdwa
                     SET error_message = in_errormsg
                  WHERE client_id = row.clientid
                  AND   employee_id = row.employeeid
                  AND   personid = row.personid
                  AND   hire_date IS NULL
                  AND   ie_date  = row.iedate
                  AND   filename = row.filename;
              ELSEIF(row.hiredate IS NOT NULL AND row.iedate IS NULL) THEN
               
                 UPDATE raw.cdwa
                     SET error_message = in_errormsg
                  WHERE client_id = row.clientid
                  AND   employee_id = row.employeeid
                  AND   personid = row.personid
                  AND   hire_date = row.hiredate
                  AND   ie_date  IS NULL
                  AND   filename = row.filename;
               ELSE
               
                 UPDATE raw.cdwa
                     SET error_message = in_errormsg
                  WHERE client_id = row.clientid
                  AND   employee_id = row.employeeid
                  AND   personid = row.personid
                  AND   hire_date IS NULL
                  AND   ie_date  IS NULL
                  AND   filename = row.filename;
              END IF;
          ELSEIF(row.clientid IS NULL AND row.employeeid IS NOT NULL) THEN
            --if no client id is present then update based on employeeid personid and filename
              UPDATE raw.cdwa
                 SET error_message = in_errormsg
              WHERE client_id IS NULL
              AND employee_id = row.employeeid
              AND   personid = row.personid
              AND   filename = row.filename;
          ELSE
              --Pre-qualifed Ip
              UPDATE raw.cdwa
                 SET error_message = in_errormsg
              WHERE employee_id IS NULL
              AND   personid = row.personid
              AND   filename = row.filename;
         
          END IF;

    -- Insert a error message details into log table 
          INSERT INTO logs.fileprocesserrorlogs
          (
            row_id,
            employee_id,
            name,
            error_message,
            file_category,
			file_name
          )
          VALUES
          (
            row_countid,
            row.employeeid,
            CONCAT(row.firstname,' ',row.middlename,' ',row.lastname),
            in_errormsg,
            'CDWA',
            row.filename
          );
          
    END IF;
	
    in_isvalid := TRUE;
    in_issoftError := FALSE;
    in_errormsg := ' ';
    row_countid := row_countid + 1;
    
  END LOOP;
  
 CLOSE cur_cdwaproviders;
 
--Insert an entry into the logs table
WITH cte AS
(
 SELECT 'glue-cdwa-validation' AS processname,
       MAX(filemodifieddate) as filedate,
       '1' AS success
FROM raw.cdwa
),
ctefinal AS
(
  SELECT *
  FROM cte c
  WHERE c.filedate NOT IN (SELECT lastprocesseddate
                         FROM logs.lastprocessed
                         WHERE processname = 'glue-cdwa-validation'
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
