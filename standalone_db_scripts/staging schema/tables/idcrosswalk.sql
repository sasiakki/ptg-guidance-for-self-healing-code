-- Table: staging.idcrosswalk

-- DROP TABLE IF EXISTS staging.idcrosswalk;

CREATE TABLE IF NOT EXISTS staging.idcrosswalk
(
    personid bigint,
    dshsid bigint,
    sfngid character varying(255) COLLATE pg_catalog."default",
    fullssn character varying(100) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    cdwaid bigint
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.idcrosswalk
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.idcrosswalk TO anveeraprasad;

GRANT ALL ON TABLE staging.idcrosswalk TO cicd_pipeline;

GRANT SELECT ON TABLE staging.idcrosswalk TO eblythe;

GRANT SELECT ON TABLE staging.idcrosswalk TO htata;

GRANT SELECT ON TABLE staging.idcrosswalk TO lizawu;

GRANT SELECT ON TABLE staging.idcrosswalk TO readonly_testing;

GRANT ALL ON TABLE staging.idcrosswalk TO system_pipeline;