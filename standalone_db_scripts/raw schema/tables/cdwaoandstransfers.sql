-- Table: raw.cdwaoandstransfers

-- DROP TABLE IF EXISTS "raw".cdwaoandstransfers;

CREATE TABLE IF NOT EXISTS "raw".cdwaoandstransfers
(
    employeeid bigint,
    personid bigint,
    trainingprogram character varying COLLATE pg_catalog."default",
    classname character varying COLLATE pg_catalog."default",
    dshscoursecode character varying COLLATE pg_catalog."default",
    credithours character varying COLLATE pg_catalog."default",
    completeddate date,
    trainingentity character varying COLLATE pg_catalog."default",
    reasonfortransfer character varying COLLATE pg_catalog."default",
    employerstaff character varying COLLATE pg_catalog."default",
    createddate date,
    filename character varying COLLATE pg_catalog."default",
    filedate date,
    isvalid boolean DEFAULT false,
    error_message character varying COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".cdwaoandstransfers
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".cdwaoandstransfers TO PUBLIC;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".cdwaoandstransfers TO anveeraprasad;

GRANT ALL ON TABLE "raw".cdwaoandstransfers TO cicd_pipeline;

GRANT INSERT, SELECT ON TABLE "raw".cdwaoandstransfers TO readonly_testing;

GRANT ALL ON TABLE "raw".cdwaoandstransfers TO system_pipeline;