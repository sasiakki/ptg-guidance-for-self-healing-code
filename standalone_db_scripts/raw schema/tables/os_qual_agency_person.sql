-- Table: raw.os_qual_agency_person

-- DROP TABLE IF EXISTS "raw".os_qual_agency_person;

CREATE TABLE IF NOT EXISTS "raw".os_qual_agency_person
(
    startdate character varying(1000) COLLATE pg_catalog."default",
    enddate character varying(1000) COLLATE pg_catalog."default",
    status character varying(1000) COLLATE pg_catalog."default",
    ipaddress character varying(1000) COLLATE pg_catalog."default",
    progress character varying(1000) COLLATE pg_catalog."default",
    duration_in_seconds character varying(1000) COLLATE pg_catalog."default",
    finished character varying(1000) COLLATE pg_catalog."default",
    recordeddate character varying(1000) COLLATE pg_catalog."default",
    responseid character varying(1000) COLLATE pg_catalog."default",
    recipientlastname character varying(1000) COLLATE pg_catalog."default",
    recipientfirstname character varying(1000) COLLATE pg_catalog."default",
    recipientemail character varying(1000) COLLATE pg_catalog."default",
    externalreference character varying(1000) COLLATE pg_catalog."default",
    locationlatitude character varying(1000) COLLATE pg_catalog."default",
    locationlongitude character varying(1000) COLLATE pg_catalog."default",
    distributionchannel character varying(1000) COLLATE pg_catalog."default",
    userlanguage character varying(1000) COLLATE pg_catalog."default",
    q_recaptchascore character varying(1000) COLLATE pg_catalog."default",
    agency_firstname character varying(1000) COLLATE pg_catalog."default",
    agency_lastname character varying(1000) COLLATE pg_catalog."default",
    agency_email character varying(1000) COLLATE pg_catalog."default",
    employername character varying(1000) COLLATE pg_catalog."default",
    person_firstname character varying COLLATE pg_catalog."default",
    person_lastname character varying(1000) COLLATE pg_catalog."default",
    person_dob character varying(1000) COLLATE pg_catalog."default",
    person_phone character varying(1000) COLLATE pg_catalog."default",
    person_id character varying(1000) COLLATE pg_catalog."default",
    os_completion_date character varying(1000) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filename character varying COLLATE pg_catalog."default",
    filemodifieddate timestamp without time zone,
    isdelta boolean NOT NULL DEFAULT false
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".os_qual_agency_person
    OWNER to cicd_pipeline;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "raw".os_qual_agency_person TO anveeraprasad;

GRANT ALL ON TABLE "raw".os_qual_agency_person TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".os_qual_agency_person TO cukaumunna;

GRANT SELECT ON TABLE "raw".os_qual_agency_person TO eblythe;

GRANT SELECT ON TABLE "raw".os_qual_agency_person TO htata;

GRANT SELECT ON TABLE "raw".os_qual_agency_person TO lizawu;

GRANT SELECT ON TABLE "raw".os_qual_agency_person TO readonly_testing;

GRANT ALL ON TABLE "raw".os_qual_agency_person TO system_pipeline;