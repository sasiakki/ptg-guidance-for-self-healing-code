-- Table: eligibility.student_training

-- DROP TABLE IF EXISTS eligibility.student_training;

CREATE TABLE IF NOT EXISTS eligibility.student_training
(
    "studentId" character varying COLLATE pg_catalog."default" NOT NULL,
    training_code character varying COLLATE pg_catalog."default" NOT NULL,
    name character varying COLLATE pg_catalog."default",
    status character varying COLLATE pg_catalog."default" NOT NULL,
    due_date character varying COLLATE pg_catalog."default",
    tracking_date character varying COLLATE pg_catalog."default",
    eligibility_date character varying COLLATE pg_catalog."default",
    start_date character varying COLLATE pg_catalog."default",
    completed_date character varying COLLATE pg_catalog."default",
    training_category character varying COLLATE pg_catalog."default",
    required_hours numeric(5,2),
    earned_hours numeric(5,2),
    transfer_hours numeric(5,2),
    "sfId" character varying COLLATE pg_catalog."default",
    publisher character varying COLLATE pg_catalog."default",
    benefit_continuation_due_date character varying COLLATE pg_catalog."default",
    created character varying COLLATE pg_catalog."default",
    archived character varying COLLATE pg_catalog."default",
    is_required boolean,
    train_id character varying COLLATE pg_catalog."default",
    cc_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    total_hours numeric(5,2),
    reasoncode character varying COLLATE pg_catalog."default",
    CONSTRAINT "PK_f09e1ed76af282b7df523aef18d" PRIMARY KEY (cc_id),
    CONSTRAINT "FK_138d9dcd552b089a8d4c28a16c3" FOREIGN KEY ("studentId")
        REFERENCES eligibility.student (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS eligibility.student_training
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE eligibility.student_training TO anveeraprasad;

GRANT ALL ON TABLE eligibility.student_training TO cicd_pipeline;

GRANT SELECT ON TABLE eligibility.student_training TO eblythe;

GRANT SELECT ON TABLE eligibility.student_training TO htata;

GRANT SELECT ON TABLE eligibility.student_training TO lizawu;

GRANT SELECT ON TABLE eligibility.student_training TO readonly_testing;

GRANT ALL ON TABLE eligibility.student_training TO system_pipeline;