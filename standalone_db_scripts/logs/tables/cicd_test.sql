-- Table: logs.cicd_test

-- DROP TABLE IF EXISTS logs.cicd_test;

CREATE TABLE IF NOT EXISTS logs.cicd_test
(
    numberofrows integer,
    filesize integer,
    processeddate date,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.cicd_test
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.cicd_test TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.cicd_test TO readonly_testing;

GRANT ALL ON TABLE logs.cicd_test TO system_pipeline;