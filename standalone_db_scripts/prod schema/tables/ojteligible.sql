-- Table: prod.ojteligible

-- DROP TABLE IF EXISTS prod.ojteligible;

CREATE TABLE IF NOT EXISTS prod.ojteligible
(
    personid bigint,
    appliedhours numeric(5,2),
    pendinghours numeric(5,2),
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.ojteligible
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.ojteligible TO PUBLIC;

GRANT SELECT ON TABLE prod.ojteligible TO anveeraprasad;

GRANT ALL ON TABLE prod.ojteligible TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE prod.ojteligible TO readonly_testing;

GRANT ALL ON TABLE prod.ojteligible TO system_pipeline;