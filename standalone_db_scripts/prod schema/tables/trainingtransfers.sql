-- Table: prod.trainingtransfers

-- DROP TABLE IF EXISTS prod.trainingtransfers;

CREATE TABLE IF NOT EXISTS prod.trainingtransfers
(
    transferid bigint NOT NULL DEFAULT nextval('prod.trainingtransfer_id_seq'::regclass),
    personid bigint NOT NULL,
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
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    courseid character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.trainingtransfers
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.trainingtransfers TO PUBLIC;

GRANT SELECT ON TABLE prod.trainingtransfers TO anveeraprasad;

GRANT ALL ON TABLE prod.trainingtransfers TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE prod.trainingtransfers TO readonly_testing;

GRANT ALL ON TABLE prod.trainingtransfers TO system_pipeline;