-- Table: prod.migration_ojteligible

-- DROP TABLE IF EXISTS prod.migration_ojteligible;

CREATE TABLE IF NOT EXISTS prod.migration_ojteligible
(
    personid bigint,
    appliedhours numeric(5,2),
    pendinghours numeric(5,2),
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.migration_ojteligible
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.migration_ojteligible TO PUBLIC;

GRANT ALL ON TABLE prod.migration_ojteligible TO cicd_pipeline;

GRANT INSERT ON TABLE prod.migration_ojteligible TO readonly_testing;

GRANT ALL ON TABLE prod.migration_ojteligible TO system_pipeline;