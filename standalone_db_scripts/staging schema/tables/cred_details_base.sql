-- Table: staging.cred_details_base

-- DROP TABLE IF EXISTS staging.cred_details_base;

CREATE TABLE IF NOT EXISTS staging.cred_details_base
(
    credentialnumber character varying(255) COLLATE pg_catalog."default",
    credentialtype character varying(255) COLLATE pg_catalog."default",
    hiredateeligible integer,
    eligiblestatus integer,
    rank integer,
    personid character varying(255) COLLATE pg_catalog."default",
    credentialstatus character varying(255) COLLATE pg_catalog."default",
    lastissuancedate character varying(255) COLLATE pg_catalog."default",
    firstissuancedate character varying(255) COLLATE pg_catalog."default",
    credcount bigint,
    cred_status_count bigint,
    stat text COLLATE pg_catalog."default",
    primary_cred text COLLATE pg_catalog."default",
    credtype text COLLATE pg_catalog."default",
    hireexp integer,
    hiredate timestamp without time zone,
    expirationdate character varying(255) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dateofhire character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.cred_details_base
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.cred_details_base TO anveeraprasad;

GRANT ALL ON TABLE staging.cred_details_base TO cicd_pipeline;

GRANT SELECT ON TABLE staging.cred_details_base TO eblythe;

GRANT SELECT ON TABLE staging.cred_details_base TO htata;

GRANT SELECT ON TABLE staging.cred_details_base TO lizawu;

GRANT SELECT ON TABLE staging.cred_details_base TO readonly_testing;

GRANT ALL ON TABLE staging.cred_details_base TO system_pipeline;