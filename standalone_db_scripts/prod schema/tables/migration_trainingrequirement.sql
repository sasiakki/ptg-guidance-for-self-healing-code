-- Table: prod.migration_trainingrequirement

-- DROP TABLE IF EXISTS prod.migration_trainingrequirement;

CREATE TABLE IF NOT EXISTS prod.migration_trainingrequirement
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
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone,
    reasonfortransfer character varying COLLATE pg_catalog."default",
    comments character varying COLLATE pg_catalog."default",
    duedateoverridereason character varying(50) COLLATE pg_catalog."default",
    archived timestamp without time zone,
    learningpath character varying(20) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.migration_trainingrequirement
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.migration_trainingrequirement TO PUBLIC;

GRANT ALL ON TABLE prod.migration_trainingrequirement TO cicd_pipeline;

GRANT INSERT ON TABLE prod.migration_trainingrequirement TO readonly_testing;

GRANT ALL ON TABLE prod.migration_trainingrequirement TO system_pipeline;