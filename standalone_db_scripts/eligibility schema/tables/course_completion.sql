-- Table: eligibility.course_completion

-- DROP TABLE IF EXISTS eligibility.course_completion;

CREATE TABLE IF NOT EXISTS eligibility.course_completion
(
    name character varying COLLATE pg_catalog."default" NOT NULL,
    status character varying COLLATE pg_catalog."default",
    completed_date character varying COLLATE pg_catalog."default",
    publisher character varying COLLATE pg_catalog."default",
    "sfId" character varying COLLATE pg_catalog."default",
    "studentId" character varying COLLATE pg_catalog."default",
    cc_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    personid bigint NOT NULL,
    CONSTRAINT "PK_f7a5d161280c6878fd25e0358ea" PRIMARY KEY (cc_id),
    CONSTRAINT "FK_14cdf9fc082be33e10feb1805df" FOREIGN KEY ("studentId")
        REFERENCES eligibility.student (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS eligibility.course_completion
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE eligibility.course_completion TO anveeraprasad;

GRANT ALL ON TABLE eligibility.course_completion TO cicd_pipeline;

GRANT SELECT ON TABLE eligibility.course_completion TO eblythe;

GRANT SELECT ON TABLE eligibility.course_completion TO htata;

GRANT SELECT ON TABLE eligibility.course_completion TO lizawu;

GRANT SELECT ON TABLE eligibility.course_completion TO readonly_testing;

GRANT ALL ON TABLE eligibility.course_completion TO system_pipeline;