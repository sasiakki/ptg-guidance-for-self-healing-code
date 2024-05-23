-- Table: raw.dohcompleted

-- DROP TABLE IF EXISTS "raw".dohcompleted;

CREATE TABLE IF NOT EXISTS "raw".dohcompleted
(
    filelastname character varying(255) COLLATE pg_catalog."default",
    filefirstname character varying(255) COLLATE pg_catalog."default",
    filereceiveddate character varying(255) COLLATE pg_catalog."default",
    dohname character varying(255) COLLATE pg_catalog."default",
    credentialnumber character varying(255) COLLATE pg_catalog."default",
    credentialstatus character varying(255) COLLATE pg_catalog."default",
    applicationdate character varying(255) COLLATE pg_catalog."default",
    dateapprovedinstructorcodeandnameudfupdated character varying(255) COLLATE pg_catalog."default",
    approvedinstructorcodeandname character varying(255) COLLATE pg_catalog."default",
    dategraduatedfor70hours character varying(255) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone,
    filename character varying(100) COLLATE pg_catalog."default",
    filedate timestamp without time zone,
    examfeepaid character varying(1000) COLLATE pg_catalog."default",
    reconciled character varying(1000) COLLATE pg_catalog."default",
    reconnotes character varying(1000) COLLATE pg_catalog."default",
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "raw".dohcompleted
    OWNER to cicd_pipeline;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "raw".dohcompleted TO anveeraprasad;

GRANT ALL ON TABLE "raw".dohcompleted TO cicd_pipeline;

GRANT SELECT ON TABLE "raw".dohcompleted TO readonly_testing;

GRANT ALL ON TABLE "raw".dohcompleted TO system_pipeline;