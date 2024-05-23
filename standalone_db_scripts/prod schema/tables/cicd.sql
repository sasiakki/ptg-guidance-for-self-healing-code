-- Table: prod.cicd

-- DROP TABLE IF EXISTS prod.cicd;

CREATE TABLE IF NOT EXISTS prod.cicd
(
    id integer,
    name character varying(20) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.cicd
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.cicd TO PUBLIC;

GRANT ALL ON TABLE prod.cicd TO cicd_pipeline;

GRANT INSERT, SELECT ON TABLE prod.cicd TO readonly_testing;

GRANT ALL ON TABLE prod.cicd TO system_pipeline;