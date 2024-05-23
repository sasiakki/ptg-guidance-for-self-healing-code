-- Table: staging.learningpath_updates

-- DROP TABLE IF EXISTS staging.learningpath_updates;

CREATE TABLE IF NOT EXISTS staging.learningpath_updates
(
    transcriptid bigint,
    personid bigint,
    trainingprogramcode character varying COLLATE pg_catalog."default",
    trainingid character varying COLLATE pg_catalog."default",
    learningpath character varying(10) COLLATE pg_catalog."default",
    completeddate date,
    status character varying(10) COLLATE pg_catalog."default",
    earnedhours numeric(5,2)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.learningpath_updates
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.learningpath_updates TO PUBLIC;

GRANT ALL ON TABLE staging.learningpath_updates TO cicd_pipeline;

GRANT INSERT, SELECT ON TABLE staging.learningpath_updates TO readonly_testing;

GRANT ALL ON TABLE staging.learningpath_updates TO system_pipeline;