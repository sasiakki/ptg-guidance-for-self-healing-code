-- Table: raw.traininghistory

-- DROP TABLE IF EXISTS "raw".traininghistory;

CREATE TABLE IF NOT EXISTS "raw".traininghistory
(
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
    qual_person_id bigint,
    dshsid bigint,
    trainingsource character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filedate timestamp without time zone,
    dshscourseid character varying COLLATE pg_catalog."default",
    filename character varying(800) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".traininghistory
    OWNER to cicd_pipeline;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "raw".traininghistory TO anveeraprasad;

GRANT ALL ON TABLE "raw".traininghistory TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".traininghistory TO readonly_testing;

GRANT ALL ON TABLE "raw".traininghistory TO system_pipeline;