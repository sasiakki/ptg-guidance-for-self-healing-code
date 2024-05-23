-- Table: raw.maritalstatus

-- DROP TABLE IF EXISTS "raw".maritalstatus;

CREATE TABLE IF NOT EXISTS "raw".maritalstatus
(
    id integer NOT NULL DEFAULT nextval('raw.maritalstatus_id_seq'::regclass),
    code character varying(1) COLLATE pg_catalog."default" NOT NULL,
    value character varying(50) COLLATE pg_catalog."default" NOT NULL,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone,
    CONSTRAINT maritalstatus_pk PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".maritalstatus
    OWNER to cicd_pipeline;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".maritalstatus TO anveeraprasad;

GRANT ALL ON TABLE "raw".maritalstatus TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".maritalstatus TO jsharief;

GRANT SELECT ON TABLE "raw".maritalstatus TO lizawu;

GRANT SELECT ON TABLE "raw".maritalstatus TO readonly_testing;

GRANT ALL ON TABLE "raw".maritalstatus TO system_pipeline;