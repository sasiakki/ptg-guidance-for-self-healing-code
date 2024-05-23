-- Table: logs.doceboilterrors

-- DROP TABLE IF EXISTS logs.doceboilterrors;

CREATE TABLE IF NOT EXISTS logs.doceboilterrors
(
    id bigint NOT NULL DEFAULT nextval('logs.doceboilterrors_id_seq'::regclass),
    username character varying COLLATE pg_catalog."default",
    firstname character varying COLLATE pg_catalog."default",
    lastname character varying COLLATE pg_catalog."default",
    trainingid character varying COLLATE pg_catalog."default",
    coursename character varying COLLATE pg_catalog."default",
    coursecode character varying COLLATE pg_catalog."default",
    credits character varying COLLATE pg_catalog."default",
    dshscode character varying COLLATE pg_catalog."default",
    sessioninstructor character varying COLLATE pg_catalog."default",
    sessionname character varying COLLATE pg_catalog."default",
    eventinstructor character varying COLLATE pg_catalog."default",
    completiondate character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    filedate date,
    error_reason character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.doceboilterrors
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.doceboilterrors TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.doceboilterrors TO readonly_testing;

GRANT ALL ON TABLE logs.doceboilterrors TO system_pipeline;