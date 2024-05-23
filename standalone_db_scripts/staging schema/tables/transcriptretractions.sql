-- Table: staging.transcriptretractions

-- DROP TABLE IF EXISTS staging.transcriptretractions;

CREATE TABLE IF NOT EXISTS staging.transcriptretractions
(
    id bigint NOT NULL DEFAULT nextval('staging.transcriptretractions_id_seq'::regclass),
    transcriptid bigint NOT NULL,
    personid bigint NOT NULL,
    courseid character varying COLLATE pg_catalog."default",
    credithours numeric(5,2),
    completeddate date,
    coursename character varying COLLATE pg_catalog."default",
    instructorid character varying COLLATE pg_catalog."default",
    instructor character varying COLLATE pg_catalog."default",
    trainingsource character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    filedate date,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dshsid character varying COLLATE pg_catalog."default",
    archivedreason character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.transcriptretractions
    OWNER to postgres;

GRANT SELECT ON TABLE staging.transcriptretractions TO PUBLIC;

GRANT ALL ON TABLE staging.transcriptretractions TO cicd_pipeline;

GRANT ALL ON TABLE staging.transcriptretractions TO postgres;

GRANT INSERT, SELECT ON TABLE staging.transcriptretractions TO readonly_testing;

GRANT ALL ON TABLE staging.transcriptretractions TO system_pipeline;