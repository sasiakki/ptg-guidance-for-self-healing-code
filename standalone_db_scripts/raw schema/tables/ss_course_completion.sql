-- Table: raw.ss_course_completion

-- DROP TABLE IF EXISTS "raw".ss_course_completion;

CREATE TABLE IF NOT EXISTS "raw".ss_course_completion
(
    learner_id character varying COLLATE pg_catalog."default",
    first_name character varying(100) COLLATE pg_catalog."default",
    last_name character varying(100) COLLATE pg_catalog."default",
    phone_number character varying(50) COLLATE pg_catalog."default",
    learner_email character varying(50) COLLATE pg_catalog."default",
    attendance character varying(8) COLLATE pg_catalog."default",
    class_id character varying(49) COLLATE pg_catalog."default",
    class_title character varying COLLATE pg_catalog."default",
    date date,
    duration numeric(3,2),
    when_enrolled date,
    instructor character varying(100) COLLATE pg_catalog."default",
    sheet_name character varying(50) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    isdelta boolean NOT NULL DEFAULT false,
    filename character varying(50) COLLATE pg_catalog."default",
    filedate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".ss_course_completion
    OWNER to cicd_pipeline;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "raw".ss_course_completion TO anveeraprasad;

GRANT ALL ON TABLE "raw".ss_course_completion TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".ss_course_completion TO cukaumunna;

GRANT SELECT ON TABLE "raw".ss_course_completion TO eblythe;

GRANT SELECT ON TABLE "raw".ss_course_completion TO htata;

GRANT SELECT ON TABLE "raw".ss_course_completion TO lizawu;

GRANT SELECT ON TABLE "raw".ss_course_completion TO readonly_testing;

GRANT ALL ON TABLE "raw".ss_course_completion TO system_pipeline;