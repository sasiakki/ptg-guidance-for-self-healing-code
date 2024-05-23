-- Table: staging.cicd

-- DROP TABLE IF EXISTS staging.cicd;

CREATE TABLE IF NOT EXISTS staging.cicd
(
    id integer,
    name character varying(20) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.cicd
    OWNER to cicd_pipeline;