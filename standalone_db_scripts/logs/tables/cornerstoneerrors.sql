-- Table: logs.cornerstoneerrors

-- DROP TABLE IF EXISTS logs.cornerstoneerrors;

CREATE TABLE IF NOT EXISTS logs.cornerstoneerrors
(
    id bigint NOT NULL DEFAULT nextval('logs.cornerstoneerrors_id_seq'::regclass),
    student_first_name character varying(120) COLLATE pg_catalog."default",
    student_last_name character varying(120) COLLATE pg_catalog."default",
    offering_title character varying(255) COLLATE pg_catalog."default",
    course_title character varying(150) COLLATE pg_catalog."default",
    student_email character varying(255) COLLATE pg_catalog."default",
    registered_date character varying(255) COLLATE pg_catalog."default",
    begin_date character varying(255) COLLATE pg_catalog."default",
    completion_date character varying(255) COLLATE pg_catalog."default",
    last_active_date character varying(255) COLLATE pg_catalog."default",
    grade character varying(10) COLLATE pg_catalog."default",
    status character varying(25) COLLATE pg_catalog."default",
    completion_percentage character varying(25) COLLATE pg_catalog."default",
    completed_date character varying(255) COLLATE pg_catalog."default",
    course_type character varying(50) COLLATE pg_catalog."default",
    bg_person_id character varying(50) COLLATE pg_catalog."default",
    date_of_birth date,
    phone_number character varying(255) COLLATE pg_catalog."default",
    street_1 character varying(255) COLLATE pg_catalog."default",
    street_2 character varying(255) COLLATE pg_catalog."default",
    city character varying(55) COLLATE pg_catalog."default",
    state character varying(55) COLLATE pg_catalog."default",
    postal_code character varying(100) COLLATE pg_catalog."default",
    filename character varying(255) COLLATE pg_catalog."default",
    filedate date,
    error_reason character varying COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.cornerstoneerrors
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.cornerstoneerrors TO cicd_pipeline;

GRANT ALL ON TABLE logs.cornerstoneerrors TO readonly_testing;

GRANT ALL ON TABLE logs.cornerstoneerrors TO system_pipeline;