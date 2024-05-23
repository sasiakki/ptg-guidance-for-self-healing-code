-- Table: raw.employeehours

-- DROP TABLE IF EXISTS "raw".employeehours;

CREATE TABLE IF NOT EXISTS "raw".employeehours
(
    employeeid character varying COLLATE pg_catalog."default",
    personid character varying COLLATE pg_catalog."default",
    firstname character varying COLLATE pg_catalog."default",
    middlename character varying COLLATE pg_catalog."default",
    lastname character varying COLLATE pg_catalog."default",
    ssn character varying COLLATE pg_catalog."default",
    workmonth character varying COLLATE pg_catalog."default",
    hours character varying COLLATE pg_catalog."default",
    cchindicator character varying COLLATE pg_catalog."default",
    dphindicator character varying COLLATE pg_catalog."default",
    servicecode character varying COLLATE pg_catalog."default",
    servicecodemodifier character varying COLLATE pg_catalog."default",
    servicecodedescription character varying COLLATE pg_catalog."default",
    tier1 character varying COLLATE pg_catalog."default",
    tier2 character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filemodifieddate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".employeehours
    OWNER to cicd_pipeline;

GRANT UPDATE, INSERT, SELECT, DELETE ON TABLE "raw".employeehours TO anveeraprasad;

GRANT ALL ON TABLE "raw".employeehours TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".employeehours TO lizawu;

GRANT SELECT ON TABLE "raw".employeehours TO readonly_testing;

GRANT ALL ON TABLE "raw".employeehours TO system_pipeline;