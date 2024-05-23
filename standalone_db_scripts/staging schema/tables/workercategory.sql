-- Table: staging.workercategory

-- DROP TABLE IF EXISTS staging.workercategory;

CREATE TABLE IF NOT EXISTS staging.workercategory
(
    workercode character varying(10) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    workercategory character varying(100) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    tccode character varying(10) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    priority integer,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.workercategory
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.workercategory TO anveeraprasad;

GRANT ALL ON TABLE staging.workercategory TO cicd_pipeline;

GRANT SELECT ON TABLE staging.workercategory TO eblythe;

GRANT SELECT ON TABLE staging.workercategory TO htata;

GRANT SELECT ON TABLE staging.workercategory TO lizawu;

GRANT SELECT ON TABLE staging.workercategory TO readonly_testing;

GRANT ALL ON TABLE staging.workercategory TO system_pipeline;