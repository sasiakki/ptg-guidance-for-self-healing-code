-- Table: logs.doceboerrors

-- DROP TABLE IF EXISTS logs.doceboerrors;

CREATE TABLE IF NOT EXISTS logs.doceboerrors
(
    id bigint NOT NULL DEFAULT nextval('logs.doceboerrors_id_seq'::regclass),
    username character varying(25) COLLATE pg_catalog."default",
    firstname character varying(255) COLLATE pg_catalog."default",
    lastname character varying(255) COLLATE pg_catalog."default",
    coursecode character varying(55) COLLATE pg_catalog."default",
    coursetype character varying(25) COLLATE pg_catalog."default",
    coursename character varying(255) COLLATE pg_catalog."default",
    firstaccessdate character varying(255) COLLATE pg_catalog."default",
    completiondate character varying(255) COLLATE pg_catalog."default",
    status character varying(25) COLLATE pg_catalog."default",
    credithours character varying(25) COLLATE pg_catalog."default",
    dshsid character varying(25) COLLATE pg_catalog."default",
    cdwaid character varying(25) COLLATE pg_catalog."default",
    trainingid character varying(50) COLLATE pg_catalog."default",
    dshscode character varying(25) COLLATE pg_catalog."default",
    filename character varying(250) COLLATE pg_catalog."default",
    filedate timestamp without time zone,
    error_reason character varying(255) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.doceboerrors
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.doceboerrors TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.doceboerrors TO readonly_testing;

GRANT ALL ON TABLE logs.doceboerrors TO system_pipeline;