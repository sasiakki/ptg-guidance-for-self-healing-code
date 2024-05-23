-- Table: staging.applyojtperson

-- DROP TABLE IF EXISTS staging.applyojtperson;

CREATE TABLE IF NOT EXISTS staging.applyojtperson
(
    personid bigint
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.applyojtperson
    OWNER to system_pipeline;