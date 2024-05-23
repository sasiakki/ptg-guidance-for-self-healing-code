-- Table: logs.migration_traineestatuslogs

-- DROP TABLE IF EXISTS logs.migration_traineestatuslogs;

CREATE TABLE IF NOT EXISTS logs.migration_traineestatuslogs
(
    employeeid character varying COLLATE pg_catalog."default",
    personid bigint,
    compliancestatus character varying COLLATE pg_catalog."default",
    trainingexempt character varying COLLATE pg_catalog."default",
    trainingprogram character varying COLLATE pg_catalog."default",
    trainingstatus character varying COLLATE pg_catalog."default",
    classname character varying COLLATE pg_catalog."default",
    dshscoursecode character varying COLLATE pg_catalog."default",
    credithours numeric,
    completeddate character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    isvalid boolean,
    errormessage character varying COLLATE pg_catalog."default",
    matchstatus character varying COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone,
    recordmodifieddate timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.migration_traineestatuslogs
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.migration_traineestatuslogs TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.migration_traineestatuslogs TO readonly_testing;

GRANT ALL ON TABLE logs.migration_traineestatuslogs TO system_pipeline;