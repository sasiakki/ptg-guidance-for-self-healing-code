-- Table: raw.languages

-- DROP TABLE IF EXISTS "raw".languages;

CREATE TABLE IF NOT EXISTS "raw".languages
(
    id integer NOT NULL DEFAULT nextval('raw.languages_id_seq'::regclass),
    code character varying(50) COLLATE pg_catalog."default" NOT NULL,
    value character varying(50) COLLATE pg_catalog."default" NOT NULL,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone,
    CONSTRAINT languages_pk PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".languages
    OWNER to cicd_pipeline;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".languages TO anveeraprasad;

GRANT ALL ON TABLE "raw".languages TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".languages TO jsharief;

GRANT SELECT ON TABLE "raw".languages TO lizawu;

GRANT SELECT ON TABLE "raw".languages TO readonly_testing;

GRANT ALL ON TABLE "raw".languages TO system_pipeline;