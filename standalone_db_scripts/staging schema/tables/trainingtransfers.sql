-- Table: staging.trainingtransfers

-- DROP TABLE IF EXISTS staging.trainingtransfers;

CREATE TABLE IF NOT EXISTS staging.trainingtransfers
(
    employeeid bigint,
    personid bigint,
    trainingprogram character varying COLLATE pg_catalog."default",
    trainingprogramcode character varying COLLATE pg_catalog."default",
    classname character varying COLLATE pg_catalog."default",
    dshscoursecode character varying COLLATE pg_catalog."default",
    transferhours numeric(5,2),
    completeddate date,
    transfersource character varying COLLATE pg_catalog."default",
    reasonfortransfer character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    courseid character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.trainingtransfers
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.trainingtransfers TO PUBLIC;

GRANT SELECT ON TABLE staging.trainingtransfers TO anveeraprasad;

GRANT ALL ON TABLE staging.trainingtransfers TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE staging.trainingtransfers TO readonly_testing;

GRANT ALL ON TABLE staging.trainingtransfers TO system_pipeline;