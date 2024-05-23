-- Table: raw.doceboilt_course_completion

-- DROP TABLE IF EXISTS "raw".doceboilt_course_completion;

CREATE TABLE IF NOT EXISTS "raw".doceboilt_course_completion
(
    username character varying COLLATE pg_catalog."default",
    firstname character varying COLLATE pg_catalog."default",
    lastname character varying COLLATE pg_catalog."default",
    trainingid character varying COLLATE pg_catalog."default",
    coursename character varying COLLATE pg_catalog."default",
    coursecode character varying COLLATE pg_catalog."default",
    credits character varying COLLATE pg_catalog."default",
    dshscode character varying COLLATE pg_catalog."default",
    sessioninstructor character varying COLLATE pg_catalog."default",
    sessionname character varying COLLATE pg_catalog."default",
    eventinstructor character varying COLLATE pg_catalog."default",
    completiondate character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filename character varying COLLATE pg_catalog."default",
    filedate date,
    isdelta boolean NOT NULL DEFAULT false
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".doceboilt_course_completion
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".doceboilt_course_completion TO PUBLIC;

GRANT ALL ON TABLE "raw".doceboilt_course_completion TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE "raw".doceboilt_course_completion TO readonly_testing;

GRANT ALL ON TABLE "raw".doceboilt_course_completion TO system_pipeline;