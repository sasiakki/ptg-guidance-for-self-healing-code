-- Table: raw.qualtrics_transfer_hours

-- DROP TABLE IF EXISTS "raw".qualtrics_transfer_hours;

CREATE TABLE IF NOT EXISTS "raw".qualtrics_transfer_hours
(
    personid character varying(500) COLLATE pg_catalog."default",
    courseid character varying(500) COLLATE pg_catalog."default",
    dshsid character varying(500) COLLATE pg_catalog."default",
    credits character varying(500) COLLATE pg_catalog."default",
    completed timestamp without time zone,
    coursename character varying(500) COLLATE pg_catalog."default",
    instructor character varying(500) COLLATE pg_catalog."default",
    instructorid character varying(500) COLLATE pg_catalog."default",
    source character varying(500) COLLATE pg_catalog."default",
    reason_code character varying(3000) COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    filedate date,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".qualtrics_transfer_hours
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".qualtrics_transfer_hours TO PUBLIC;

GRANT ALL ON TABLE "raw".qualtrics_transfer_hours TO cicd_pipeline;

GRANT SELECT, INSERT ON TABLE "raw".qualtrics_transfer_hours TO readonly_testing;

GRANT ALL ON TABLE "raw".qualtrics_transfer_hours TO system_pipeline;