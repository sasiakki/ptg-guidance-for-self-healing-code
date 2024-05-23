-- Table: prod.duedateextension

-- DROP TABLE IF EXISTS prod.duedateextension;

CREATE TABLE IF NOT EXISTS prod.duedateextension
(
    personid bigint NOT NULL,
    employerrequested character varying COLLATE pg_catalog."default",
    duedateoverride timestamp without time zone,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    duedateoverridereason character varying COLLATE pg_catalog."default" NOT NULL,
    bcapproveddate timestamp without time zone,
    trainingid character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.duedateextension
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.duedateextension TO PUBLIC;

GRANT ALL ON TABLE prod.duedateextension TO cicd_pipeline;

GRANT INSERT ON TABLE prod.duedateextension TO readonly_testing;

GRANT ALL ON TABLE prod.duedateextension TO system_pipeline;