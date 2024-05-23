-- Table: prod.migration_trainingrequirement_arch

-- DROP TABLE IF EXISTS prod.migration_trainingrequirement_arch;

CREATE TABLE IF NOT EXISTS prod.migration_trainingrequirement_arch
(
    requiredhours real,
    earnedhours real,
    transferredhours real,
    trainingprogram character varying COLLATE pg_catalog."default",
    trainingprogramcode character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default",
    trainingid character varying COLLATE pg_catalog."default",
    trainreq_id uuid,
    completeddate timestamp without time zone,
    isrequired boolean,
    trackingdate timestamp without time zone,
    duedate timestamp without time zone,
    isoverride boolean,
    duedateextension timestamp without time zone,
    created timestamp without time zone,
    personid bigint,
    isarchived boolean,
    datearchived timestamp without time zone,
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.migration_trainingrequirement_arch
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.migration_trainingrequirement_arch TO PUBLIC;

GRANT ALL ON TABLE prod.migration_trainingrequirement_arch TO cicd_pipeline;

GRANT INSERT ON TABLE prod.migration_trainingrequirement_arch TO readonly_testing;

GRANT ALL ON TABLE prod.migration_trainingrequirement_arch TO system_pipeline;