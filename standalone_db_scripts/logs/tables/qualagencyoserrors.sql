-- Table: logs.qualagencyoserrors

-- DROP TABLE IF EXISTS logs.qualagencyoserrors;

CREATE TABLE IF NOT EXISTS logs.qualagencyoserrors
(
    startdate text COLLATE pg_catalog."default",
    enddate text COLLATE pg_catalog."default",
    status text COLLATE pg_catalog."default",
    ipaddress text COLLATE pg_catalog."default",
    progress text COLLATE pg_catalog."default",
    duration_in_seconds text COLLATE pg_catalog."default",
    recordeddate text COLLATE pg_catalog."default",
    finished text COLLATE pg_catalog."default",
    responseid text COLLATE pg_catalog."default",
    locationlatitude text COLLATE pg_catalog."default",
    locationlongitude text COLLATE pg_catalog."default",
    distributionchannel text COLLATE pg_catalog."default",
    userlanguage text COLLATE pg_catalog."default",
    q_recaptchascore text COLLATE pg_catalog."default",
    agency_firstname text COLLATE pg_catalog."default",
    agency_lastname text COLLATE pg_catalog."default",
    agency_email text COLLATE pg_catalog."default",
    employername text COLLATE pg_catalog."default",
    person_firstname text COLLATE pg_catalog."default",
    person_lastname text COLLATE pg_catalog."default",
    person_dob text COLLATE pg_catalog."default",
    person_phone text COLLATE pg_catalog."default",
    person_id text COLLATE pg_catalog."default",
    os_completion_date text COLLATE pg_catalog."default",
    filename text COLLATE pg_catalog."default",
    filemodifieddate timestamp without time zone,
    error_reason text COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.qualagencyoserrors
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.qualagencyoserrors TO cicd_pipeline;

GRANT SELECT ON TABLE logs.qualagencyoserrors TO readonly_testing;

GRANT ALL ON TABLE logs.qualagencyoserrors TO system_pipeline;