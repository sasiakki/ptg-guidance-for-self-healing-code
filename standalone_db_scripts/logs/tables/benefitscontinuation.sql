-- Table: logs.benefitscontinuation

-- DROP TABLE IF EXISTS logs.benefitscontinuation;

CREATE TABLE IF NOT EXISTS logs.benefitscontinuation
(
    personid bigint NOT NULL,
    employerrequested text COLLATE pg_catalog."default",
    duedateoverride timestamp without time zone,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    duedateoverridereason character varying COLLATE pg_catalog."default" NOT NULL,
    error_reason text COLLATE pg_catalog."default",
    bcapproveddate timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.benefitscontinuation
    OWNER to cicd_pipeline;

GRANT ALL ON TABLE logs.benefitscontinuation TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE logs.benefitscontinuation TO readonly_testing;

GRANT ALL ON TABLE logs.benefitscontinuation TO system_pipeline;