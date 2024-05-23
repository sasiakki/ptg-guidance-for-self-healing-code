-- Table: logs.fileprocesserrorlogs

-- DROP TABLE IF EXISTS logs.fileprocesserrorlogs;

CREATE TABLE IF NOT EXISTS logs.fileprocesserrorlogs
(
    id integer NOT NULL DEFAULT nextval('logs.fileprocesserrorlogs_id_seq'::regclass),
    row_id integer,
    employee_id numeric(9,0),
    name character varying COLLATE pg_catalog."default",
    error_message character varying COLLATE pg_catalog."default",
    file_category character varying COLLATE pg_catalog."default",
    file_name character varying COLLATE pg_catalog."default",
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.fileprocesserrorlogs
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE logs.fileprocesserrorlogs TO anveeraprasad;

GRANT ALL ON TABLE logs.fileprocesserrorlogs TO cicd_pipeline;

GRANT SELECT ON TABLE logs.fileprocesserrorlogs TO eblythe;

GRANT SELECT ON TABLE logs.fileprocesserrorlogs TO htata;

GRANT SELECT ON TABLE logs.fileprocesserrorlogs TO lizawu;

GRANT SELECT ON TABLE logs.fileprocesserrorlogs TO readonly_testing;

GRANT ALL ON TABLE logs.fileprocesserrorlogs TO system_pipeline;