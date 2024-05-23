-- Table: raw.reldoblang

-- DROP TABLE IF EXISTS "raw".reldoblang;

CREATE TABLE IF NOT EXISTS "raw".reldoblang
(
    provider_id bigint,
    student_id bigint,
    social_security_number integer,
    dob character varying(10) COLLATE pg_catalog."default",
    client_relationship_to_ip character varying(19) COLLATE pg_catalog."default",
    preferred_language character varying(37) COLLATE pg_catalog."default",
    cumulative_career_hours numeric(8,2),
    monthly_hours_worked numeric(6,2),
    monthly_hours_worked_month integer,
    ip_contract_expiration_date character varying(10) COLLATE pg_catalog."default",
    termination_type integer,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    termination_date character varying COLLATE pg_catalog."default",
    authorization_start_date character varying COLLATE pg_catalog."default",
    authorization_end_date character varying COLLATE pg_catalog."default",
    last_background_check_date character varying COLLATE pg_catalog."default",
    filemodifieddate timestamp without time zone,
    filename character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".reldoblang
    OWNER to cicd_pipeline;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "raw".reldoblang TO anveeraprasad;

GRANT ALL ON TABLE "raw".reldoblang TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".reldoblang TO cukaumunna;

GRANT SELECT ON TABLE "raw".reldoblang TO eblythe;

GRANT SELECT ON TABLE "raw".reldoblang TO htata;

GRANT SELECT ON TABLE "raw".reldoblang TO lizawu;

GRANT SELECT ON TABLE "raw".reldoblang TO readonly_testing;

GRANT ALL ON TABLE "raw".reldoblang TO system_pipeline;