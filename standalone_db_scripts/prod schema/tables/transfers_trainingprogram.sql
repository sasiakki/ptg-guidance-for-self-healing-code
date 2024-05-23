-- Table: prod.transfers_trainingprogram

-- DROP TABLE IF EXISTS prod.transfers_trainingprogram;

CREATE TABLE IF NOT EXISTS prod.transfers_trainingprogram
(
    trainingprogram character varying COLLATE pg_catalog."default",
    trainingprogramcode character varying COLLATE pg_catalog."default",
    credithours character varying COLLATE pg_catalog."default",
    courseid character varying COLLATE pg_catalog."default",
    isactive boolean
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.transfers_trainingprogram
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.transfers_trainingprogram TO PUBLIC;

GRANT SELECT ON TABLE prod.transfers_trainingprogram TO anveeraprasad;

GRANT ALL ON TABLE prod.transfers_trainingprogram TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE prod.transfers_trainingprogram TO readonly_testing;

GRANT ALL ON TABLE prod.transfers_trainingprogram TO system_pipeline;