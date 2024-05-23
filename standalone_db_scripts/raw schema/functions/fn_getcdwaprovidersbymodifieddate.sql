-- FUNCTION: raw.fn_getcdwaprovidersbymodifieddate(boolean)

-- DROP FUNCTION IF EXISTS "raw".fn_getcdwaprovidersbymodifieddate(boolean);

CREATE OR REPLACE FUNCTION "raw".fn_getcdwaprovidersbymodifieddate(
	in_is_valid boolean DEFAULT false)
    RETURNS TABLE(employeeid numeric, personid character varying, firstname character varying, middlename character varying, lastname character varying, ssn character varying, dob integer, gender character varying, ethnicity character varying, race character varying, language character varying, maritalstatus character varying, phone1 numeric, phone2 numeric, email character varying, mailingadd1 character varying, mailingadd2 character varying, mailingcity character varying, mailingstate character varying, mailingzip character varying, physicaladd1 character varying, physicaladd2 character varying, physicalcity character varying, physicalstate character varying, physicalzip character varying, employeeclassification character varying, exemptstatus character varying, backgroundcheckdate integer, iedate integer, hiredate integer, classificationstartdate integer, carinaeligible character varying, ahcaseligible character varying, oscompleteddate integer, terminationdate integer, authorizedstartdate integer, authorizedenddate integer, clientcount numeric, clientrelationship character varying, clientid character varying, filename character varying, modifieddate timestamp with time zone, employerid integer, priority integer, classificationcode character varying, isvalid boolean, error_message character varying, filemodifieddate date) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$

BEGIN
RETURN query
SELECT provider.employee_id as employeeid,
       provider.personid,
       provider.first_name as firstname,
       provider.middle_name as middlename,
       provider.last_name as lastname,
       provider.ssn,
       provider.dob,
       provider.gender,
       provider.ethnicity,
       provider.race,
       provider.language,
       provider.marital_status as maritalstatus,
       provider.phone_1 as phone1,
       provider.phone_2 as phone2,
       provider.email,
       provider.mailing_add_1 as mailingadd1,
       provider.mailing_add_2 as mailingadd2,
       --provider.mailingadd3,
       provider.mailing_city as mailingcity,
       provider.mailing_state as mailingstate,
       provider.mailing_zip as mailingzip,
       provider.physical_add_1 as physicaladd1,
       provider.physical_add_2 as physicaladd2,
       --provider.physical_add_3,
       provider.physical_city as physicalcity,
       provider.physical_state as physicalstate,
       provider.physical_zip as physicalzip,
       CASE
         WHEN (provider.employee_classification IS NULL OR provider.employee_classification::TEXT = ''::TEXT) AND provider.hire_date IS NOT NULL AND provider.hire_date <> 19000101 AND LENGTH(provider.hire_date::TEXT) = 8 THEN 'Orientation & Safety'::CHARACTER VARYING
         ELSE provider.employee_classification
       END AS employeeclassification,
       provider.exempt_status as exemptstatus,
       provider.background_check_date as backgroundcheckdate,
       provider.ie_date as iedate,
       provider.hire_date as hiredate,
       provider.classification_start_date as classificationstartdate,
       provider.carina_eligible as carinaeligible,
       provider.ahcas_eligible as ahcaseligible,
       provider.os_completed as oscompleteddate,
       provider.termination_date as terminationdate,
       provider.authorized_start_date as authorizedstartdate,
       provider.authorized_end_date as authorizedenddate,
       provider.client_count as clientcount,
       provider.client_relationship as clientrelationship,
       provider.client_id as clientid,
       provider.filename,
       --TO_TIMESTAMP(provider.dateuploaded::text, 'YYYY-MM-DD HH24:MI:SS') as dateuploaded,
       TO_TIMESTAMP(provider.recordmodifieddate::text, 'YYYY-MM-DD HH24:MI:SS') as modifieddate,
       (SELECT employertrust.employerid
        FROM prod.employertrust
        WHERE employertrust.name::TEXT = 'CDWA (IP)'::TEXT
        AND   employertrust.trust::TEXT = 'TP'::TEXT)
        --AND   employertrust.sourcename::TEXT = 'CDWA'::TEXT)
		AS employerid,
       CASE
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Standard HCA'::TEXT THEN 1
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Adult Child Provider'::TEXT THEN 2
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Limited Service Provider'::TEXT THEN 3
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Family Provider'::TEXT THEN 4
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Respite Provider'::TEXT THEN 5
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'DD Parent Provider'::TEXT THEN 6
         WHEN (provider.employee_classification IS NULL OR provider.employee_classification::TEXT = ''::TEXT) AND provider.hire_date IS NOT NULL AND provider.hire_date <> 19000101 AND LENGTH(provider.hire_date::TEXT) = 8 THEN 99
         ELSE NULL::INTEGER
       END AS priority,
       CASE
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Standard HCA'::TEXT THEN 'SHCA'::varchar
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Adult Child Provider'::TEXT THEN 'ADCH'::varchar
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Limited Service Provider'::TEXT THEN 'LSPR'::varchar
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Family Provider'::TEXT THEN 'FAPR'::varchar
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'Respite Provider'::TEXT THEN 'RESP'::varchar
         WHEN provider.employee_classification IS NOT NULL AND provider.employee_classification::TEXT = 'DD Parent Provider'::TEXT THEN 'DDPP'::varchar
         WHEN (provider.employee_classification IS NULL OR provider.employee_classification::TEXT = ''::TEXT) AND provider.hire_date IS NOT NULL 
         AND provider.hire_date <> 19000101 AND LENGTH(provider.hire_date::TEXT) = 8 THEN 'OSAF'::varchar
         ELSE NULL::varchar
       END AS classificationcode,
       provider.isvalid,
       provider.error_message,
       provider.filemodifieddate
FROM raw.cdwa provider
WHERE provider.isvalid = in_is_valid
AND   provider.filemodifieddate > (SELECT CASE
                                            WHEN MAX(lastprocesseddate) IS NULL THEN (CURRENT_DATE -1)
                                            ELSE MAX(lastprocesseddate)
                                          END AS MAXPROCESSDATE
                                   FROM logs.lastprocessed
                                   WHERE processname = 'glue-cdwa-validation'
                                   AND   success = '1')

ORDER BY provider.employee_id,provider.personid;
END;
$BODY$;

