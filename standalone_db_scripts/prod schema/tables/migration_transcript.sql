-- Table: prod.migration_transcript

-- DROP TABLE IF EXISTS prod.migration_transcript;

CREATE TABLE IF NOT EXISTS prod.migration_transcript
(
    transcriptid bigint,
    personid bigint,
    coursename character varying COLLATE pg_catalog."default",
    courseid character varying COLLATE pg_catalog."default",
    completeddate character varying COLLATE pg_catalog."default",
    credithours numeric(5,2),
    coursetype character varying COLLATE pg_catalog."default",
    trainingprogram character varying COLLATE pg_catalog."default",
    trainingprogramcode character varying COLLATE pg_catalog."default",
    instructorname character varying COLLATE pg_catalog."default",
    instructorid character varying COLLATE pg_catalog."default",
    dshscourseid character varying(50) COLLATE pg_catalog."default",
    trainingsource character varying(50) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone,
    trainingid character varying COLLATE pg_catalog."default",
    learningpath character varying(20) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.migration_transcript
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.migration_transcript TO PUBLIC;

GRANT ALL ON TABLE prod.migration_transcript TO cicd_pipeline;

GRANT INSERT ON TABLE prod.migration_transcript TO readonly_testing;

GRANT ALL ON TABLE prod.migration_transcript TO system_pipeline;