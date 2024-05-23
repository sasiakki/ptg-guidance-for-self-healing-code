-- Table: eligibility.check_person

-- DROP TABLE IF EXISTS eligibility.check_person;

CREATE TABLE IF NOT EXISTS eligibility.check_person
(
    pgc_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    personid bigint NOT NULL,
    type character varying COLLATE pg_catalog."default",
    credentialstatus character varying COLLATE pg_catalog."default",
    firstissuance character varying COLLATE pg_catalog."default",
    expiration character varying COLLATE pg_catalog."default",
    workercategory character varying COLLATE pg_catalog."default",
    categorycode character varying COLLATE pg_catalog."default",
    hiredate timestamp without time zone,
    exempt character varying COLLATE pg_catalog."default",
    ahcas_eligible boolean,
    trackingdate timestamp without time zone,
    empstatus character varying COLLATE pg_catalog."default",
    dob character varying COLLATE pg_catalog."default",
    language1 character varying COLLATE pg_catalog."default",
    check_stat integer DEFAULT 0,
    rehiredate character varying COLLATE pg_catalog."default",
    last_termination_date character varying COLLATE pg_catalog."default",
    CONSTRAINT "PK_843b2e1b2f0cade1226ab9c4b0e" PRIMARY KEY (pgc_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS eligibility.check_person
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE eligibility.check_person TO anveeraprasad;

GRANT ALL ON TABLE eligibility.check_person TO cicd_pipeline;

GRANT SELECT ON TABLE eligibility.check_person TO eblythe;

GRANT SELECT ON TABLE eligibility.check_person TO htata;

GRANT SELECT ON TABLE eligibility.check_person TO lizawu;

GRANT SELECT ON TABLE eligibility.check_person TO readonly_testing;

GRANT ALL ON TABLE eligibility.check_person TO system_pipeline;