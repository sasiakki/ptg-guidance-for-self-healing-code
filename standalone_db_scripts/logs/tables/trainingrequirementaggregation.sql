-- Table: logs.trainingrequirementaggregation

-- DROP TABLE IF EXISTS logs.trainingrequirementaggregation;

CREATE TABLE IF NOT EXISTS logs.trainingrequirementaggregation
(
    trainingid character varying(50) COLLATE pg_catalog."default",
    transcriptcount integer,
    nochange boolean,
    trainingstatusold character varying(30) COLLATE pg_catalog."default",
    trainingstatusnew character varying(30) COLLATE pg_catalog."default",
    requiredhours real,
    totalhoursold numeric(5,2),
    totalhoursnew numeric(5,2),
    earnedhoursold real,
    earnedhoursnew real,
    transferhoursold numeric(5,2),
    transferhoursnew numeric(5,2),
    trainingcompletedateold date,
    trainingcompletedatenew date,
    archived timestamp with time zone,
    recordmodified_old timestamp with time zone,
    execution_time timestamp with time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.trainingrequirementaggregation
    OWNER to postgres;

GRANT ALL ON TABLE logs.trainingrequirementaggregation TO cicd_pipeline;

GRANT ALL ON TABLE logs.trainingrequirementaggregation TO postgres;

GRANT INSERT, SELECT ON TABLE logs.trainingrequirementaggregation TO readonly_testing;

GRANT ALL ON TABLE logs.trainingrequirementaggregation TO system_pipeline;