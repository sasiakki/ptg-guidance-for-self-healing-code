-- Table: logs.personquarantine

-- DROP TABLE IF EXISTS logs.personquarantine;

CREATE TABLE IF NOT EXISTS logs.personquarantine
(
    person_unique_id bigint,
    firstname character varying(255) COLLATE pg_catalog."default",
    lastname character varying(255) COLLATE pg_catalog."default",
    middlename character varying(255) COLLATE pg_catalog."default",
    ssn character varying(30) COLLATE pg_catalog."default",
    email1 character varying(255) COLLATE pg_catalog."default",
    email2 character varying(255) COLLATE pg_catalog."default",
    homephone character varying(255) COLLATE pg_catalog."default",
    mobilephone character varying(30) COLLATE pg_catalog."default",
    language character varying(255) COLLATE pg_catalog."default",
    physicaladdress character varying(255) COLLATE pg_catalog."default",
    mailingaddress character varying(255) COLLATE pg_catalog."default",
    status character varying(30) COLLATE pg_catalog."default",
    exempt character varying(30) COLLATE pg_catalog."default",
    type character varying(255) COLLATE pg_catalog."default",
    workercategory character varying(255) COLLATE pg_catalog."default",
    credentialnumber character varying(255) COLLATE pg_catalog."default",
    cdwaid bigint,
    dshsid bigint,
    categorycode character varying(10) COLLATE pg_catalog."default",
    iscarinaeligible boolean,
    personid bigint,
    dob character varying COLLATE pg_catalog."default",
    hiredate timestamp without time zone,
    trackingdate date,
    ahcas_eligible boolean,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    sfcontactid character varying COLLATE pg_catalog."default",
    approval_status character varying COLLATE pg_catalog."default",
    sourcekey character varying COLLATE pg_catalog."default",
    mailingstreet1 character varying COLLATE pg_catalog."default",
    mailingstreet2 character varying COLLATE pg_catalog."default",
    mailingcity character varying COLLATE pg_catalog."default",
    mailingstate character varying COLLATE pg_catalog."default",
    mailingzip character varying COLLATE pg_catalog."default",
    mailingcountry character varying COLLATE pg_catalog."default",
    matched_sourcekeys character varying COLLATE pg_catalog."default",
    studentid bigint
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.personquarantine
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.personquarantine TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.personquarantine TO readonly_testing;

GRANT ALL ON TABLE logs.personquarantine TO system_pipeline;