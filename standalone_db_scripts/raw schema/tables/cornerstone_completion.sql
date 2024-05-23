-- Table: raw.cornerstone_completion

-- DROP TABLE IF EXISTS "raw".cornerstone_completion;

CREATE TABLE IF NOT EXISTS "raw".cornerstone_completion
(
    offering_title character varying COLLATE pg_catalog."default",
    course_title character varying COLLATE pg_catalog."default",
    user_first_name character varying COLLATE pg_catalog."default",
    user_last_name character varying COLLATE pg_catalog."default",
    user_email character varying COLLATE pg_catalog."default",
    last_login_date timestamp without time zone,
    bg_person_id character varying COLLATE pg_catalog."default",
    course_type character varying COLLATE pg_catalog."default",
    date_of_birth date,
    phone_number character varying COLLATE pg_catalog."default",
    street_1 character varying COLLATE pg_catalog."default",
    street_2 character varying COLLATE pg_catalog."default",
    city character varying COLLATE pg_catalog."default",
    state character varying COLLATE pg_catalog."default",
    postal_code character varying COLLATE pg_catalog."default",
    registered_date timestamp without time zone,
    begin_date timestamp without time zone,
    completed_date timestamp without time zone,
    grade_percentage character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completion_percentage character varying COLLATE pg_catalog."default",
    completion_date timestamp without time zone,
    filename character varying(800) COLLATE pg_catalog."default",
    filedate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".cornerstone_completion
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".cornerstone_completion TO PUBLIC;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".cornerstone_completion TO anveeraprasad;

GRANT ALL ON TABLE "raw".cornerstone_completion TO cicd_pipeline;

GRANT INSERT, SELECT ON TABLE "raw".cornerstone_completion TO readonly_testing;

GRANT ALL ON TABLE "raw".cornerstone_completion TO system_pipeline;