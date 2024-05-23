-- Table: prod.migration_person

-- DROP TABLE IF EXISTS prod.migration_person;

CREATE TABLE IF NOT EXISTS prod.migration_person
(
    firstname character varying(255) COLLATE pg_catalog."default",
    lastname character varying(255) COLLATE pg_catalog."default",
    ssn character varying(30) COLLATE pg_catalog."default",
    email1 character varying(255) COLLATE pg_catalog."default",
    email2 character varying(255) COLLATE pg_catalog."default",
    homephone character varying(30) COLLATE pg_catalog."default",
    mobilephone character varying(30) COLLATE pg_catalog."default",
    language character varying(255) COLLATE pg_catalog."default",
    physicaladdress text COLLATE pg_catalog."default",
    mailingaddress text COLLATE pg_catalog."default",
    status character varying(30) COLLATE pg_catalog."default",
    exempt character varying(30) COLLATE pg_catalog."default",
    type character varying(30) COLLATE pg_catalog."default",
    workercategory character varying(30) COLLATE pg_catalog."default",
    categorycode character varying(30) COLLATE pg_catalog."default",
    iscarinaeligible boolean,
    personid bigint,
    dob character varying COLLATE pg_catalog."default",
    hiredate timestamp without time zone,
    trackingdate date,
    ahcas_eligible boolean,
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
    dshsid bigint,
    credentialnumber character varying COLLATE pg_catalog."default",
    cdwaid bigint,
    sfcontactid character varying COLLATE pg_catalog."default",
    matched_sourcekeys character varying COLLATE pg_catalog."default",
    lasttermdate date,
    rehiredate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.migration_person
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.migration_person TO PUBLIC;

GRANT ALL ON TABLE prod.migration_person TO cicd_pipeline;

GRANT INSERT ON TABLE prod.migration_person TO readonly_testing;

GRANT ALL ON TABLE prod.migration_person TO system_pipeline;