-- Table: staging.employmentrelationshiphistory

-- DROP TABLE IF EXISTS staging.employmentrelationshiphistory;

CREATE TABLE IF NOT EXISTS staging.employmentrelationshiphistory
(
    relationshipid integer NOT NULL DEFAULT nextval('staging.employmentrelationshiphistory_relationshipid_seq'::regclass),
    personid bigint,
    employeeid bigint,
    workercategory character varying(100) COLLATE pg_catalog."default",
    categorycode character varying(30) COLLATE pg_catalog."default",
    role character varying(30) COLLATE pg_catalog."default",
    source character varying COLLATE pg_catalog."default",
    priority integer,
    modifieddate timestamp without time zone,
    createdby character varying(50) COLLATE pg_catalog."default",
    filedate date,
    relationship character varying COLLATE pg_catalog."default",
    branchid integer,
    hiredate timestamp without time zone,
    authstart character varying COLLATE pg_catalog."default",
    authend character varying COLLATE pg_catalog."default",
    terminationdate character varying COLLATE pg_catalog."default",
    empstatus character varying COLLATE pg_catalog."default",
    trackingdate character varying COLLATE pg_catalog."default",
    modified timestamp without time zone,
    employerid character varying(255) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    sfngrecordid character varying(50) COLLATE pg_catalog."default",
    isignored boolean DEFAULT false,
    isoverride boolean DEFAULT false,
    agencyid bigint,
    branch1 integer,
    branch2 integer,
    branch3 integer,
    branch4 integer,
    authtermflag character varying COLLATE pg_catalog."default",
    CONSTRAINT employmentrelationshiphistory_pkey PRIMARY KEY (relationshipid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.employmentrelationshiphistory
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.employmentrelationshiphistory TO anveeraprasad;

GRANT ALL ON TABLE staging.employmentrelationshiphistory TO cicd_pipeline;

GRANT SELECT ON TABLE staging.employmentrelationshiphistory TO eblythe;

GRANT SELECT ON TABLE staging.employmentrelationshiphistory TO htata;

GRANT SELECT ON TABLE staging.employmentrelationshiphistory TO lizawu;

GRANT SELECT ON TABLE staging.employmentrelationshiphistory TO readonly_testing;

GRANT ALL ON TABLE staging.employmentrelationshiphistory TO system_pipeline;
-- Index: idx_staging_employmentrelationshiphistory

-- DROP INDEX IF EXISTS staging.idx_staging_employmentrelationshiphistory;

CREATE INDEX IF NOT EXISTS idx_staging_employmentrelationshiphistory
    ON staging.employmentrelationshiphistory USING btree
    (source COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: ser_personid_idx

-- DROP INDEX IF EXISTS staging.ser_personid_idx;

CREATE INDEX IF NOT EXISTS ser_personid_idx
    ON staging.employmentrelationshiphistory USING btree
    (personid ASC NULLS LAST)
    TABLESPACE pg_default;