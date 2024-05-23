-- Table: logs.trainingtransferslogs

-- DROP TABLE IF EXISTS logs.trainingtransferslogs;

CREATE TABLE IF NOT EXISTS logs.trainingtransferslogs
(
    employeeid bigint,
    personid bigint,
    trainingprogram character varying COLLATE pg_catalog."default",
    trainingprogramcode character varying COLLATE pg_catalog."default",
    classname character varying COLLATE pg_catalog."default",
    dshscoursecode character varying COLLATE pg_catalog."default",
    credithours character varying COLLATE pg_catalog."default",
    completeddate date,
    trainingentity character varying COLLATE pg_catalog."default",
    reasonfortransfer character varying COLLATE pg_catalog."default",
    employerstaff character varying COLLATE pg_catalog."default",
    createddate date,
    filename character varying COLLATE pg_catalog."default",
    filedate date,
    isvalid boolean DEFAULT false,
    error_message character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.trainingtransferslogs
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE logs.trainingtransferslogs TO anveeraprasad;

GRANT ALL ON TABLE logs.trainingtransferslogs TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.trainingtransferslogs TO readonly_testing;

GRANT ALL ON TABLE logs.trainingtransferslogs TO system_pipeline;