-- Table: raw.ethnicity

-- DROP TABLE IF EXISTS "raw".ethnicity;

CREATE TABLE IF NOT EXISTS "raw".ethnicity
(
    id integer NOT NULL DEFAULT nextval('raw.ethnicity_id_seq'::regclass),
    code character varying(2) COLLATE pg_catalog."default" NOT NULL,
    value character varying(50) COLLATE pg_catalog."default" NOT NULL,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone,
    CONSTRAINT ethnicity_pk PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".ethnicity
    OWNER to cicd_pipeline;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".ethnicity TO anveeraprasad;

GRANT ALL ON TABLE "raw".ethnicity TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".ethnicity TO jsharief;

GRANT SELECT ON TABLE "raw".ethnicity TO lizawu;

GRANT SELECT ON TABLE "raw".ethnicity TO readonly_testing;

GRANT ALL ON TABLE "raw".ethnicity TO system_pipeline;