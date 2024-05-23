-- Table: raw.cdwatransitionreports

-- DROP TABLE IF EXISTS "raw".cdwatransitionreports;

CREATE TABLE IF NOT EXISTS "raw".cdwatransitionreports
(
    providerone_id character varying(20) COLLATE pg_catalog."default",
    workdayid character varying COLLATE pg_catalog."default",
    personid character varying COLLATE pg_catalog."default",
    category character varying COLLATE pg_catalog."default",
    subcategory character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default",
    ssn character varying COLLATE pg_catalog."default",
    hiredate character varying COLLATE pg_catalog."default",
    birthdate character varying COLLATE pg_catalog."default",
    ipname character varying COLLATE pg_catalog."default",
    firstname character varying COLLATE pg_catalog."default",
    middlename character varying COLLATE pg_catalog."default",
    lastname character varying COLLATE pg_catalog."default",
    email character varying COLLATE pg_catalog."default",
    homephone character varying COLLATE pg_catalog."default",
    cellphone character varying COLLATE pg_catalog."default",
    addresstype character varying COLLATE pg_catalog."default",
    addressline1 character varying COLLATE pg_catalog."default",
    addressline2 character varying COLLATE pg_catalog."default",
    city character varying COLLATE pg_catalog."default",
    state character varying COLLATE pg_catalog."default",
    zipcode character varying COLLATE pg_catalog."default",
    preferredlanguage character varying COLLATE pg_catalog."default",
    recommendedpreferredlanguage character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    filedate timestamp without time zone,
    dateuploaded timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".cdwatransitionreports
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".cdwatransitionreports TO PUBLIC;

GRANT DELETE, UPDATE, INSERT, SELECT ON TABLE "raw".cdwatransitionreports TO anveeraprasad;

GRANT ALL ON TABLE "raw".cdwatransitionreports TO cicd_pipeline;

GRANT INSERT ON TABLE "raw".cdwatransitionreports TO readonly_testing;

GRANT ALL ON TABLE "raw".cdwatransitionreports TO system_pipeline;