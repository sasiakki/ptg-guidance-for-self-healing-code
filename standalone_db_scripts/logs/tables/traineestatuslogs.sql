-- Table: logs.traineestatuslogs

-- DROP TABLE IF EXISTS logs.traineestatuslogs;

CREATE TABLE IF NOT EXISTS logs.traineestatuslogs
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
    isvalid boolean NOT NULL DEFAULT true,
    errormessage character varying COLLATE pg_catalog."default",
    matchstatus character varying COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT now(),
    recordmodifieddate timestamp without time zone DEFAULT now()
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.traineestatuslogs
    OWNER to postgres;

GRANT SELECT ON TABLE logs.traineestatuslogs TO anveeraprasad;

GRANT ALL ON TABLE logs.traineestatuslogs TO cicd_pipeline;

GRANT ALL ON TABLE logs.traineestatuslogs TO postgres;

GRANT SELECT, INSERT ON TABLE logs.traineestatuslogs TO readonly_testing;

GRANT ALL ON TABLE logs.traineestatuslogs TO system_pipeline;