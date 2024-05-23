-- Table: prod.coursecatalog

-- DROP TABLE IF EXISTS prod.coursecatalog;

CREATE TABLE IF NOT EXISTS prod.coursecatalog
(
    coursename character varying COLLATE pg_catalog."default",
    credithours character varying COLLATE pg_catalog."default",
    trainingprogramcode character varying COLLATE pg_catalog."default",
    coursetype character varying COLLATE pg_catalog."default",
    courselanguage character varying COLLATE pg_catalog."default",
    courseversion character varying COLLATE pg_catalog."default",
    courseid character varying COLLATE pg_catalog."default",
    dshscourseid character varying COLLATE pg_catalog."default",
    trainingprogramtype character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.coursecatalog
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.coursecatalog TO PUBLIC;

GRANT SELECT ON TABLE prod.coursecatalog TO anveeraprasad;

GRANT ALL ON TABLE prod.coursecatalog TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE prod.coursecatalog TO readonly_testing;

GRANT ALL ON TABLE prod.coursecatalog TO system_pipeline;