-- Table: raw.qualtricstrainingtransfers

-- DROP TABLE IF EXISTS "raw".qualtricstrainingtransfers;

CREATE TABLE IF NOT EXISTS "raw".qualtricstrainingtransfers
(
    startdate timestamp without time zone,
    enddate timestamp without time zone,
    status character varying COLLATE pg_catalog."default",
    ipaddress character varying COLLATE pg_catalog."default",
    progress character varying COLLATE pg_catalog."default",
    duration_in_seconds character varying COLLATE pg_catalog."default",
    finished character varying COLLATE pg_catalog."default",
    recordeddate timestamp without time zone,
    responseid character varying COLLATE pg_catalog."default",
    recipientlastname character varying COLLATE pg_catalog."default",
    recipientfirstname character varying COLLATE pg_catalog."default",
    recipientemail character varying COLLATE pg_catalog."default",
    externalreference character varying COLLATE pg_catalog."default",
    locationlatitude character varying COLLATE pg_catalog."default",
    locationlongitude character varying COLLATE pg_catalog."default",
    distributionchannel character varying COLLATE pg_catalog."default",
    userlanguage character varying COLLATE pg_catalog."default",
    personid bigint,
    course_name character varying COLLATE pg_catalog."default",
    reasonfortransfer character varying COLLATE pg_catalog."default",
    continuing_education_information_1 character varying COLLATE pg_catalog."default",
    continuing_education_information_2 character varying COLLATE pg_catalog."default",
    completed_date character varying COLLATE pg_catalog."default",
    trainingentity_retired character varying COLLATE pg_catalog."default",
    trainingentity character varying COLLATE pg_catalog."default",
    credithours character varying COLLATE pg_catalog."default",
    employer character varying COLLATE pg_catalog."default",
    employerstaff character varying COLLATE pg_catalog."default",
    non_seiu character varying COLLATE pg_catalog."default",
    additional_comments character varying COLLATE pg_catalog."default",
    form_completed_date character varying COLLATE pg_catalog."default",
    filemodifieddate timestamp without time zone,
    filename character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    isdelta boolean
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".qualtricstrainingtransfers
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".qualtricstrainingtransfers TO PUBLIC;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".qualtricstrainingtransfers TO anveeraprasad;

GRANT ALL ON TABLE "raw".qualtricstrainingtransfers TO cicd_pipeline;

GRANT INSERT, SELECT ON TABLE "raw".qualtricstrainingtransfers TO readonly_testing;

GRANT ALL ON TABLE "raw".qualtricstrainingtransfers TO system_pipeline;