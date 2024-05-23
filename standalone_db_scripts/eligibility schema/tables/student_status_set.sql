-- Table: eligibility.student_status_set

-- DROP TABLE IF EXISTS eligibility.student_status_set;

CREATE TABLE IF NOT EXISTS eligibility.student_status_set
(
    "studentId" character varying COLLATE pg_catalog."default" NOT NULL,
    "isCompliant" boolean,
    "isGrandFathered" boolean,
    ahcas_eligible boolean,
    "complianceStatus" character varying COLLATE pg_catalog."default",
    CONSTRAINT "PK_ab8674006bee35aee2db63e4484" PRIMARY KEY ("studentId")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS eligibility.student_status_set
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE eligibility.student_status_set TO anveeraprasad;

GRANT ALL ON TABLE eligibility.student_status_set TO cicd_pipeline;

GRANT SELECT ON TABLE eligibility.student_status_set TO eblythe;

GRANT SELECT ON TABLE eligibility.student_status_set TO htata;

GRANT SELECT ON TABLE eligibility.student_status_set TO lizawu;

GRANT SELECT ON TABLE eligibility.student_status_set TO readonly_testing;

GRANT ALL ON TABLE eligibility.student_status_set TO system_pipeline;