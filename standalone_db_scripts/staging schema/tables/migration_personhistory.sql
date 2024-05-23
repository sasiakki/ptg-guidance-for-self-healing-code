-- Table: staging.migration_personhistory

-- DROP TABLE IF EXISTS staging.migration_personhistory;

CREATE TABLE IF NOT EXISTS staging.migration_personhistory
(
    personid bigint,
    firstname character varying(1000) COLLATE pg_catalog."default",
    lastname character varying(255) COLLATE pg_catalog."default",
    ssn character varying(30) COLLATE pg_catalog."default",
    email1 character varying(255) COLLATE pg_catalog."default",
    mobilephone character varying(30) COLLATE pg_catalog."default",
    language character varying(300) COLLATE pg_catalog."default",
    physicaladdress character varying(1000) COLLATE pg_catalog."default",
    mailingaddress character varying(1000) COLLATE pg_catalog."default",
    status character varying(30) COLLATE pg_catalog."default",
    exempt character varying(30) COLLATE pg_catalog."default",
    hiredate timestamp without time zone,
    type character varying(30) COLLATE pg_catalog."default",
    workercategory character varying(30) COLLATE pg_catalog."default",
    categorycode character varying(30) COLLATE pg_catalog."default",
    modified timestamp without time zone,
    credentialnumber character varying(50) COLLATE pg_catalog."default",
    sourcekey character varying(50) COLLATE pg_catalog."default",
    dshsid bigint,
    dob character varying COLLATE pg_catalog."default",
    cdwa_id integer,
    email2 character varying(255) COLLATE pg_catalog."default",
    homephone character varying(30) COLLATE pg_catalog."default",
    trackingdate timestamp without time zone,
    iscarinaeligible boolean,
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone,
    trainingstatus character varying(30) COLLATE pg_catalog."default",
    middlename character varying(255) COLLATE pg_catalog."default",
    mailingstreet1 character varying(255) COLLATE pg_catalog."default",
    mailingstreet2 character varying(255) COLLATE pg_catalog."default",
    mailingcity character varying(255) COLLATE pg_catalog."default",
    mailingstate character varying(255) COLLATE pg_catalog."default",
    mailingzip character varying(20) COLLATE pg_catalog."default",
    mailingcountry character varying(30) COLLATE pg_catalog."default",
    filemodifieddate date,
    preferred_language character varying(50) COLLATE pg_catalog."default",
    last_background_check_date date,
    ip_contract_expiration_date date,
    agencyid bigint,
    ie_date date,
    ahcas_eligible boolean
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.migration_personhistory
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.migration_personhistory TO PUBLIC;

GRANT ALL ON TABLE staging.migration_personhistory TO cicd_pipeline;

GRANT INSERT ON TABLE staging.migration_personhistory TO readonly_testing;

GRANT ALL ON TABLE staging.migration_personhistory TO system_pipeline;