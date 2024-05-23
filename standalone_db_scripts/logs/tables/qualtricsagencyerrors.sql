-- Table: logs.qualtricsagencyerrors

-- DROP TABLE IF EXISTS logs.qualtricsagencyerrors;

CREATE TABLE IF NOT EXISTS logs.qualtricsagencyerrors
(
    id bigint NOT NULL DEFAULT nextval('logs.qualtricsagencyerrors_id_seq'::regclass),
    startdate character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    enddate character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    status character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    ipaddress character varying(1000) COLLATE pg_catalog."default",
    progress character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    duration_in_seconds character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    finished character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    recordeddate character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    responseid character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    recipientlastname character varying(1000) COLLATE pg_catalog."default",
    recipientfirstname character varying(1000) COLLATE pg_catalog."default",
    recipientemail character varying(1000) COLLATE pg_catalog."default",
    externalreference character varying(1000) COLLATE pg_catalog."default",
    locationlatitude character varying(1000) COLLATE pg_catalog."default",
    locationlongitude character varying(1000) COLLATE pg_catalog."default",
    distributionchannel character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    userlanguage character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    q_recaptchascore character varying(1000) COLLATE pg_catalog."default",
    person_emp_status character varying(1000) COLLATE pg_catalog."default",
    agency_firstname character varying(1000) COLLATE pg_catalog."default",
    agency_lastname character varying(1000) COLLATE pg_catalog."default",
    agency_email character varying(1000) COLLATE pg_catalog."default",
    agency_phone character varying(1000) COLLATE pg_catalog."default",
    employername character varying(1000) COLLATE pg_catalog."default",
    terminated_person_firstname character varying(1000) COLLATE pg_catalog."default",
    terminated_person_middlename character varying(1000) COLLATE pg_catalog."default",
    terminated_person_lastname character varying(1000) COLLATE pg_catalog."default",
    terminated_person_dob character varying(1000) COLLATE pg_catalog."default",
    terminated_person_ssn character varying(1000) COLLATE pg_catalog."default",
    terminated_person_id character varying(1000) COLLATE pg_catalog."default",
    terminated_person_phone character varying(1000) COLLATE pg_catalog."default",
    terminated_person_email character varying(1000) COLLATE pg_catalog."default",
    terminated_person_street character varying(1000) COLLATE pg_catalog."default",
    terminated_person_city character varying(1000) COLLATE pg_catalog."default",
    terminated_person_state character varying(1000) COLLATE pg_catalog."default",
    terminated_person_zipcode character varying(1000) COLLATE pg_catalog."default",
    terminated_person_employerbranch character varying(1000) COLLATE pg_catalog."default",
    person_termination_date character varying(1000) COLLATE pg_catalog."default",
    newhire_person_firstname character varying(1000) COLLATE pg_catalog."default",
    newhire_person_middlename character varying(1000) COLLATE pg_catalog."default",
    newhire_person_lastname character varying(1000) COLLATE pg_catalog."default",
    newhire_person_dob character varying(1000) COLLATE pg_catalog."default",
    newhire_person_ssn character varying(1000) COLLATE pg_catalog."default",
    newhire_person_phone1 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_phone2 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_phone3 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_email1 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_email2 character varying(1000) COLLATE pg_catalog."default",
    newhire_person_street character varying(1000) COLLATE pg_catalog."default",
    newhire_person_city character varying(1000) COLLATE pg_catalog."default",
    newhire_person_state character varying(1000) COLLATE pg_catalog."default",
    newhire_person_zipcode character varying(1000) COLLATE pg_catalog."default",
    preferredlanguage character varying(1000) COLLATE pg_catalog."default",
    newhire_personemployerbranch character varying(1000) COLLATE pg_catalog."default",
    person_hire_date character varying(1000) COLLATE pg_catalog."default",
    exempt character varying(1000) COLLATE pg_catalog."default",
    person_workercategory character varying(1000) COLLATE pg_catalog."default",
    cg_status character varying(1000) COLLATE pg_catalog."default",
    error_reason character varying(1000) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    isdelta boolean NOT NULL DEFAULT false,
    filemodifieddate timestamp without time zone,
    filename character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.qualtricsagencyerrors
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.qualtricsagencyerrors TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.qualtricsagencyerrors TO readonly_testing;

GRANT ALL ON TABLE logs.qualtricsagencyerrors TO system_pipeline;