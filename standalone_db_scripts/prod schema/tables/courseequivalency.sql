-- Table: prod.courseequivalency

-- DROP TABLE IF EXISTS prod.courseequivalency;

CREATE TABLE IF NOT EXISTS prod.courseequivalency
(
    courseid character varying(20) COLLATE pg_catalog."default",
    trainingprogramcode character varying(20) COLLATE pg_catalog."default",
    trainingprogramtype character varying(20) COLLATE pg_catalog."default",
    learningpath character varying(20) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.courseequivalency
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.courseequivalency TO PUBLIC;

GRANT ALL ON TABLE prod.courseequivalency TO cicd_pipeline;

GRANT INSERT ON TABLE prod.courseequivalency TO readonly_testing;

GRANT ALL ON TABLE prod.courseequivalency TO system_pipeline;