-- Table: prod.migration_employmentrelationship

-- DROP TABLE IF EXISTS prod.migration_employmentrelationship;

CREATE TABLE IF NOT EXISTS prod.migration_employmentrelationship
(
    relationshipid bigint,
    personid bigint,
    employeeid bigint,
    employerid character varying(255) COLLATE pg_catalog."default",
    branchid integer,
    workercategory character varying(50) COLLATE pg_catalog."default",
    categorycode character varying(50) COLLATE pg_catalog."default",
    hiredate timestamp without time zone,
    authstart character varying COLLATE pg_catalog."default",
    authend character varying COLLATE pg_catalog."default",
    empstatus character varying(50) COLLATE pg_catalog."default",
    terminationdate character varying COLLATE pg_catalog."default",
    trackingdate character varying COLLATE pg_catalog."default",
    isoverride boolean,
    isignored boolean,
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone,
    sfngrecordid character varying(50) COLLATE pg_catalog."default",
    source character varying COLLATE pg_catalog."default",
    role character varying COLLATE pg_catalog."default",
    agencyid bigint,
    filedate date,
    createdby character varying(50) COLLATE pg_catalog."default",
    relationship character varying COLLATE pg_catalog."default",
    priority integer,
    rehiredate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.migration_employmentrelationship
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.migration_employmentrelationship TO PUBLIC;

GRANT ALL ON TABLE prod.migration_employmentrelationship TO cicd_pipeline;

GRANT INSERT ON TABLE prod.migration_employmentrelationship TO readonly_testing;

GRANT ALL ON TABLE prod.migration_employmentrelationship TO system_pipeline;