-- Table: staging.learner

-- DROP TABLE IF EXISTS staging.learner;

CREATE TABLE IF NOT EXISTS staging.learner
(
    personid bigint NOT NULL,
    benefitscontinuation boolean,
    orientationandsafetycomplete date,
    compliant character varying COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    requiredtraining character varying COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    archived timestamp without time zone,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    learnerid uuid NOT NULL DEFAULT uuid_generate_v4(),
    CONSTRAINT learnertest_pkey PRIMARY KEY (personid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.learner
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.learner TO anveeraprasad;

GRANT ALL ON TABLE staging.learner TO cicd_pipeline;

GRANT SELECT ON TABLE staging.learner TO eblythe;

GRANT SELECT ON TABLE staging.learner TO htata;

GRANT SELECT ON TABLE staging.learner TO lizawu;

GRANT SELECT ON TABLE staging.learner TO readonly_testing;

GRANT ALL ON TABLE staging.learner TO system_pipeline;