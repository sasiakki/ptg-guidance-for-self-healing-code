-- Table: staging.traininghistory

-- DROP TABLE IF EXISTS staging.traininghistory;

CREATE TABLE IF NOT EXISTS staging.traininghistory
(
    traininghistoryid bigint NOT NULL DEFAULT nextval('staging.traininghistory_id_seq'::regclass),
    personid bigint,
    coursename character varying COLLATE pg_catalog."default",
    courseid character varying COLLATE pg_catalog."default",
    completeddate date,
    credithours double precision,
    trainingprogramcode bigint,
    trainingprogramtype character varying COLLATE pg_catalog."default",
    courselanguage character varying COLLATE pg_catalog."default",
    coursetype character varying COLLATE pg_catalog."default",
    instructorname character varying COLLATE pg_catalog."default",
    instructorid character varying COLLATE pg_catalog."default",
    trainingsource character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dshscourseid character varying COLLATE pg_catalog."default",
    learningpath character varying(20) COLLATE pg_catalog."default",
    islearningpathchanged boolean,
    filename character varying(800) COLLATE pg_catalog."default",
    filedate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.traininghistory
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.traininghistory TO PUBLIC;

GRANT SELECT ON TABLE staging.traininghistory TO anveeraprasad;

GRANT ALL ON TABLE staging.traininghistory TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE staging.traininghistory TO readonly_testing;

GRANT ALL ON TABLE staging.traininghistory TO system_pipeline;