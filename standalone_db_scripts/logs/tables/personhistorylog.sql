-- Table: logs.personhistorylog

-- DROP TABLE IF EXISTS logs.personhistorylog;

CREATE TABLE IF NOT EXISTS logs.personhistorylog
(
    personid integer NOT NULL DEFAULT nextval('logs.personhistorylog_personid_seq'::regclass),
    firstname character varying(30) COLLATE pg_catalog."default",
    lastname character varying(30) COLLATE pg_catalog."default",
    ssn character varying(30) COLLATE pg_catalog."default",
    email character varying(255) COLLATE pg_catalog."default",
    phone character varying(30) COLLATE pg_catalog."default",
    language character varying(30) COLLATE pg_catalog."default",
    physicaladdress character varying(255) COLLATE pg_catalog."default",
    mailingaddress character varying(255) COLLATE pg_catalog."default",
    status character varying(30) COLLATE pg_catalog."default",
    exempt character varying(30) COLLATE pg_catalog."default",
    hiredate timestamp without time zone,
    type character varying(30) COLLATE pg_catalog."default",
    workercategory character varying(30) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS logs.personhistorylog
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE logs.personhistorylog TO anveeraprasad;

GRANT ALL ON TABLE logs.personhistorylog TO cicd_pipeline;

GRANT SELECT ON TABLE logs.personhistorylog TO eblythe;

GRANT SELECT ON TABLE logs.personhistorylog TO htata;

GRANT SELECT ON TABLE logs.personhistorylog TO lizawu;

GRANT SELECT ON TABLE logs.personhistorylog TO readonly_testing;

GRANT ALL ON TABLE logs.personhistorylog TO system_pipeline;