-- Table: logs.transcriptretractionerrors

-- DROP TABLE IF EXISTS logs.transcriptretractionerrors;

CREATE TABLE IF NOT EXISTS logs.transcriptretractionerrors
(
    id bigint NOT NULL,
    transcriptid bigint,
    personid bigint,
    courseid character varying COLLATE pg_catalog."default",
    dshsid character varying COLLATE pg_catalog."default",
    credithours numeric(5,2),
    completeddate date,
    coursename character varying COLLATE pg_catalog."default",
    instructorid character varying COLLATE pg_catalog."default",
    instructor character varying COLLATE pg_catalog."default",
    trainingsource character varying COLLATE pg_catalog."default",
    errorreason character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    filedate date,
    archivedreason character varying COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.transcriptretractionerrors
    OWNER to postgres;

GRANT ALL ON TABLE logs.transcriptretractionerrors TO cicd_pipeline;

GRANT ALL ON TABLE logs.transcriptretractionerrors TO postgres;

GRANT INSERT, SELECT ON TABLE logs.transcriptretractionerrors TO readonly_testing;

GRANT ALL ON TABLE logs.transcriptretractionerrors TO system_pipeline;