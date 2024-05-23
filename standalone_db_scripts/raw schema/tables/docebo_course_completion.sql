-- Table: raw.docebo_course_completion

-- DROP TABLE IF EXISTS "raw".docebo_course_completion;

CREATE TABLE IF NOT EXISTS "raw".docebo_course_completion
(
    username bigint,
    firstname character varying COLLATE pg_catalog."default",
    lastname character varying COLLATE pg_catalog."default",
    coursecode character varying COLLATE pg_catalog."default",
    coursetype character varying COLLATE pg_catalog."default",
    coursename character varying COLLATE pg_catalog."default",
    firstaccessdate character varying COLLATE pg_catalog."default",
    completiondate character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default",
    credithours character varying COLLATE pg_catalog."default",
    dshsid character varying COLLATE pg_catalog."default",
    cdwaid character varying COLLATE pg_catalog."default",
    trainingid character varying COLLATE pg_catalog."default",
    dshscode character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    filedate timestamp without time zone,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".docebo_course_completion
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".docebo_course_completion TO PUBLIC;

GRANT ALL ON TABLE "raw".docebo_course_completion TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE "raw".docebo_course_completion TO readonly_testing;

GRANT ALL ON TABLE "raw".docebo_course_completion TO system_pipeline;