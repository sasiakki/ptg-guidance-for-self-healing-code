-- Table: logs.test2

-- DROP TABLE IF EXISTS logs.test2;

CREATE TABLE IF NOT EXISTS logs.test2
(
    id integer,
    name character varying(40) COLLATE pg_catalog."default",
    completion date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.test2
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.test2 TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.test2 TO readonly_testing;

GRANT ALL ON TABLE logs.test2 TO system_pipeline;