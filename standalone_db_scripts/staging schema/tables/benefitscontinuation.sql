-- Table: staging.benefitscontinuation

-- DROP TABLE IF EXISTS staging.benefitscontinuation;

CREATE TABLE IF NOT EXISTS staging.benefitscontinuation
(
    personid bigint NOT NULL,
    employerrequested character varying COLLATE pg_catalog."default" NOT NULL,
    duedateoverride timestamp without time zone,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    firstname character varying COLLATE pg_catalog."default",
    lastname character varying COLLATE pg_catalog."default",
    email character varying COLLATE pg_catalog."default",
    duedateoverridereason character varying COLLATE pg_catalog."default",
    file_source character varying COLLATE pg_catalog."default",
    trainingname character varying COLLATE pg_catalog."default",
    bcapproveddate timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS staging.benefitscontinuation
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE staging.benefitscontinuation TO PUBLIC;

GRANT ALL ON TABLE staging.benefitscontinuation TO cicd_pipeline;

GRANT INSERT, SELECT ON TABLE staging.benefitscontinuation TO readonly_testing;

GRANT ALL ON TABLE staging.benefitscontinuation TO system_pipeline;