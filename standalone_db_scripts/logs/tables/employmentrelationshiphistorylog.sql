-- Table: logs.employmentrelationshiphistorylog

-- DROP TABLE IF EXISTS logs.employmentrelationshiphistorylog;

CREATE TABLE IF NOT EXISTS logs.employmentrelationshiphistorylog
(
    id integer NOT NULL DEFAULT nextval('logs.employmentrelationshiphistorylog_id_seq'::regclass),
    relationshipid character varying COLLATE pg_catalog."default",
    personid bigint,
    employeeid bigint,
    employerid character varying COLLATE pg_catalog."default",
    branchid character varying COLLATE pg_catalog."default",
    empstatus character varying COLLATE pg_catalog."default",
    workercategory character varying COLLATE pg_catalog."default",
    categorycode character varying COLLATE pg_catalog."default",
    hiredate character varying COLLATE pg_catalog."default",
    trackingdate character varying COLLATE pg_catalog."default",
    role character varying COLLATE pg_catalog."default",
    isoverride character varying COLLATE pg_catalog."default",
    isignored character varying COLLATE pg_catalog."default",
    sourcekey character varying COLLATE pg_catalog."default",
    authstart character varying COLLATE pg_catalog."default",
    authend character varying COLLATE pg_catalog."default",
    terminationdate character varying COLLATE pg_catalog."default",
    modified timestamp without time zone,
    filedate character varying COLLATE pg_catalog."default",
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    createdby character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.employmentrelationshiphistorylog
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE logs.employmentrelationshiphistorylog TO anveeraprasad;

GRANT ALL ON TABLE logs.employmentrelationshiphistorylog TO cicd_pipeline;

GRANT SELECT ON TABLE logs.employmentrelationshiphistorylog TO lizawu;

GRANT SELECT ON TABLE logs.employmentrelationshiphistorylog TO readonly_testing;

GRANT ALL ON TABLE logs.employmentrelationshiphistorylog TO system_pipeline;