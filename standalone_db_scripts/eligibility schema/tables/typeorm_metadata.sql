-- Table: eligibility.typeorm_metadata

-- DROP TABLE IF EXISTS eligibility.typeorm_metadata;

CREATE TABLE IF NOT EXISTS eligibility.typeorm_metadata
(
    type character varying COLLATE pg_catalog."default" NOT NULL,
    database character varying COLLATE pg_catalog."default",
    schema character varying COLLATE pg_catalog."default",
    "table" character varying COLLATE pg_catalog."default",
    name character varying COLLATE pg_catalog."default",
    value text COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS eligibility.typeorm_metadata
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE eligibility.typeorm_metadata TO anveeraprasad;

GRANT ALL ON TABLE eligibility.typeorm_metadata TO cicd_pipeline;

GRANT SELECT ON TABLE eligibility.typeorm_metadata TO eblythe;

GRANT SELECT ON TABLE eligibility.typeorm_metadata TO htata;

GRANT SELECT ON TABLE eligibility.typeorm_metadata TO lizawu;

GRANT SELECT ON TABLE eligibility.typeorm_metadata TO readonly_testing;

GRANT ALL ON TABLE eligibility.typeorm_metadata TO system_pipeline;