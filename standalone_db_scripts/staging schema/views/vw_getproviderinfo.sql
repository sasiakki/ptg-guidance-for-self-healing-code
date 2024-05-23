CREATE OR REPLACE VIEW staging.vw_getproviderinfo
AS 
 SELECT cdwap.employee_id,
    ( SELECT DISTINCT employertrust.employerid::numeric AS employerid
           FROM prod.employertrust
          WHERE employertrust.name::text = 'CDWA (IP)'::text AND employertrust.trust::text = 'TP'::text) AS employerid,
        CASE
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Standard HCA'::text THEN 1
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Adult Child Provider'::text THEN 2
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Limited Service Provider'::text THEN 3
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Family Provider'::text THEN 4
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Respite Provider'::text THEN 5
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'DD Parent Provider'::text THEN 6
            WHEN (cdwap.employee_classification IS NULL OR cdwap.employee_classification::text = ''::text OR cdwap.employee_classification::text = 'Orientation & Safety'::text) AND cdwap.hire_date IS NOT NULL AND cdwap.hire_date <> 19000101 AND length(cdwap.hire_date::text) = 8 THEN 99
            ELSE NULL::integer
        END AS priority,
        CASE
            WHEN cdwap.termination_date IS NOT NULL AND cdwap.termination_date <> 19000101 AND length(cdwap.termination_date::text) = 8 THEN 'Terminated'::text
            ELSE 'Active'::text
        END AS empstatus,
        CASE
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Standard HCA'::text THEN 'SHCA'::text
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Adult Child Provider'::text THEN 'ADCH'::text
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Limited Service Provider'::text THEN 'LSPR'::text
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Family Provider'::text THEN 'FAPR'::text
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Respite Provider'::text THEN 'RESP'::text
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'DD Parent Provider'::text THEN 'DDPP'::text
            WHEN (cdwap.employee_classification IS NULL OR cdwap.employee_classification::text = ''::text OR cdwap.employee_classification::text = 'Orientation & Safety'::text) AND cdwap.hire_date IS NOT NULL THEN 'OSAF'::text
            ELSE NULL::text
        END AS classificationcode,
        CASE
            WHEN cdwap.classification_start_date IS NOT NULL AND cdwap.classification_start_date <> 19000101 AND length(cdwap.classification_start_date::text) = 8 THEN to_date(cdwap.classification_start_date::text, 'YYYYMMDD'::text)
            ELSE NULL::date
        END AS initialtrackingdate,
        CASE
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Adult Child Provider'::text THEN 'Adult Child'::character varying
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Parent Provider'::text THEN NULL
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'Respite Provider'::text THEN 'Respite'::character varying
            WHEN cdwap.employee_classification IS NOT NULL AND cdwap.employee_classification::text = 'DD Parent Provider'::text THEN 'Parent Provider DDD'::character varying
            WHEN (cdwap.employee_classification IS NULL OR cdwap.employee_classification::text = ''::text OR cdwap.employee_classification::text = 'Orientation & Safety'::text) AND cdwap.hire_date IS NOT NULL AND cdwap.hire_date <> 19000101 AND length(cdwap.hire_date::text) = 8 THEN 'Orientation & Safety'::character varying
            ELSE cdwap.employee_classification
        END AS employee_classification,
        CASE
            WHEN cdwap.authorized_start_date IS NOT NULL AND cdwap.authorized_start_date <> 19000101 AND length(cdwap.authorized_start_date::text) = 8 THEN to_date(cdwap.authorized_start_date::text, 'YYYYMMDD'::text)::timestamp without time zone
            ELSE NULL::timestamp without time zone
        END AS authorized_start_date,
        CASE
            WHEN cdwap.authorized_end_date IS NOT NULL AND cdwap.authorized_end_date <> 19000101 AND length(cdwap.authorized_end_date::text) = 8 THEN to_date(cdwap.authorized_end_date::text, 'YYYYMMDD'::text)::timestamp without time zone
            ELSE NULL::timestamp without time zone
        END AS authorized_end_date,
        CASE
            WHEN cdwap.classification_start_date IS NOT NULL AND cdwap.classification_start_date <> 19000101 AND length(cdwap.classification_start_date::text) = 8 THEN to_date(cdwap.classification_start_date::text, 'YYYYMMDD'::text)::timestamp without time zone
            ELSE NULL::timestamp without time zone
        END AS classification_start_date,
        CASE
            WHEN cdwap.termination_date IS NOT NULL AND cdwap.termination_date <> 19000101 AND length(cdwap.termination_date::text) = 8 THEN to_date(cdwap.termination_date::text, 'YYYYMMDD'::text)::timestamp without time zone
            ELSE NULL::timestamp without time zone
        END AS termination_date,
        CASE
            WHEN cdwap.os_completed IS NOT NULL AND cdwap.os_completed <> 19000101 AND length(cdwap.os_completed::text) = 8 THEN to_date(cdwap.os_completed::text, 'YYYYMMDD'::text)
            ELSE NULL::date
        END AS os_completed,
    cdwap.client_relationship AS relationship,
    cdwap.personid AS person_id,
        CASE
            WHEN cdwap.hire_date IS NOT NULL AND cdwap.hire_date <> 19000101 AND length(cdwap.hire_date::text) = 8 THEN to_date(cdwap.hire_date::text, 'YYYYMMDD'::text)
            ELSE NULL::date
        END AS hire_date,
    'CDWA-'::text || cdwap.personid::text AS sourcekey,
    cdwap.filemodifieddate AS filedate,
    cdwap.filename
   FROM raw.cdwa cdwap
  WHERE cdwap.employee_id IS NOT NULL
AND   cdwap.isvalid = TRUE
AND   cdwap.filemodifieddate > (SELECT CASE
                                        WHEN MAX(lastprocesseddate) IS NULL THEN (CURRENT_DATE -1)
                                        ELSE MAX(lastprocesseddate)
                                      END AS MAXPROCESSDATE
                               FROM logs.lastprocessed
                               WHERE processname = 'glue-cdwa-providerinfo-employmentrelationship-process'
                               AND   success = '1')
ORDER BY cdwap.termination_date, cdwap.hire_date, cdwap.employee_id;
