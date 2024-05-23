-- PROCEDURE: staging.sp_newmasterperson()

-- DROP PROCEDURE staging.sp_newmasterperson();

CREATE OR REPLACE PROCEDURE staging.sp_newmasterperson(
	)
LANGUAGE 'plpgsql'
AS $BODY$
declare var_firstname CHARACTER VARYING;
var_lastname CHARACTER VARYING;
var_middlename CHARACTER VARYING;
var_ssn CHARACTER VARYING;
var_email1 CHARACTER VARYING;
var_email2 CHARACTER VARYING;
var_homephone CHARACTER VARYING;
var_mobilephone CHARACTER VARYING;
var_language CHARACTER VARYING;
var_physicaladdress CHARACTER VARYING;
var_mailingaddress CHARACTER VARYING;
var_status CHARACTER VARYING;
var_exempt CHARACTER VARYING;
var_type CHARACTER VARYING;
var_workercategory CHARACTER VARYING;
var_credentialnumber CHARACTER VARYING;
var_cdwaid BIGINT;
var_dshsid BIGINT;
var_categorycode CHARACTER VARYING;
var_iscarinaeligible BOOLEAN;
var_ahcas_eligible BOOLEAN;
var_personid BIGINT;
var_dob CHARACTER VARYING;
var_hiredate TIMESTAMP without time zone;
var_trackingdate DATE;
var_employeeid CHARACTER VARYING;
var_recordmodifieddate TIMESTAMP without time zone;
var_recordcreateddate TIMESTAMP without time zone;
var_employerid CHARACTER VARYING;
var_branchid CHARACTER VARYING;
var_authstart DATE;
var_authend DATE;
var_empstatus CHARACTER VARYING;
var_terminationdate DATE;
var_isoverride BOOLEAN;
var_isignored BOOLEAN;
var_sourcekey CHARACTER VARYING;
var_phc INTEGER;
var_erhc INTEGER;
var_esource CHARACTER VARYING;
var_mailingstreet1 CHARACTER VARYING;
var_mailingstreet2 CHARACTER VARYING;
var_mailingcity CHARACTER VARYING;
var_mailingstate CHARACTER VARYING;
var_mailingzip CHARACTER VARYING;
var_mailingcountry CHARACTER VARYING;
var_puid NUMERIC;
var_rn BIGINT;
var_role CHARACTER VARYING;
row_classificationstaging record;
rec_icd12 record;

cur_icd12 cursor for select * from staging.fn_gethistory() order by recordmodifieddate; 

--delta_timestamp_from TIMESTAMP WITH TIME ZONE;
delta_timestamp_to TIMESTAMP WITH TIME ZONE;

