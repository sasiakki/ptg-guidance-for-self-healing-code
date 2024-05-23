CREATE OR REPLACE PROCEDURE staging.sp_quarantinemasterperson()
  LANGUAGE plpgsql
AS
$body$
declare var_relationshipid integer;
var_employeeid bigint;
var_workercategory character varying;
var_categorycode character varying;
var_esource character varying;
var_branchid bigint;
var_employerid bigint;
var_hiredate timestamp without time zone;
var_authstart date;
var_authend date;
var_terminationdate date;
var_empstatus character varying;
var_trackingdate date;
var_isignored integer;
var_isoverride integer;
var_person_unique_id bigint;
var_firstname character varying;
var_lastname character varying;
var_middlename character varying;
var_ssn character varying;
var_email1 character varying;
var_email2 character varying;
var_homephone character varying;
var_mobilephone character varying;
var_language character varying;
var_physicaladdress character varying;
var_mailingaddress character varying;
var_status character varying;
var_exempt character varying;
var_type character varying;
var_credentialnumber character varying;
var_cdwaid bigint;
var_dshsid bigint;
var_iscarinaeligible boolean;
var_dob character varying;
var_ahcas_eligible boolean;
var_recordmodifieddate timestamp without time zone;
var_recordcreateddate timestamp without time zone;
var_sfcontactid character varying;
var_approval_status character varying;
var_sourcekey character varying;
var_mailingstreet1 character varying;
var_mailingstreet2 character varying;
var_mailingcity character varying;
var_mailingstate character varying;
var_mailingzip character varying;
var_mailingcountry character varying;
c_zip character varying;
var_matched_sourcekeys character varying;
var_role character varying;
row_classificationstaging record;
rec_icd12 record;
-- variables used
var_personid bigint;
var_qpersonid bigint;
arr_split_keys text [];
r character varying;

cur_person cursor for select * from staging.personquarantine where approval_status='update' or approval_status='create' order by recordmodifieddate; 
--cur_emp cursor for select * from staging.employmentrelationshipquarantine where approval_status='approved' order by recordmodifieddate; --Add columns

BEGIN
	--Capturing data steward changes made to staging.personquarantine in logs.personquarantine
