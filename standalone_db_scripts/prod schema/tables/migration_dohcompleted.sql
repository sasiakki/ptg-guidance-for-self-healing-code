-- Table: prod.migration_dohcompleted

-- DROP TABLE IF EXISTS prod.migration_dohcompleted;

CREATE TABLE IF NOT EXISTS prod.migration_dohcompleted
(
    id integer,
    filelastname character varying(255) COLLATE pg_catalog."default",
    filefirstname character varying(255) COLLATE pg_catalog."default",
    filereceiveddate date,
    dohname character varying(255) COLLATE pg_catalog."default",
    credentialnumber character varying(255) COLLATE pg_catalog."default",
    credentialstatus character varying(255) COLLATE pg_catalog."default",
    applicationdate date,
    dateinstructorupdated date,
    approvedinstructorcode character varying(255) COLLATE pg_catalog."default",
    approvedinstructorname character varying(255) COLLATE pg_catalog."default",
    dategraduatedfor70hours date,
    completeddate date,
    examfeepaid character varying(255) COLLATE pg_catalog."default",
    reconciled date,
    reconnotes character varying(255) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone,
    recordcreateddate timestamp without time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.migration_dohcompleted
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.migration_dohcompleted TO PUBLIC;

GRANT ALL ON TABLE prod.migration_dohcompleted TO cicd_pipeline;

GRANT INSERT ON TABLE prod.migration_dohcompleted TO readonly_testing;

GRANT ALL ON TABLE prod.migration_dohcompleted TO system_pipeline;