BEGIN

    SELECT CURRENT_TIMESTAMP INTO delta_timestamp_to;

    RAISE NOTICE 'Starting Execution %', Now();
    
    open cur_icd12;

    LOOP

        fetch cur_icd12 into var_firstname, var_lastname, var_middlename, var_ssn, var_email1, var_email2, var_homephone, var_mobilephone, var_language, var_physicaladdress, var_mailingaddress, var_status, var_exempt, var_type, var_workercategory, var_credentialnumber, var_cdwaid, var_dshsid, var_categorycode, var_iscarinaeligible, var_personid, var_dob, var_hiredate, var_trackingdate, var_employeeid, var_sourcekey, var_recordmodifieddate, var_recordcreateddate, var_employerid, var_branchid, var_authstart, var_authend, var_empstatus, var_terminationdate, var_isoverride, var_isignored, var_esource, var_mailingstreet1, var_mailingstreet2, var_mailingcity, var_mailingstate, var_mailingzip, var_mailingcountry, var_role, var_ahcas_eligible, var_rn;

        EXIT WHEN NOT FOUND;
		
			var_firstname := NULLIF(TRIM(var_firstname ),'');
            var_lastname := NULLIF(TRIM(var_lastname ),'');
            var_middlename:= NULLIF(TRIM(var_middlename),'');
            var_ssn := NULLIF(TRIM(var_ssn ),'');
            var_dob:= NULLIF(TRIM(var_dob),'');
            var_email1 := NULLIF(TRIM(var_email1 ),'');
            var_email2 := NULLIF(TRIM(var_email2 ),'');
            var_homephone := NULLIF(TRIM(var_homephone ),'');
            var_mobilephone := NULLIF(TRIM(var_mobilephone ),'');
            var_language := NULLIF(TRIM(var_language ),'');
            var_physicaladdress := NULLIF(TRIM(var_physicaladdress ),'');
            var_mailingaddress:= NULLIF(TRIM(var_mailingaddress),'');
            var_mailingstreet1 := NULLIF(TRIM(var_mailingstreet1 ),'');
            var_mailingstreet2 := NULLIF(TRIM(var_mailingstreet2 ),'');
            var_mailingcity := NULLIF(TRIM(var_mailingcity ),'');
            var_mailingstate := NULLIF(TRIM(var_mailingstate ),'');
            var_mailingzip := NULLIF(TRIM(var_mailingzip ),'');
            var_mailingcountry := NULLIF(TRIM(var_mailingcountry ),'');
            var_sourcekey:= NULLIF(TRIM(var_sourcekey),'');

            RAISE NOTICE 'personid is null, start matching';

            var_personid := coalesce(prod.fn_matchsourcekey(var_sourcekey),prod.fn_checkprodperson(upper(var_firstname), upper(var_lastname), var_ssn, var_dob, var_homephone, var_mobilephone, var_email1, var_email2, var_mailingaddress, var_mailingzip, var_dshsid));

            IF var_personid is not NULL Then

                RAISE NOTICE 'found match, updating prod.person';

                RAISE NOTICE '% assigned to % with employeeid %',var_personid,upper(var_firstname),var_employeeid;

                UPDATE prod.person p

                    SET firstname= TRIM(COALESCE(upper(var_firstname),firstname)),

                        lastname= TRIM(COALESCE(upper(var_lastname),lastname)),

                        middlename= TRIM(COALESCE(upper(var_middlename),middlename)),

                        ssn= TRIM(COALESCE(var_ssn,ssn)),

                        dob= TRIM(COALESCE(var_dob,dob)),

                        email1= TRIM(COALESCE(var_email1,email1)),

                        email2= TRIM(COALESCE(var_email2,email2)),

                        homephone= TRIM(COALESCE(var_homephone,homephone)),

                        mobilephone= TRIM(COALESCE(var_mobilephone,mobilephone)),

                        language= TRIM(COALESCE(var_language,language)),

                        physicaladdress= TRIM(COALESCE(var_physicaladdress,physicaladdress)),

                        mailingaddress = TRIM(COALESCE(var_mailingaddress,mailingaddress)),

                        ahcas_eligible = COALESCE(var_ahcas_eligible,ahcas_eligible),

                        --exempt= COALESCE(var_exempt,exempt),

                        --type= COALESCE(var_type,type),

                        --credentialnumber= COALESCE(var_credentialnumber,credentialnumber),

                        cdwaid= COALESCE(var_cdwaid,cdwaid),

                        dshsid= COALESCE(var_dshsid,dshsid),

                        mailingstreet1= TRIM(COALESCE(var_mailingstreet1,mailingstreet1)),

                        mailingstreet2= TRIM(COALESCE(var_mailingstreet2,mailingstreet2)),

                        mailingcity= TRIM(COALESCE(var_mailingcity,mailingcity)),

                        mailingstate= TRIM(COALESCE(var_mailingstate,mailingstate)),

                        mailingzip= TRIM(COALESCE(var_mailingzip,mailingzip)),

                        mailingcountry= TRIM(COALESCE(var_mailingcountry,mailingcountry)),

                        recordmodifieddate= CURRENT_TIMESTAMP,
                        
                                    matched_sourcekeys= CASE 
                                                            WHEN p.matched_sourcekeys is NULL THEN CONCAT(var_sourcekey,';')
                                                            WHEN p.matched_sourcekeys like CONCAT('%',var_sourcekey,'%')::text THEN p.matched_sourcekeys
                                                            ELSE CONCAT(matched_sourcekeys,var_sourcekey,';')
                                                            END

                    WHERE p.personid = var_personid
					
					AND 
					(
						md5(UPPER(concat_ws('|',
							NULLIF(TRIM(firstname),''),NULLIF(TRIM(lastname),''),NULLIF(TRIM(middlename),''),NULLIF(TRIM(ssn),''),NULLIF(TRIM(dob),''),
							NULLIF(TRIM(email1),''),NULLIF(TRIM(email2),''),NULLIF(TRIM(homephone),''),NULLIF(TRIM(mobilephone),''),NULLIF(TRIM(language),''),
							NULLIF(TRIM(physicaladdress),''),NULLIF(TRIM(mailingaddress),''),ahcas_eligible,cdwaid,dshsid,
							NULLIF(TRIM(mailingstreet1),''),NULLIF(TRIM(mailingstreet2),''),NULLIF(TRIM(mailingcity),''),NULLIF(TRIM(mailingstate),''),NULLIF(TRIM(mailingzip),''),
							NULLIF(TRIM(mailingcountry),'')
							)))
					<> 
					
                        md5(UPPER(concat_ws('|', 
							COALESCE(var_firstname,NULLIF(TRIM(firstname),'')),COALESCE(var_lastname,NULLIF(TRIM(lastname),'')),COALESCE(var_middlename,NULLIF(TRIM(middlename),'')),COALESCE(var_ssn,NULLIF(TRIM(ssn),'')),COALESCE(var_dob,NULLIF(TRIM(dob),'')),COALESCE(
							var_email1,NULLIF(TRIM(email1),'')),COALESCE(var_email2,NULLIF(TRIM(email2),'')),COALESCE( var_homephone,NULLIF(TRIM(homephone),'')),COALESCE( var_mobilephone,NULLIF(TRIM(mobilephone),'')),COALESCE( var_language,NULLIF(TRIM(language),'')),COALESCE( 
							var_physicaladdress,NULLIF(TRIM(physicaladdress),'')),COALESCE( var_mailingaddress,NULLIF(TRIM(mailingaddress),'')),COALESCE( var_ahcas_eligible,ahcas_eligible),COALESCE(var_cdwaid,cdwaid),COALESCE(var_dshsid,dshsid),COALESCE( 
							var_mailingstreet1,NULLIF(TRIM(mailingstreet1),'')),COALESCE(var_mailingstreet2,NULLIF(TRIM(mailingstreet2),'')),COALESCE( var_mailingcity,NULLIF(TRIM(mailingcity),'')),COALESCE(var_mailingstate,NULLIF(TRIM(mailingstate),'')),COALESCE(var_mailingzip,NULLIF(TRIM(mailingzip),'')),COALESCE( 
							var_mailingcountry,NULLIF(TRIM(mailingcountry),''))
							)))
					)

					;

                RAISE NOTICE 'update with matching personid in personhistory';

                UPDATE staging.personhistory ph
                        SET personid = var_personid::BIGINT,
                        recordmodifieddate= delta_timestamp_to
                        WHERE ph.sourcekey = var_sourcekey
                        AND   ph.personid IS NULL
						AND (ph.personid IS NULL OR ( COALESCE( personid,0 ) <> COALESCE( var_personid::BIGINT, 0) ) );
                       
                RAISE NOTICE 'update with matching personid in employmentrelationshiphistory';

               UPDATE staging.employmentrelationshiphistory erh
                      SET personid = var_personid,
                          recordmodifieddate= delta_timestamp_to
                      WHERE erh.source = var_sourcekey --var_esource
                      AND   erh.personid IS NULL
					  AND ( erh.personid IS NULL or ( COALESCE( erh.personid,0) <> COALESCE( var_personid, 0) ) );
                    
                RAISE NOTICE 'update with matching personid in prod.employmentrelationship';

                UPDATE prod.employmentrelationship per
                       SET personid = var_personid,
                           recordmodifieddate= delta_timestamp_to
                      WHERE per.source = var_sourcekey --var_esource
                      AND   per.personid IS NULL
					  AND   ( per.personid IS NULL OR ( COALESCE(per.personid,0) <> COALESCE(var_personid, 0) ) );

                        IF var_cdwaid is not NULL and var_dshsid is not null THEN
            
                            UPDATE staging.idcrosswalk
                                SET personid = var_personid, 
									recordmodifieddate = delta_timestamp_to
                            WHERE cdwaid = var_cdwaid and dshsid = var_dshsid
								AND ( personid IS NULL OR (COALESCE(personid,0) <> COALESCE(var_personid,0) ) );
                    
                        ELSIF var_dshsid is not NULL THEN

                            UPDATE staging.idcrosswalk
                                SET personid = var_personid, recordmodifieddate = delta_timestamp_to
                            WHERE dshsid = var_dshsid 
								AND ( personid IS NULL OR (COALESCE(personid,0) <> COALESCE(var_personid,0) ) );

                        ELSIF var_cdwaid is not NULL THEN

                            UPDATE staging.idcrosswalk
                                SET personid = var_personid, recordmodifieddate = delta_timestamp_to
                            WHERE cdwaid = var_cdwaid AND ( personid IS NULL OR (COALESCE(personid,0) <> COALESCE(var_personid,0) ) );

                        END IF;
                
            ELSE

                RAISE NOTICE 'No match, starting quarantine.';
                RAISE NOTICE 'Matching quarantine. %, %, %, %, %, %, %, %, %, %', upper(var_firstname), upper(var_lastname), var_ssn, var_dob, var_homephone, var_mobilephone, var_email1, var_email2, var_mailingaddress, var_mailingzip;

                var_puid := staging.fn_checkquarantineperson(upper(var_firstname), upper(var_lastname), var_ssn, var_dob, var_homephone, var_mobilephone, var_email1, var_email2, var_mailingaddress, var_mailingzip, var_dshsid);

                IF var_puid is not null THEN

                    RAISE NOTICE 'Found Quarantine Match, updating, %', var_sourcekey;                

                    RAISE NOTICE 'update with matched serial in personquarantine, %', var_puid;

                    UPDATE staging.personquarantine pq

                        SET 

                            firstname= TRIM(COALESCE(upper(var_firstname),firstname)),

                            lastname= TRIM(COALESCE(upper(var_lastname),lastname)),

                            middlename= TRIM(COALESCE(upper(var_middlename),middlename)),

                            ssn= TRIM(COALESCE(var_ssn,ssn)),

                            email1= TRIM(COALESCE(var_email1,email1)),

                            email2= TRIM(COALESCE(var_email2,email2)),

                            homephone= TRIM(COALESCE(var_homephone,homephone)),

                            mobilephone= TRIM(COALESCE(var_mobilephone,mobilephone)),

                            language= TRIM(COALESCE(var_language,language)),

                            physicaladdress= TRIM(COALESCE(var_physicaladdress,physicaladdress)),

                            mailingaddress= TRIM(COALESCE(var_mailingaddress,mailingaddress)),

                            ahcas_eligible = COALESCE(var_ahcas_eligible,ahcas_eligible),

                           -- status= COALESCE(var_status,status),

                            --exempt= COALESCE(var_exempt,exempt),

                            --type= COALESCE(var_type,type),

                            --workercategory= COALESCE(var_workercategory,workercategory),

                            --credentialnumber= COALESCE(var_credentialnumber,credentialnumber),

                            cdwaid= COALESCE(var_cdwaid,cdwaid),

                            dshsid= COALESCE(var_dshsid,dshsid),

                            --categorycode= COALESCE(var_categorycode,categorycode),

                            --iscarinaeligible= COALESCE(var_iscarinaeligible,iscarinaeligible),

                            dob= TRIM(COALESCE(var_dob,dob)),

                           -- hiredate= COALESCE(var_hiredate,hiredate),

                            --trackingdate= COALESCE(var_trackingdate,trackingdate),

                            mailingstreet1= TRIM(COALESCE(var_mailingstreet1,mailingstreet1)),

                            mailingstreet2= TRIM(COALESCE(var_mailingstreet2,mailingstreet2)),

                            mailingcity= TRIM(COALESCE(var_mailingcity,mailingcity)),

                            mailingstate= TRIM(COALESCE(var_mailingstate,mailingstate)),

                            mailingzip= TRIM(COALESCE(var_mailingzip,mailingzip)),

                            mailingcountry= TRIM(COALESCE(var_mailingcountry,mailingcountry)),

                            recordmodifieddate= delta_timestamp_to,
                            
                                     matched_sourcekeys= CASE 
                                            WHEN pq.matched_sourcekeys is NULL THEN CONCAT(var_sourcekey,';')
                                            WHEN pq.matched_sourcekeys like CONCAT('%',var_sourcekey,'%')::text THEN pq.matched_sourcekeys
                                            ELSE CONCAT(matched_sourcekeys,var_sourcekey,';')
                                            END

                        WHERE pq.person_unique_id = var_puid
						AND 
						(
							md5(UPPER(
								concat_ws('|',NULLIF(TRIM(firstname),''),NULLIF(TRIM(lastname),''),NULLIF(TRIM(middlename),''),NULLIF(TRIM(ssn),''),NULLIF(TRIM(dob),''),
								NULLIF(TRIM(email1),''),NULLIF(TRIM(email2),''),NULLIF(TRIM(homephone),''),NULLIF(TRIM(mobilephone),''),NULLIF(TRIM(language),''),
								NULLIF(TRIM(physicaladdress),''),NULLIF(TRIM(mailingaddress),''),ahcas_eligible,cdwaid,dshsid,
								NULLIF(TRIM(mailingstreet1),''),NULLIF(TRIM(mailingstreet2),''),NULLIF(TRIM(mailingcity),''),NULLIF(TRIM(mailingstate),''),NULLIF(TRIM(mailingzip),''),
								NULLIF(TRIM(mailingcountry),''),NULLIF(TRIM(matched_sourcekeys),'')
										 ) 
							   ))
						)
						<> 
						(
							md5(UPPER(
								concat_ws('|', COALESCE(var_firstname,NULLIF(TRIM(firstname),'')),COALESCE(var_lastname,NULLIF(TRIM(lastname),'')),COALESCE(var_middlename,NULLIF(TRIM(middlename),'')),COALESCE(var_ssn,NULLIF(TRIM(ssn),'')),COALESCE(var_dob,NULLIF(TRIM(dob),'')),
								COALESCE(var_email1,NULLIF(TRIM(email1),'')),COALESCE(var_email2,NULLIF(TRIM(email2),'')),COALESCE( var_homephone,NULLIF(TRIM(homephone),'')),COALESCE( var_mobilephone,NULLIF(TRIM(mobilephone),'')),COALESCE( var_language,NULLIF(TRIM(language),'')),
								COALESCE(var_physicaladdress,NULLIF(TRIM(physicaladdress),'')),COALESCE( var_mailingaddress,NULLIF(TRIM(mailingaddress),'')),COALESCE( var_ahcas_eligible,ahcas_eligible),COALESCE(var_cdwaid,cdwaid),COALESCE(var_dshsid,dshsid),
								COALESCE(var_mailingstreet1,NULLIF(TRIM(mailingstreet1),'')),COALESCE(var_mailingstreet2,NULLIF(TRIM(mailingstreet2),'')),COALESCE( var_mailingcity,NULLIF(TRIM(mailingcity),'')),COALESCE(var_mailingstate,NULLIF(TRIM(mailingstate),'')),COALESCE(var_mailingzip,NULLIF(TRIM(mailingzip),'')),
								COALESCE(var_mailingcountry,NULLIF(TRIM(mailingcountry),'')),COALESCE(var_sourcekey,NULLIF(TRIM(matched_sourcekeys),''))
										 )
								))
						)
						
						;

                ELSE
                    RAISE NOTICE 'No Quarantine Match, inserting, %', var_sourcekey;
                    RAISE NOTICE 'check matched sourcekey (should be null), %', var_puid;
                    RAISE NOTICE 'Inserting to staging.personquarantine with sourcekey';

                    --RAISE NOTICE '% assigned to % with employeeid %',var_personid,upper(var_firstname),var_employeeid;

                    INSERT INTO staging.personquarantine(firstname, lastname, middlename, ssn, email1, email2, homephone, mobilephone, language, physicaladdress,

                    mailingaddress, ahcas_eligible, exempt, cdwaid, dshsid,dob, recordmodifieddate, recordcreateddate, sourcekey, mailingstreet1, mailingstreet2, mailingcity, 

                    mailingstate, mailingzip, mailingcountry, matched_sourcekeys)

                    VALUES (upper(var_firstname), upper(var_lastname), upper(var_middlename), var_ssn, var_email1, var_email2, var_homephone, var_mobilephone, var_language,

                    var_physicaladdress, var_mailingaddress, var_ahcas_eligible, 'false',var_cdwaid, var_dshsid, var_dob, delta_timestamp_to, delta_timestamp_to, var_sourcekey, var_mailingstreet1, var_mailingstreet2, var_mailingcity, var_mailingstate, 

                    var_mailingzip, var_mailingcountry, CONCAT(var_sourcekey,';'));

                END IF;

            END IF; 

    END LOOP;

    CLOSE cur_icd12; 
    
    UPDATE staging.personquarantine pq
    SET studentid = rc.studentid,
    recordmodifieddate = delta_timestamp_to
    from raw.credential rc 
    WHERE concat('CRED-',rc.credentialnumber) = pq.sourcekey
    and pq.studentid is null 
	AND ( pq.studentid IS NULL OR ( COALESCE( pq.studentid,0) <> COALESCE( rc.studentid, 0) ) );
    
    INSERT INTO logs.lastprocessed(processname, lastprocesseddate, success)
    VALUES ('proc-personmastering',delta_timestamp_to, '1');
    
    RAISE NOTICE 'Finish Execution %', NOW();

END;
$BODY$;
