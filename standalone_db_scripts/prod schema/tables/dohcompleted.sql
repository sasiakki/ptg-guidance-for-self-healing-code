-- Table: prod.dohcompleted

-- DROP TABLE IF EXISTS prod.dohcompleted;

CREATE TABLE IF NOT EXISTS prod.dohcompleted
(
    id integer NOT NULL DEFAULT nextval('prod.dohcompleted_id_seq'::regclass),
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
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT dohcompleted_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.dohcompleted
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.dohcompleted TO PUBLIC;

GRANT SELECT ON TABLE prod.dohcompleted TO anveeraprasad;

GRANT ALL ON TABLE prod.dohcompleted TO cicd_pipeline;

GRANT INSERT ON TABLE prod.dohcompleted TO readonly_testing;

GRANT ALL ON TABLE prod.dohcompleted TO system_pipeline;