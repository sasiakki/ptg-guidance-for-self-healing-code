-- Table: eligibility.student

-- DROP TABLE IF EXISTS eligibility.student;

CREATE TABLE IF NOT EXISTS eligibility.student
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    provider_id character varying COLLATE pg_catalog."default",
    first_name character varying COLLATE pg_catalog."default",
    last_name character varying COLLATE pg_catalog."default",
    training_status character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default",
    publisher character varying COLLATE pg_catalog."default",
    active_training character varying COLLATE pg_catalog."default",
    assigned_category character varying COLLATE pg_catalog."default",
    num_active_emp integer,
    prefer_language character varying COLLATE pg_catalog."default",
    birth_date character varying COLLATE pg_catalog."default",
    CONSTRAINT "PK_3d8016e1cb58429474a3c041904" PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS eligibility.student
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE eligibility.student TO anveeraprasad;

GRANT ALL ON TABLE eligibility.student TO cicd_pipeline;

GRANT SELECT ON TABLE eligibility.student TO eblythe;

GRANT SELECT ON TABLE eligibility.student TO htata;

GRANT SELECT ON TABLE eligibility.student TO lizawu;

GRANT SELECT ON TABLE eligibility.student TO readonly_testing;

GRANT ALL ON TABLE eligibility.student TO system_pipeline;