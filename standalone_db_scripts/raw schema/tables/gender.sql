-- Table: raw.gender

-- DROP TABLE IF EXISTS "raw".gender;

CREATE TABLE IF NOT EXISTS "raw".gender
(
    id integer NOT NULL DEFAULT nextval('raw.gender_id_seq'::regclass),
    code character varying(1) COLLATE pg_catalog."default" NOT NULL,
    value character varying(50) COLLATE pg_catalog."default" NOT NULL,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone,
    CONSTRAINT gender_pk PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".gender
    OWNER to cicd_pipeline;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".gender TO anveeraprasad;

GRANT ALL ON TABLE "raw".gender TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".gender TO jsharief;

GRANT SELECT ON TABLE "raw".gender TO lizawu;

GRANT SELECT ON TABLE "raw".gender TO readonly_testing;

GRANT ALL ON TABLE "raw".gender TO system_pipeline;