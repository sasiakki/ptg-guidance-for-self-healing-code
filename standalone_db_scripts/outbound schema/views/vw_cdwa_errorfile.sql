-- View: outbound.vw_cdwa_errorfile

-- DROP VIEW outbound.vw_cdwa_errorfile;

CREATE OR REPLACE VIEW outbound.vw_cdwa_errorfile
 AS
 SELECT provider.employee_id AS employeeid,
    provider.personid,
    provider.first_name AS firstname,
    provider.middle_name AS middlename,
    provider.last_name AS lastname,
    provider.ssn,
    provider.dob,
    provider.gender,
    provider.ethnicity,
    provider.race,
    provider.language,
    provider.marital_status AS maritalstatus,
    provider.phone_1 AS phone1,
    provider.phone_2 AS phone2,
    provider.email,
    provider.mailing_add_1 AS mailingadd1,
    provider.mailing_add_2 AS mailingadd2,
    provider.mailing_city AS mailingcity,
    provider.mailing_state AS mailingstate,
    provider.mailing_zip AS mailingzip,
    provider.physical_add_1 AS physicaladd1,
    provider.physical_add_2 AS physicaladd2,
    provider.physical_city AS physicalcity,
    provider.physical_state AS physicalstate,
    provider.physical_zip AS physicalzip,
        CASE
            WHEN provider.employee_classification::text = 'Orientation & Safety'::text THEN ''::character varying
            ELSE provider.employee_classification
        END AS employeeclassification,
    provider.exempt_status AS exemptstatus,
    provider.background_check_date AS backgroundcheckdate,
    provider.ie_date AS iedate,
    provider.hire_date AS hiredate,
    provider.classification_start_date AS classificationstartdate,
    provider.carina_eligible AS carinaeligible,
    provider.ahcas_eligible AS ahcaseligible,
    provider.os_completed AS oscompleteddate,
    provider.termination_date AS terminationdate,
    provider.authorized_start_date AS authorizedstartdate,
    provider.authorized_end_date AS authorizedenddate,
    provider.client_count AS clientcount,
    provider.client_relationship AS clientrelationship,
    provider.client_id AS clientid,
    provider.filename,
    provider.isvalid,
    provider.error_message,
    provider.filemodifieddate
   FROM raw.cdwa provider
  WHERE provider.isvalid = false AND provider.filemodifieddate = (( SELECT max(t2.filemodifieddate) AS max
           FROM raw.cdwa t2))
  ORDER BY provider.employee_id, provider.personid;

