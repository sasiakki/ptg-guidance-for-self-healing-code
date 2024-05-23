-- Table: raw.dohclassified

-- DROP TABLE IF EXISTS "raw".dohclassified;

CREATE TABLE IF NOT EXISTS "raw".dohclassified
(
    filelastname character varying(255) COLLATE pg_catalog."default",
    filefirstname character varying(255) COLLATE pg_catalog."default",
    filereceiveddate character varying(255) COLLATE pg_catalog."default",
    dohname character varying(255) COLLATE pg_catalog."default",
    credentialnumber character varying(255) COLLATE pg_catalog."default",
    credentialstatus character varying(255) COLLATE pg_catalog."default",
    applicationdate character varying(255) COLLATE pg_catalog."default",
    datedshsbenefitpaymentudfupdated character varying(255) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filename character varying(100) COLLATE pg_catalog."default",
    filedate timestamp without time zone,
    appfeepaid character varying(1000) COLLATE pg_catalog."default",
    reconciled character varying(1000) COLLATE pg_catalog."default",
    reconnotes character varying(1000) COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".dohclassified
    OWNER to cicd_pipeline;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "raw".dohclassified TO anveeraprasad;

GRANT ALL ON TABLE "raw".dohclassified TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".dohclassified TO readonly_testing;

GRANT ALL ON TABLE "raw".dohclassified TO system_pipeline;