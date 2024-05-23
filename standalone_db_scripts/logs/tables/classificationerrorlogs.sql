-- Table: logs.classificationerrorlogs

-- DROP TABLE IF EXISTS logs.classificationerrorlogs;

CREATE TABLE IF NOT EXISTS logs.classificationerrorlogs
(
    employeeid character varying(30) COLLATE pg_catalog."default",
    studentname character varying(30) COLLATE pg_catalog."default",
    validationerror character varying(255) COLLATE pg_catalog."default",
    filename character varying(30) COLLATE pg_catalog."default",
    createddate timestamp without time zone,
    sourcekey character varying(255) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.classificationerrorlogs
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE logs.classificationerrorlogs TO anveeraprasad;

GRANT ALL ON TABLE logs.classificationerrorlogs TO cicd_pipeline;

GRANT SELECT ON TABLE logs.classificationerrorlogs TO eblythe;

GRANT SELECT ON TABLE logs.classificationerrorlogs TO htata;

GRANT SELECT ON TABLE logs.classificationerrorlogs TO lizawu;

GRANT SELECT ON TABLE logs.classificationerrorlogs TO readonly_testing;

GRANT ALL ON TABLE logs.classificationerrorlogs TO system_pipeline;