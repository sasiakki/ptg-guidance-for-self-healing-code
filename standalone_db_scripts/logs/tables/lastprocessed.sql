-- Table: logs.lastprocessed

-- DROP TABLE IF EXISTS logs.lastprocessed;

CREATE TABLE IF NOT EXISTS logs.lastprocessed
(
    id bigint NOT NULL DEFAULT nextval('logs.lastprocessed_seq'::regclass),
    processname character varying(100) COLLATE pg_catalog."default" NOT NULL,
    lastprocesseddate timestamp without time zone NOT NULL,
    success character varying(5) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT lastprocessed_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.lastprocessed
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE logs.lastprocessed TO anveeraprasad;

GRANT ALL ON TABLE logs.lastprocessed TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.lastprocessed TO readonly_testing;

GRANT ALL ON TABLE logs.lastprocessed TO system_pipeline;