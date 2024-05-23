-- Table: prod.migration_dohclassified

-- DROP TABLE IF EXISTS prod.migration_dohclassified;

CREATE TABLE IF NOT EXISTS prod.migration_dohclassified
(
    id integer,
    filelastname character varying(255) COLLATE pg_catalog."default",
    filefirstname character varying(255) COLLATE pg_catalog."default",
    filereceiveddate date,
    dohname character varying(255) COLLATE pg_catalog."default",
    credentialnumber character varying(255) COLLATE pg_catalog."default",
    credentialstatus character varying(255) COLLATE pg_catalog."default",
    applicationdate date,
    datedshsbenefitpaymentudfupdated date,
    classifieddate date,
    appfeepaid character varying(255) COLLATE pg_catalog."default",
    reconciled date,
    reconnotes character varying(255) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.migration_dohclassified
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.migration_dohclassified TO PUBLIC;

GRANT ALL ON TABLE prod.migration_dohclassified TO cicd_pipeline;

GRANT INSERT ON TABLE prod.migration_dohclassified TO readonly_testing;

GRANT ALL ON TABLE prod.migration_dohclassified TO system_pipeline;