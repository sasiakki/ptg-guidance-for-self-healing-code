-- Table: prod.dohclassified

-- DROP TABLE IF EXISTS prod.dohclassified;

CREATE TABLE IF NOT EXISTS prod.dohclassified
(
    id integer NOT NULL DEFAULT nextval('prod.dohclassified_id_seq'::regclass),
    filelastname character varying(255) COLLATE pg_catalog."default",
    filefirstname character varying(255) COLLATE pg_catalog."default",
    filereceiveddate date,
    dohname character varying(255) COLLATE pg_catalog."default",
    credentialnumber character varying(255) COLLATE pg_catalog."default",
    credentialstatus character varying(255) COLLATE pg_catalog."default",
    applicationdate date,
    datedshsbenefitpaymentudfupdated date,
    classifieddate date,
    appfeepaid character varying(255) COLLATE pg_catalog."default",
    reconciled date,
    reconnotes character varying(255) COLLATE pg_catalog."default",
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT dohclassified_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.dohclassified
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.dohclassified TO PUBLIC;

GRANT SELECT ON TABLE prod.dohclassified TO anveeraprasad;

GRANT ALL ON TABLE prod.dohclassified TO cicd_pipeline;

GRANT INSERT ON TABLE prod.dohclassified TO readonly_testing;

GRANT ALL ON TABLE prod.dohclassified TO system_pipeline;