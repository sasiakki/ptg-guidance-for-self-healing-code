-- Table: staging.migration_idcrosswalk

-- DROP TABLE IF EXISTS staging.migration_idcrosswalk;

CREATE TABLE IF NOT EXISTS staging.migration_idcrosswalk
(
    personid bigint,
    dshsid bigint,
    sfngid character varying(255) COLLATE pg_catalog."default",
    fullssn character varying(100) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone,
    cdwaid bigint
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.migration_idcrosswalk
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.migration_idcrosswalk TO PUBLIC;

GRANT ALL ON TABLE staging.migration_idcrosswalk TO cicd_pipeline;

GRANT INSERT ON TABLE staging.migration_idcrosswalk TO readonly_testing;

GRANT ALL ON TABLE staging.migration_idcrosswalk TO system_pipeline;