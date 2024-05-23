-- Table: prod.transcriptarchive

-- DROP TABLE IF EXISTS prod.transcriptarchive;

CREATE TABLE IF NOT EXISTS prod.transcriptarchive
(
    transcriptid bigint NOT NULL,
    personid bigint,
    coursename character varying COLLATE pg_catalog."default",
    courseid character varying COLLATE pg_catalog."default",
    completeddate timestamp without time zone,
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
    learningpath character varying(10) COLLATE pg_catalog."default",
    reasonfortransfer character varying COLLATE pg_catalog."default",
    archived timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    archivedreason character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.transcriptarchive
    OWNER to postgres;

GRANT SELECT ON TABLE prod.transcriptarchive TO PUBLIC;

GRANT ALL ON TABLE prod.transcriptarchive TO cicd_pipeline;

GRANT ALL ON TABLE prod.transcriptarchive TO postgres;

GRANT INSERT, SELECT ON TABLE prod.transcriptarchive TO readonly_testing;

GRANT ALL ON TABLE prod.transcriptarchive TO system_pipeline;