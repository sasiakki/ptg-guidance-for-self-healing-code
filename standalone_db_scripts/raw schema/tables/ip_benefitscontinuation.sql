-- Table: raw.ip_benefitscontinuation

-- DROP TABLE IF EXISTS "raw".ip_benefitscontinuation;

CREATE TABLE IF NOT EXISTS "raw".ip_benefitscontinuation
(
    bgpersonid character varying(50) COLLATE pg_catalog."default" NOT NULL,
    employerrequested character varying(50) COLLATE pg_catalog."default" NOT NULL,
    firstname character varying(50) COLLATE pg_catalog."default",
    lastname character varying(50) COLLATE pg_catalog."default",
    email character varying(50) COLLATE pg_catalog."default",
    bcapproveddate timestamp without time zone,
    duedateoverridereason character varying(100) COLLATE pg_catalog."default" NOT NULL,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    trainingname character varying COLLATE pg_catalog."default",
    duedateoverride timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".ip_benefitscontinuation
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".ip_benefitscontinuation TO PUBLIC;

GRANT ALL ON TABLE "raw".ip_benefitscontinuation TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE "raw".ip_benefitscontinuation TO readonly_testing;

GRANT ALL ON TABLE "raw".ip_benefitscontinuation TO system_pipeline;