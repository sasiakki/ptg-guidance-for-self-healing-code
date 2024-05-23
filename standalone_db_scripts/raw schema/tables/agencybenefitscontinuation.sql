-- Table: raw.agencybenefitscontinuation

-- DROP TABLE IF EXISTS "raw".agencybenefitscontinuation;

CREATE TABLE IF NOT EXISTS "raw".agencybenefitscontinuation
(
    bgpersonid character varying(12) COLLATE pg_catalog."default" NOT NULL,
    employerrequested character varying(50) COLLATE pg_catalog."default" NOT NULL,
    firstname character varying(50) COLLATE pg_catalog."default",
    lastname character varying(50) COLLATE pg_catalog."default",
    email character varying(50) COLLATE pg_catalog."default",
    bcapproveddate timestamp without time zone,
    duedateoverridereason character varying(50) COLLATE pg_catalog."default" NOT NULL,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    trainingname character varying COLLATE pg_catalog."default",
    duedateoverride timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".agencybenefitscontinuation
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".agencybenefitscontinuation TO PUBLIC;

GRANT ALL ON TABLE "raw".agencybenefitscontinuation TO cicd_pipeline;

GRANT INSERT, SELECT ON TABLE "raw".agencybenefitscontinuation TO readonly_testing;

GRANT ALL ON TABLE "raw".agencybenefitscontinuation TO system_pipeline;