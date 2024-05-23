-- Table: raw.cdwa

-- DROP TABLE IF EXISTS "raw".cdwa;

CREATE TABLE IF NOT EXISTS "raw".cdwa
(
    employee_id numeric(9,0),
    personid character varying(10) COLLATE pg_catalog."default",
    first_name character varying(50) COLLATE pg_catalog."default",
    middle_name character varying(50) COLLATE pg_catalog."default",
    last_name character varying(100) COLLATE pg_catalog."default",
    ssn character varying COLLATE pg_catalog."default",
    dob integer,
    gender character varying(1) COLLATE pg_catalog."default",
    race character varying(50) COLLATE pg_catalog."default",
    language character varying(5) COLLATE pg_catalog."default",
    marital_status character varying(20) COLLATE pg_catalog."default",
    phone_1 numeric(10,0),
    phone_2 numeric(10,0),
    email character varying(150) COLLATE pg_catalog."default",
    mailing_add_1 character varying(150) COLLATE pg_catalog."default",
    mailing_add_2 character varying(150) COLLATE pg_catalog."default",
    mailing_city character varying(150) COLLATE pg_catalog."default",
    mailing_state character varying(2) COLLATE pg_catalog."default",
    mailing_zip character varying(10) COLLATE pg_catalog."default",
    physical_add_1 character varying(150) COLLATE pg_catalog."default",
    physical_add_2 character varying(150) COLLATE pg_catalog."default",
    physical_city character varying(150) COLLATE pg_catalog."default",
    physical_state character varying(2) COLLATE pg_catalog."default",
    physical_zip character varying(10) COLLATE pg_catalog."default",
    employee_classification character varying(100) COLLATE pg_catalog."default",
    exempt_status character varying(5) COLLATE pg_catalog."default",
    background_check_date integer,
    ie_date integer,
    hire_date integer,
    classification_start_date integer,
    carina_eligible character varying(5) COLLATE pg_catalog."default",
    ahcas_eligible character varying(5) COLLATE pg_catalog."default",
    os_completed integer,
    termination_date integer,
    authorized_start_date integer,
    authorized_end_date integer,
    client_count numeric(2,0),
    client_relationship character varying(50) COLLATE pg_catalog."default",
    client_id character varying(20) COLLATE pg_catalog."default",
    isvalid boolean DEFAULT false,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    error_message character varying COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    filename character varying(60) COLLATE pg_catalog."default",
    ethnicity character varying(50) COLLATE pg_catalog."default",
    filemodifieddate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".cdwa
    OWNER to cicd_pipeline;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "raw".cdwa TO anveeraprasad;

GRANT ALL ON TABLE "raw".cdwa TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".cdwa TO cukaumunna;

GRANT SELECT ON TABLE "raw".cdwa TO eblythe;

GRANT SELECT ON TABLE "raw".cdwa TO htata;

GRANT SELECT ON TABLE "raw".cdwa TO lizawu;

GRANT SELECT ON TABLE "raw".cdwa TO readonly_testing;

GRANT ALL ON TABLE "raw".cdwa TO system_pipeline;