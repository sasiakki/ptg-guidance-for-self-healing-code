-- Table: logs.smartsheeterrors

-- DROP TABLE IF EXISTS logs.smartsheeterrors;

CREATE TABLE IF NOT EXISTS logs.smartsheeterrors
(
    learner_id character varying COLLATE pg_catalog."default",
    first_name character varying(100) COLLATE pg_catalog."default",
    last_name character varying(100) COLLATE pg_catalog."default",
    phone_number character varying(100) COLLATE pg_catalog."default",
    learner_email character varying(100) COLLATE pg_catalog."default",
    attendance character varying(8) COLLATE pg_catalog."default",
    class_id character varying(49) COLLATE pg_catalog."default",
    class_title character varying COLLATE pg_catalog."default",
    date date,
    duration numeric(3,2),
    when_enrolled date,
    instructor character varying(100) COLLATE pg_catalog."default",
    sheet_name character varying(100) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    error_reason character varying(100) COLLATE pg_catalog."default",
    filename character varying(50) COLLATE pg_catalog."default",
    filedate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.smartsheeterrors
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.smartsheeterrors TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.smartsheeterrors TO readonly_testing;

GRANT ALL ON TABLE logs.smartsheeterrors TO system_pipeline;