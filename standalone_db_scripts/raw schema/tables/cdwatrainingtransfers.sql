-- Table: raw.cdwatrainingtransfers

-- DROP TABLE IF EXISTS "raw".cdwatrainingtransfers;

CREATE TABLE IF NOT EXISTS "raw".cdwatrainingtransfers
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
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".cdwatrainingtransfers
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE "raw".cdwatrainingtransfers TO PUBLIC;

GRANT DELETE, INSERT, SELECT, UPDATE ON TABLE "raw".cdwatrainingtransfers TO anveeraprasad;

GRANT ALL ON TABLE "raw".cdwatrainingtransfers TO cicd_pipeline;

GRANT INSERT, SELECT ON TABLE "raw".cdwatrainingtransfers TO readonly_testing;

GRANT ALL ON TABLE "raw".cdwatrainingtransfers TO system_pipeline;