insert into logs.personquarantine
select * from staging.personquarantine where (approval_status='update' or approval_status='create') and person_unique_id not in (select distinct person_unique_id from logs.personquarantine where approval_status='update' or approval_status='create');
	RAISE NOTICE 'Starting Execution';
	open cur_person;
	LOOP
	
		FETCH cur_person INTO var_person_unique_id,var_firstname,var_lastname,
		var_middlename, var_ssn, var_email1, var_email2, var_homephone, var_mobilephone,
		 var_language, var_physicaladdress, var_mailingaddress, var_status, var_exempt, var_type,
		  var_workercategory, var_credentialnumber, var_cdwaid, var_dshsid, var_categorycode, var_iscarinaeligible, var_qpersonid, var_dob, var_hiredate, 
		  var_trackingdate, var_ahcas_eligible, var_recordmodifieddate, var_recordcreateddate, var_sfcontactid, var_approval_status, var_sourcekey, var_mailingstreet1, var_mailingstreet2, var_mailingcity,
		   var_mailingstate, var_mailingzip, var_mailingcountry, var_matched_sourcekeys;
		EXIT WHEN NOT FOUND;
		
		IF (lower(trim(var_approval_status)) = 'create') Then
		  
      RAISE NOTICE '***************var_approval_status = create***************';
		  -- get max of personids from prod.person and add 1 for new personid
			SELECT MAX(p.personid) +1 INTO var_personid FROM prod.person p;
			
			RAISE NOTICE 'New personid: %',var_personid;	
			RAISE NOTICE 'Insert into prod.person with new personid';
			
			 INSERT INTO prod.person(firstname, lastname, middlename, ssn, email1, email2, homephone, mobilephone, language, physicaladdress,
				mailingaddress, exempt, cdwaid, dshsid, 
				personid, dob, recordmodifieddate, recordcreateddate, mailingstreet1, mailingstreet2, mailingcity,
				mailingstate, mailingzip, mailingcountry, matched_sourcekeys,credentialnumber)
				VALUES (upper(var_firstname), upper(var_lastname), upper(var_middlename), var_ssn, var_email1, var_email2, var_homephone, var_mobilephone, var_language,
				var_physicaladdress, var_mailingaddress,'false',var_cdwaid, var_dshsid, var_personid, var_dob,
				CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, var_mailingstreet1, var_mailingstreet2, var_mailingcity, var_mailingstate,
				var_mailingzip, var_mailingcountry, var_matched_sourcekeys,var_credentialnumber); 
			
			RAISE NOTICE 'Update personid in staging.personhistory table';
			 UPDATE staging.personhistory p
					SET personid = var_personid::bigint
					WHERE p.personid is null and
					(
					 (p.dshsid = var_dshsid)
					 or
					 (lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.ssn) = var_ssn and lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname)
					 or
					 (lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and trim(p.dob) = var_dob)
					 or
					 (lower(trim(Left(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying,4))) = left(var_lastname,4) and
						lower(trim(Left(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying,4))) = left(var_firstname,4) and trim(p.ssn) = var_ssn and trim(p.dob) = var_dob)
					 or
					 (lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname
						and trim(p.ssn) = var_ssn and (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone))
					 or
					 (lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.ssn) = var_ssn and (lower(trim(p.email1)) = var_email1 or lower(trim(p.email2)) = var_email2 or lower(trim(p.email1)) = var_email2 or lower(trim(p.email2)) = var_email1))
					 or
					 (lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.dob) = var_dob and
						(lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone))
					 or
					 (lower(trim(Left(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying,4))) = left(var_lastname,4) and lower(trim(Left(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying,4))) = left(var_firstname,4) and
						trim(p.dob) = var_dob and (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone))
					 or
					 (lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and
						trim(p.ssn) = var_ssn and lower(trim(p.mailingzip)) = c_zip)
					 or
					 (lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and trim(p.dob) = var_dob and lower(trim(p.mailingzip)) = c_zip)
					 or
					 (lower(trim(regexp_replace(p.firstname,'[^\w]+|_','','g')::character varying)) = var_firstname and lower(trim(regexp_replace(p.lastname,'[^\w]+|_','','g')::character varying)) = var_lastname and lower(trim(p.mailingzip)) = c_zip and
				  (lower(trim(p.homephone)) = var_homephone or lower(trim(p.homephone)) = var_mobilephone or lower(trim(p.mobilephone)) = var_homephone or lower(trim(p.mobilephone)) = var_mobilephone))
					); 
					
			--RAISE NOTICE 'Deleting create and processed rows from personquarantine';
         delete from staging.personquarantine where sourcekey = var_sourcekey and  lower(trim(var_approval_status)) = 'create';
			
    ELSEIF (LOWER(TRIM(var_approval_status)) = 'update' AND EXISTS (SELECT 1 FROM prod.person WHERE personid = var_qpersonid)) THEN 
                RAISE NOTICE '***************var_approval_status = update ***************';
		            SELECT var_qpersonid INTO var_personid;
		      			RAISE NOTICE 'Update personid: %',var_personid;
			       -- update prodperson record with the record from staging.personquarantine
			          UPDATE prod.person p
                       SET firstname = COALESCE(UPPER(var_firstname),firstname),
                           lastname = COALESCE(UPPER(var_lastname),lastname),
                           middlename = COALESCE(UPPER(var_middlename),middlename),
                           ssn = COALESCE(var_ssn,ssn),
                           dob = COALESCE(var_dob,dob),
                           email1 = COALESCE(var_email1,email1),
                           email2 = COALESCE(var_email2,email2),
                           homephone = COALESCE(var_homephone,homephone),
                           mobilephone = COALESCE(var_mobilephone,mobilephone),
                           LANGUAGE = COALESCE(var_language,LANGUAGE),
                           physicaladdress = COALESCE(var_physicaladdress,physicaladdress),
                           mailingaddress = COALESCE(var_mailingaddress,mailingaddress),
                           ahcas_eligible = COALESCE(var_ahcas_eligible,ahcas_eligible),
                           credentialnumber = COALESCE(var_credentialnumber,credentialnumber),
                           cdwaid = COALESCE(var_cdwaid,cdwaid),
                           dshsid = COALESCE(var_dshsid,dshsid),
                           mailingstreet1 = COALESCE(var_mailingstreet1,mailingstreet1),
                           mailingstreet2 = COALESCE(var_mailingstreet2,mailingstreet2),
                           mailingcity = COALESCE(var_mailingcity,mailingcity),
                           mailingstate = COALESCE(var_mailingstate,mailingstate),
                           mailingzip = COALESCE(var_mailingzip,mailingzip),
                           mailingcountry = COALESCE(var_mailingcountry,mailingcountry),
                           recordmodifieddate = CURRENT_TIMESTAMP,
                           matched_sourcekeys = CASE
                                                  WHEN p.matched_sourcekeys IS NULL AND var_matched_sourcekeys IS NOT NULL THEN var_matched_sourcekeys
                                                  WHEN p.matched_sourcekeys is  NOT NULL THEN CONCAT (p.matched_sourcekeys,var_matched_sourcekeys)
                                                  ELSE CONCAT (matched_sourcekeys,var_sourcekey,';')
                                                END 
                    WHERE p.personid = var_qpersonid
                    AND   var_qpersonid IS NOT NULL
                    AND   var_qpersonid IN (SELECT personid FROM prod.person); 
                    
		          --RAISE NOTICE 'Deleting update records  and processed rows from personquarantine';
                 delete from staging.personquarantine where sourcekey = var_sourcekey  and  lower(trim(var_approval_status)) = 'update';		
			
	  END IF;
	  
    IF(var_personid IS NOT NULL and var_personid > 0 AND EXISTS (SELECT 1 FROM prod.person WHERE personid = var_personid)) THEN
    
        RAISE NOTICE 'Update personid: % into idcrosswalk with cdwa/dshs id',var_personid;
  			IF var_cdwaid is not NULL and var_dshsid is not null THEN
			
  				UPDATE staging.idcrosswalk
  					SET personid = var_personid, recordmodifieddate = current_timestamp
  				WHERE cdwaid = var_cdwaid and dshsid = var_dshsid;
				
  			ELSIF var_dshsid is not NULL THEN

  				UPDATE staging.idcrosswalk
  					SET personid = var_personid, recordmodifieddate = current_timestamp
  				WHERE dshsid = var_dshsid;
				
  			ELSIF var_cdwaid is not NULL THEN

  				UPDATE staging.idcrosswalk
  					SET personid = var_personid, recordmodifieddate = current_timestamp
  				WHERE cdwaid = var_cdwaid;
			
  			END IF; 
			
        RAISE NOTICE 'Update staging.personhistory with personid';
			
  			var_firstname := lower(trim(var_firstname));
  			var_firstname := regexp_replace(var_firstname,'[^\w]+|_','','g')::character varying;
  			var_lastname := lower(trim(var_lastname));
  			var_lastname := regexp_replace(var_lastname,'[^\w]+|_','','g')::character varying;
  			var_ssn := trim(var_ssn);
  			var_dob := trim(var_dob);
  			var_homephone := lower(trim(var_homephone));
  			var_mobilephone := lower(trim(var_mobilephone));
  			var_email1 := lower(trim(var_email1));
  			var_email2 := lower(trim(var_email2));
  			var_mailingzip := lower(trim(var_mailingzip));
  			c_zip := var_mailingzip;
			
			SELECT INTO arr_split_keys REGEXP_SPLIT_TO_ARRAY(var_matched_sourcekeys,';');
			
      			FOREACH r IN ARRAY arr_split_keys
      			LOOP
				
      				IF r is not NULL and r <> '' THEN
				
      					RAISE NOTICE 'Update staging.personhistory with new personid';
      					UPDATE staging.personhistory p
      						SET personid = var_personid::bigint
      					WHERE p.personid is null and p.sourcekey = trim(r);
					
      					RAISE NOTICE 'Update staging.employmentrelationshiphistory with new personid';
      					UPDATE staging.employmentrelationshiphistory erh
      						SET personid = var_personid::bigint
      					WHERE erh.source = trim(r) and erh.personid is null;

      					RAISE NOTICE 'Update prod.employmentrelationship with new personid';
      					UPDATE prod.employmentrelationship perh
      						SET personid = var_personid::bigint
      					WHERE perh.source = trim(r) and perh.personid is null;

      				END IF;
				          
      			END LOOP;
            
    END IF;
		var_personid:=0; 
	END LOOP;
	CLOSE cur_person;
		
END;
$body$
;
