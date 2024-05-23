-- Table: prod.employertrust

-- DROP TABLE IF EXISTS prod.employertrust;

CREATE TABLE IF NOT EXISTS prod.employertrust
(
    trustid integer NOT NULL DEFAULT nextval('prod.employertrust_trustid_seq'::regclass),
    employerid integer,
    name character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    type character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    trust character varying COLLATE pg_catalog."default",
    sourcename character varying COLLATE pg_catalog."default",
    startdate character varying COLLATE pg_catalog."default",
    enddate character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.employertrust
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.employertrust TO anveeraprasad;

GRANT ALL ON TABLE prod.employertrust TO cicd_pipeline;

GRANT SELECT ON TABLE prod.employertrust TO cukaumunna;

GRANT SELECT ON TABLE prod.employertrust TO eblythe;

GRANT SELECT ON TABLE prod.employertrust TO htata;

GRANT SELECT ON TABLE prod.employertrust TO lizawu;

GRANT SELECT ON TABLE prod.employertrust TO readonly_testing;

GRANT ALL ON TABLE prod.employertrust TO system_pipeline;