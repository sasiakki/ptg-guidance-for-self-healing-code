-- Table: prod.employmentrelationship

-- DROP TABLE IF EXISTS prod.employmentrelationship;

CREATE TABLE IF NOT EXISTS prod.employmentrelationship
(
    relationshipid bigint DEFAULT nextval('prod.employmentrelationship_relationshipid_seq'::regclass),
    personid bigint,
    employeeid bigint,
    employerid character varying(255) COLLATE pg_catalog."default",
    branchid integer,
    workercategory character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    categorycode character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    hiredate timestamp without time zone,
    authstart character varying COLLATE pg_catalog."default",
    authend character varying COLLATE pg_catalog."default",
    empstatus character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    terminationdate character varying COLLATE pg_catalog."default",
    trackingdate character varying COLLATE pg_catalog."default",
    isoverride boolean DEFAULT false,
    isignored boolean DEFAULT false,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
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

ALTER TABLE IF EXISTS prod.employmentrelationship
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.employmentrelationship TO anveeraprasad;

GRANT ALL ON TABLE prod.employmentrelationship TO cicd_pipeline;

GRANT SELECT ON TABLE prod.employmentrelationship TO cukaumunna;

GRANT SELECT ON TABLE prod.employmentrelationship TO eblythe;

GRANT SELECT ON TABLE prod.employmentrelationship TO htata;

GRANT SELECT ON TABLE prod.employmentrelationship TO lizawu;

GRANT SELECT ON TABLE prod.employmentrelationship TO readonly_testing;

GRANT ALL ON TABLE prod.employmentrelationship TO system_pipeline;
-- Index: idx_prod_employmentrelationship

-- DROP INDEX IF EXISTS prod.idx_prod_employmentrelationship;

CREATE INDEX IF NOT EXISTS idx_prod_employmentrelationship
    ON prod.employmentrelationship USING btree
    (source COLLATE pg_catalog."default" ASC NULLS LAST, personid ASC NULLS LAST)
    TABLESPACE pg_default;