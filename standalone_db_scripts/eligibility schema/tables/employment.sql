-- Table: eligibility.employment

-- DROP TABLE IF EXISTS eligibility.employment;

CREATE TABLE IF NOT EXISTS eligibility.employment
(
    name character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default" NOT NULL,
    hire_date character varying COLLATE pg_catalog."default" NOT NULL,
    terminate_date character varying COLLATE pg_catalog."default",
    authentication_date character varying COLLATE pg_catalog."default",
    training_category character varying COLLATE pg_catalog."default" NOT NULL,
    ignore_assigned_category boolean DEFAULT false,
    emp_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    "studentId" character varying COLLATE pg_catalog."default",
    rehire_date character varying COLLATE pg_catalog."default",
    CONSTRAINT "PK_be42aea4587be57510e91191637" PRIMARY KEY (emp_id),
    CONSTRAINT "FK_123f3e87eef17e04e8785bd39d9" FOREIGN KEY ("studentId")
        REFERENCES eligibility.student (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS eligibility.employment
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE eligibility.employment TO anveeraprasad;

GRANT ALL ON TABLE eligibility.employment TO cicd_pipeline;

GRANT SELECT ON TABLE eligibility.employment TO eblythe;

GRANT SELECT ON TABLE eligibility.employment TO htata;

GRANT SELECT ON TABLE eligibility.employment TO lizawu;

GRANT SELECT ON TABLE eligibility.employment TO readonly_testing;

GRANT ALL ON TABLE eligibility.employment TO system_pipeline;