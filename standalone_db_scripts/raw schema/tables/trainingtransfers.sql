-- Table: raw.trainingtransfers

-- DROP TABLE IF EXISTS "raw".trainingtransfers;

CREATE TABLE IF NOT EXISTS "raw".trainingtransfers
(
    employeeid character varying COLLATE pg_catalog."default",
    personid character varying COLLATE pg_catalog."default",
    trainingprogram character varying COLLATE pg_catalog."default",
    classname character varying COLLATE pg_catalog."default",
    dshscoursecode character varying COLLATE pg_catalog."default",
    credithours character varying COLLATE pg_catalog."default",
    completeddate character varying COLLATE pg_catalog."default",
    trainingentity character varying COLLATE pg_catalog."default",
    reasonfortransfer character varying COLLATE pg_catalog."default",
    employerstaff character varying COLLATE pg_catalog."default",
    createddate character varying COLLATE pg_catalog."default",
    filename character varying COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    filemodifieddate date
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".trainingtransfers
    OWNER to cicd_pipeline;

GRANT UPDATE, INSERT, SELECT, DELETE ON TABLE "raw".trainingtransfers TO anveeraprasad;

GRANT ALL ON TABLE "raw".trainingtransfers TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".trainingtransfers TO lizawu;

GRANT SELECT ON TABLE "raw".trainingtransfers TO readonly_testing;

GRANT ALL ON TABLE "raw".trainingtransfers TO system_pipeline;