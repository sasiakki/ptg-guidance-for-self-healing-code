-- Table: prod.employer

-- DROP TABLE IF EXISTS prod.employer;

CREATE TABLE IF NOT EXISTS prod.employer
(
    employerid integer DEFAULT nextval('prod.employer_employerid_seq'::regclass),
    employername character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    type character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    address character varying(50) COLLATE pg_catalog."default" DEFAULT NULL::character varying,
    recordmodifieddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    recordcreateddate timestamp without time zone DEFAULT CURRENT_TIMESTAMP
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS prod.employer
    OWNER to cicd_pipeline;

GRANT SELECT ON TABLE prod.employer TO anveeraprasad;

GRANT ALL ON TABLE prod.employer TO cicd_pipeline;

GRANT SELECT ON TABLE prod.employer TO cukaumunna;

GRANT SELECT ON TABLE prod.employer TO eblythe;

GRANT SELECT ON TABLE prod.employer TO htata;

GRANT SELECT ON TABLE prod.employer TO lizawu;

GRANT SELECT ON TABLE prod.employer TO readonly_testing;

GRANT ALL ON TABLE prod.employer TO system_pipeline;