-- Table: raw.race

-- DROP TABLE IF EXISTS "raw".race;

CREATE TABLE IF NOT EXISTS "raw".race
(
    id integer NOT NULL DEFAULT nextval('raw.race_id_seq'::regclass),
    code character varying(2) COLLATE pg_catalog."default" NOT NULL,
    value character varying(50) COLLATE pg_catalog."default" NOT NULL,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone,
    CONSTRAINT race_pk PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".race
    OWNER to cicd_pipeline;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".race TO anveeraprasad;

GRANT ALL ON TABLE "raw".race TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".race TO jsharief;

GRANT SELECT ON TABLE "raw".race TO lizawu;

GRANT SELECT ON TABLE "raw".race TO readonly_testing;

GRANT ALL ON TABLE "raw".race TO system_pipeline;