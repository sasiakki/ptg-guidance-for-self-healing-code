-- Table: logs.noshowerrors

-- DROP TABLE IF EXISTS logs.noshowerrors;

CREATE TABLE IF NOT EXISTS logs.noshowerrors
(
    id bigint NOT NULL DEFAULT nextval('logs.noshowerrors_id_seq'::regclass),
    transcriptid character varying COLLATE pg_catalog."default",
    personid character varying COLLATE pg_catalog."default",
    courseid character varying COLLATE pg_catalog."default",
    dshsid character varying COLLATE pg_catalog."default",
    credithours character varying COLLATE pg_catalog."default",
    completeddate character varying COLLATE pg_catalog."default",
    coursename character varying COLLATE pg_catalog."default",
    instructorid character varying COLLATE pg_catalog."default",
    instructor character varying COLLATE pg_catalog."default",
    trainingsource character varying COLLATE pg_catalog."default",
    errorreason character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    archivedreason character varying COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filedate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.noshowerrors
    OWNER to postgres;

GRANT ALL ON TABLE logs.noshowerrors TO cicd_pipeline;

GRANT ALL ON TABLE logs.noshowerrors TO postgres;

GRANT INSERT, SELECT ON TABLE logs.noshowerrors TO readonly_testing;

GRANT ALL ON TABLE logs.noshowerrors TO system_pipeline;