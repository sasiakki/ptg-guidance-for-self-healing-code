-- Table: logs.traininghistorylog

-- DROP TABLE IF EXISTS logs.traininghistorylog;

CREATE TABLE IF NOT EXISTS logs.traininghistorylog
(
    traininghistorylogid bigint NOT NULL DEFAULT nextval('staging.traininghistorylog_id_seq'::regclass),
    personid bigint,
    completeddate date,
    credithours double precision,
    coursename character varying COLLATE pg_catalog."default",
    instructorname character varying COLLATE pg_catalog."default",
    instructorid character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    courseid character varying COLLATE pg_catalog."default",
    trainingprogramcode bigint,
    qual_person_id bigint,
    dshsid bigint,
    coursetype character varying COLLATE pg_catalog."default",
    courselanguage character varying COLLATE pg_catalog."default",
    trainingprogramtype character varying COLLATE pg_catalog."default",
    trainingsource character varying COLLATE pg_catalog."default",
    dshscourseid character varying COLLATE pg_catalog."default",
    error_message character varying COLLATE pg_catalog."default",
    filename character varying(800) COLLATE pg_catalog."default",
    filedate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.traininghistorylog
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE logs.traininghistorylog TO anveeraprasad;

GRANT ALL ON TABLE logs.traininghistorylog TO cicd_pipeline;

GRANT SELECT ON TABLE logs.traininghistorylog TO readonly_testing;

GRANT ALL ON TABLE logs.traininghistorylog TO system_pipeline;