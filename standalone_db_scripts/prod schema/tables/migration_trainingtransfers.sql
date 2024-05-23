-- Table: prod.migration_trainingtransfers

-- DROP TABLE IF EXISTS prod.migration_trainingtransfers;

CREATE TABLE IF NOT EXISTS prod.migration_trainingtransfers
(
    transferid bigint,
    personid bigint,
    employerid bigint,
    employeeid bigint,
    trainingid character varying COLLATE pg_catalog."default",
    trainingprogram character varying COLLATE pg_catalog."default",
    trainingprogramcode character varying COLLATE pg_catalog."default",
    classname character varying COLLATE pg_catalog."default",
    dshscoursecode character varying COLLATE pg_catalog."default",
    transferhours numeric(5,2),
    completeddate date,
    transfersource character varying COLLATE pg_catalog."default",
    reasonfortransfer character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone,
    courseid character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.migration_trainingtransfers
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.migration_trainingtransfers TO PUBLIC;

GRANT ALL ON TABLE prod.migration_trainingtransfers TO cicd_pipeline;

GRANT INSERT ON TABLE prod.migration_trainingtransfers TO readonly_testing;

GRANT ALL ON TABLE prod.migration_trainingtransfers TO system_pipeline;