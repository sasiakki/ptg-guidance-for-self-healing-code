-- Table: raw.credential_ospi

-- DROP TABLE IF EXISTS "raw".credential_ospi;

CREATE TABLE IF NOT EXISTS "raw".credential_ospi
(
    personid character varying(50) COLLATE pg_catalog."default",
    employer character varying(50) COLLATE pg_catalog."default",
    firstname character varying(100) COLLATE pg_catalog."default",
    middlename character varying(100) COLLATE pg_catalog."default",
    lastname character varying(100) COLLATE pg_catalog."default",
    birthdate character varying(10) COLLATE pg_catalog."default",
    credentialnumber character varying(50) COLLATE pg_catalog."default",
    credentialtype character varying(20) COLLATE pg_catalog."default",
    credentialstatus character varying(10) COLLATE pg_catalog."default",
    firstissuancedate character varying(10) COLLATE pg_catalog."default",
    expirationdate character varying(10) COLLATE pg_catalog."default",
    filename character varying(100) COLLATE pg_catalog."default",
    filedate character varying(10) COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".credential_ospi
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".credential_ospi TO PUBLIC;

GRANT ALL ON TABLE "raw".credential_ospi TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE "raw".credential_ospi TO readonly_testing;

GRANT ALL ON TABLE "raw".credential_ospi TO system_pipeline;