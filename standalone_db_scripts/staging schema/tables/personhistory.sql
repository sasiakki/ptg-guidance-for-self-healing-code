-- Table: staging.personhistory

-- DROP TABLE IF EXISTS staging.personhistory;

CREATE TABLE IF NOT EXISTS staging.personhistory
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
    workercategory character varying(100) COLLATE pg_catalog."default",
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
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
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
    ahcas_eligible boolean DEFAULT false
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.personhistory
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.personhistory TO anveeraprasad;

GRANT ALL ON TABLE staging.personhistory TO cicd_pipeline;

GRANT SELECT ON TABLE staging.personhistory TO eblythe;

GRANT SELECT ON TABLE staging.personhistory TO htata;

GRANT SELECT ON TABLE staging.personhistory TO lizawu;

GRANT SELECT ON TABLE staging.personhistory TO readonly_testing;

GRANT ALL ON TABLE staging.personhistory TO system_pipeline;
-- Index: idx_staging_person_history

-- DROP INDEX IF EXISTS staging.idx_staging_person_history;

CREATE INDEX IF NOT EXISTS idx_staging_person_history
    ON staging.personhistory USING btree
    (sourcekey COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: sph_personid_idx

-- DROP INDEX IF EXISTS staging.sph_personid_idx;

CREATE INDEX IF NOT EXISTS sph_personid_idx
    ON staging.personhistory USING btree
    (personid ASC NULLS LAST)
    TABLESPACE pg_default;