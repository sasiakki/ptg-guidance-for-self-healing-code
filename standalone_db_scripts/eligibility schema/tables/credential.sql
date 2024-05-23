-- Table: eligibility.credential

-- DROP TABLE IF EXISTS eligibility.credential;

CREATE TABLE IF NOT EXISTS eligibility.credential
(
    name character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default",
    "firstIssuance_date" character varying COLLATE pg_catalog."default",
    expiration_date character varying COLLATE pg_catalog."default",
    credential_number character varying COLLATE pg_catalog."default" NOT NULL,
    "studentId" character varying COLLATE pg_catalog."default",
    cred_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    CONSTRAINT "PK_8da5f6a4285f56e31873c735740" PRIMARY KEY (cred_id),
    CONSTRAINT "FK_3893416ba91a9d1bd50d3d1e60c" FOREIGN KEY ("studentId")
        REFERENCES eligibility.student (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS eligibility.credential
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE eligibility.credential TO anveeraprasad;

GRANT ALL ON TABLE eligibility.credential TO cicd_pipeline;

GRANT SELECT ON TABLE eligibility.credential TO eblythe;

GRANT SELECT ON TABLE eligibility.credential TO htata;

GRANT SELECT ON TABLE eligibility.credential TO lizawu;

GRANT SELECT ON TABLE eligibility.credential TO readonly_testing;

GRANT ALL ON TABLE eligibility.credential TO system_pipeline;